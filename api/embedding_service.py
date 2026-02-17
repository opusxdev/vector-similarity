from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from typing import List
import uvicorn

app = FastAPI(
    title="Embedding Service",
    description="Microservice for generating text embeddings",
    version="1.0.0"
)

# Load model at startup
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("model loaded successfully")

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: List[float]
    dimension: int

@app.post("/embed", response_model=EmbedResponse)
def generate_embedding(request: EmbedRequest):
    """Generate embedding for given text"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        embedding = model.encode(request.text).tolist()
        
        return EmbedResponse(
            embedding=embedding,
            dimension=len(embedding)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "all-MiniLM-L6-v2",
        "dimension": 384
    }

@app.get("/")
def root():
    return {
        "service": "Embedding Service",
        "model": "all-MiniLM-L6-v2",
        "endpoints": {
            "POST /embed": "Generate embedding for text",
            "GET /health": "Health check"
        }
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" Starting Embedding Service")
    print("="*60)
    print(" Server: http://localhost:8001")
    print(" Health: http://localhost:8001/health")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)







