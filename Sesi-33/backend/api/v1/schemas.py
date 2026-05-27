from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

class IngestRequest(BaseModel):
    car_name: str
    spesifikasi: str
    fitur: str
    testimoni: str

class BatchIngestRequest(BaseModel):
    documents: list
