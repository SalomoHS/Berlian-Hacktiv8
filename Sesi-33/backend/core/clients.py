from langchain_openai import ChatOpenAI
from pinecone import Pinecone
import google.generativeai as genai

from core.config import config

pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index(config.INDEX_NAME)

genai.configure(api_key=config.GEMINI_API_KEY)

# llm = ChatGoogleGenerativeAI(
#     model=config.MODEL_ID,
#     temperature=0.7,
#     google_api_key=config.GEMINI_API_KEY,
#     streaming=True,
# )

llm = ChatOpenAI(
    model_name=config.MODEL_ID,
    temperature=0.7,
    api_key=config.MODEL_API_KEY,
    base_url=config.MODEL_ENDPOINT,
    streaming=True,
)

classifier_llm = ChatOpenAI(
    model_name=config.CLASSIFIER_MODEL_ID,
    temperature=0.0,
    api_key=config.CLASSIFIER_API_KEY,
    base_url=config.CLASSIFIER_ENDPOINT,
)