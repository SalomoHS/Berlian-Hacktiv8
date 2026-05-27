import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    INDEX_NAME: str = os.getenv("INDEX_NAME", "car-brochures-index")
    
    MODEL_ENDPOINT: str = os.getenv("MODEL_ENDPOINT", "http://localhost:20128/v1")
    MODEL_API_KEY: str = os.getenv("MODEL_API_KEY", "sk-d89117e5f05a4ffa-djnjno-ecc582ac")
    MODEL_ID: str = os.getenv("MODEL_ID", "gemini-2.5-flash")
    
    CLASSIFIER_ENDPOINT: str = os.getenv("CLASSIFIER_ENDPOINT", "http://localhost:20128/v1")
    CLASSIFIER_API_KEY: str = os.getenv("CLASSIFIER_API_KEY", "sk-d89117e5f05a4ffa-djnjno-ecc582ac")
    CLASSIFIER_MODEL_ID: str = os.getenv("CLASSIFIER_MODEL_ID", "nvidia/Llama-3.1-Nemotron-Nano-8B-v1")
    
    DENSE_WEIGHT: float = 0.6
    SPARSE_WEIGHT: float = 0.4
    TOP_K_DENSE: int = 5
    TOP_K_FINAL: int = 3

config = Config()