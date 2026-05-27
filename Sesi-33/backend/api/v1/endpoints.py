from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.v1.schemas import ChatRequest, IngestRequest, BatchIngestRequest
from services.rag_service import rag_service
from services.ingestion_service import ingestion_service

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        async def generate():
            async for chunk in rag_service.generate_recommendation_stream(
                request.message, 
                request.conversation_history
            ):
                yield chunk
        
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest")
async def ingest_document(request: IngestRequest):
    try:
        result = ingestion_service.ingest_document(
            car_name=request.car_name,
            spesifikasi=request.spesifikasi,
            fitur=request.fitur,
            testimoni=request.testimoni
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/batch")
async def ingest_batch(request: BatchIngestRequest):
    try:
        result = ingestion_service.ingest_batch(request.documents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/init")
async def init_index():
    try:
        ingestion_service.create_index_if_not_exists()
        return {"message": "Index initialization complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
