from typing import List, Dict, Any, AsyncGenerator
import google.generativeai as genai
import numpy as np

from core.clients import index, genai, llm
from core.config import config
from services.bm25_service import BM25Service
from services.fusion_service import reciprocal_rank_fusion
from services.classifier_service import classifier_service

SYSTEM_PROMPT = """
### Persona
You are Tony, an AI automotive sales specialist.

### Task
- Your task is specializing in providing car recommendations to users. 
- Your expertise spans across various vehicle types, technical specifications, features, and real user experiences, allowing you to deliver accurate, personalized advice tailored to user needs.

### Rules
- If user greet, respond with a friendly greeting.
- You must use the information provided in the context to answer the user's question.
- If the context does not contain relevant information, inform the user that you do not have that information.
- Provide informative, kind, and structured answers.
- No Greetings or introduction, just answer the user's question.
- Place the main answer on the first sentence.
- Use bold formatting for car name in the first sentence.

if {needs_car_context} == True:
    ### Output 
    - Response in Bahasa Indonesia
    - Present top 2 recommended cars as clear sections, each with:
    - Car model name as a heading
    - Key specifications (engine, fuel efficiency, dimensions) that align with user needs
    - Standout features that match their priorities (e.g., safety features, infotainment)
    - Relevant user testimonial snippets that support real-world performance
    - End with a concise summary comparing the top options and a clear recommendation for their specific use case
    - Keep the tone conversational and supportive, avoiding overly technical jargon
    - Limit the full response to 500 words or less for readability
if {needs_car_context} == False:
    - Response in Bahasa Indonesia
    - Answer the user's question directly.
"""

HUMAN_PROMPT = """
Konteks Informasi Mobil:
{context}

Riwayat Percakapan:
{conversation_history}

Pertanyaan Pengguna: 
{question}

Berdasarkan konteks di atas, berikan rekomendasi mobil yang paling sesuai untuk pengguna dan jelaskan alasannya (sebutkan spesifikasi atau fitur yang mendukung).
"""

class RAGService:
    def __init__(self):
        self.bm25_service = BM25Service()
    
    def get_gemini_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-2",
                content=text,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def hybrid_search(self, user_query: str) -> List[Dict[str, Any]]:
        query_vector = self.get_gemini_embedding(user_query)
        if not query_vector:
            return []

        search_results = index.query(
            vector=query_vector,
            top_k=config.TOP_K_DENSE,
            include_metadata=True,
        )
        matches = search_results.get("matches", [])
        if not matches:
            return []

        dense_scores = np.array([m.get("score", 0.0) for m in matches])

        self.bm25_service.build(matches)
        sparse_scores = self.bm25_service.get_scores(user_query)

        fused_scores = reciprocal_rank_fusion(dense_scores, sparse_scores)

        ranked_indices = np.argsort(-fused_scores)[:config.TOP_K_FINAL]
        reranked_matches = [matches[i] for i in ranked_indices]

        print(f"\n  [Hybrid Search] Candidates: {len(matches)} | "
              f"Fused top-{config.TOP_K_FINAL}: {ranked_indices.tolist()}")

        return reranked_matches

    def build_context(self, matches: List[Dict[str, Any]]) -> str:
        context_list = []
        for match in matches:
            meta = match.get("metadata", {})
            car_name = meta.get("car_name", "Tidak diketahui")
            spesifikasi = meta.get("spesifikasi_teknis", "Tidak ada data")
            fitur = meta.get("fitur", "Tidak ada data")
            testimoni = meta.get("testimoni", "Tidak ada data")

            car_info = (
                f"Mobil: {car_name}\n"
                f"Spesifikasi Teknis: {spesifikasi}\n"
                f"Fitur: {fitur}\n"
                f"Testimoni: {testimoni}"
            )
            context_list.append(car_info)

        return "\n\n---\n\n".join(context_list)

    def _format_conversation_history(self, history: List[Dict[str, str]]) -> str:
        if not history:
            return "Tidak ada riwayat percakapan sebelumnya."
        
        formatted = []
        for msg in history:
            role = "Pengguna" if msg.get("role") == "user" else "Tony"
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        
        return "\n\n".join(formatted)

    def generate_recommendation(self, user_query: str, conversation_history: List[Dict[str, str]] = None) -> str:
        if conversation_history is None:
            conversation_history = []
        
        print(f"\nMemproses pertanyaan: '{user_query}'...")
        if conversation_history:
            print(f"  Dengan {len(conversation_history)} pesan riwayat...")

        needs_car_context = classifier_service.classify_query(user_query)
        print(f"  Klasifikasi konteks mobil: {needs_car_context}")

        reranked_matches = self.hybrid_search(user_query)
        context_text = self.build_context(reranked_matches) if reranked_matches else ""
        history_text = self._format_conversation_history(conversation_history)

        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            if needs_car_context:
                human_prompt = HUMAN_PROMPT
            else:
                human_prompt = """
Riwayat Percakapan:
{conversation_history}

Pertanyaan Pengguna: 
{question}

Berikan jawaban yang sesuai untuk pertanyaan pengguna ini.
"""
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", human_prompt)
            ])

            chain = prompt_template | llm | StrOutputParser()
            
            final_answer = chain.invoke({
                "context": context_text,
                "conversation_history": history_text,
                "question": user_query,
            })
            return final_answer
        except Exception as e:
            error_msg = f"Error saat generate dengan LangChain: {e}"
            print(error_msg)
            return error_msg

    async def generate_recommendation_stream(self, user_query: str, conversation_history: List[Dict[str, str]] = None) -> AsyncGenerator[str, None]:
        if conversation_history is None:
            conversation_history = []
        
        print(f"\nMemproses pertanyaan: '{user_query}'...")
        if conversation_history:
            print(f"  Dengan {len(conversation_history)} pesan riwayat...")

        needs_car_context = classifier_service.classify_query(user_query)
        print(f"  Klasifikasi konteks mobil: {needs_car_context}")

        history_text = self._format_conversation_history(conversation_history)

        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            if needs_car_context:
                reranked_matches = self.hybrid_search(user_query)
                context_text = self.build_context(reranked_matches) if reranked_matches else ""
                
                human_prompt = HUMAN_PROMPT
            else:
                human_prompt = """
Riwayat Percakapan:
{conversation_history}

Pertanyaan Pengguna: 
{question}

Berikan jawaban yang sesuai untuk pertanyaan pengguna ini.
"""
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", human_prompt)
            ])

            chain = prompt_template | llm | StrOutputParser()
            
            if needs_car_context:

                async for chunk in chain.astream({
                    "needs_car_context": needs_car_context,
                    "context": context_text,
                    "conversation_history": history_text,
                    "question": user_query,
                }):
                    yield chunk
            else:
                async for chunk in chain.astream({
                    "needs_car_context": needs_car_context,
                    "conversation_history": history_text,
                    "question": user_query,
                }):
                    yield chunk
        except Exception as e:
            error_msg = f"Error saat generate dengan LangChain: {e}"
            print(error_msg)
            yield error_msg

rag_service = RAGService()
