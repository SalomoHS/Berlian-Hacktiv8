from typing import List, Dict, Any
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec

from core.clients import pc
from core.config import config

class IngestionService:
    def __init__(self):
        self.pc = pc
        self.index_name = config.INDEX_NAME
    
    def create_index_if_not_exists(self):
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=768,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
            print(f"Index '{self.index_name}' created successfully")
        else:
            print(f"Index '{self.index_name}' already exists")

    def get_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model="models/gemini-embedding-2",
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def ingest_document(self, car_name: str, spesifikasi: str, fitur: str, testimoni: str) -> Dict[str, Any]:
        try:
            combined_text = f"{car_name} {spesifikasi} {fitur} {testimoni}"
            embedding = self.get_embedding(combined_text)
            
            if not embedding:
                return {"success": False, "error": "Failed to generate embedding"}
            
            doc_id = car_name.lower().replace(" ", "-")
            
            index = self.pc.Index(self.index_name)
            index.upsert(
                vectors=[{
                    "id": doc_id,
                    "values": embedding,
                    "metadata": {
                        "car_name": car_name,
                        "spesifikasi_teknis": spesifikasi,
                        "fitur": fitur,
                        "testimoni": testimoni
                    }
                }]
            )
            
            return {"success": True, "doc_id": doc_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def ingest_batch(self, documents: List[Dict[str, str]]) -> Dict[str, Any]:
        vectors_to_upsert = []
        
        for doc in documents:
            combined_text = f"{doc.get('car_name', '')} {doc.get('spesifikasi', '')} {doc.get('fitur', '')} {doc.get('testimoni', '')}"
            embedding = self.get_embedding(combined_text)
            
            if embedding:
                doc_id = doc.get('car_name', '').lower().replace(" ", "-")
                vectors_to_upsert.append({
                    "id": doc_id,
                    "values": embedding,
                    "metadata": {
                        "car_name": doc.get('car_name', ''),
                        "spesifikasi_teknis": doc.get('spesifikasi', ''),
                        "fitur": doc.get('fitur', ''),
                        "testimoni": doc.get('testimoni', '')
                    }
                })
        
        if vectors_to_upsert:
            index = self.pc.Index(self.index_name)
            index.upsert(vectors=vectors_to_upsert)
            return {"success": True, "count": len(vectors_to_upsert)}
        
        return {"success": False, "error": "No valid documents to ingest"}

ingestion_service = IngestionService()
