from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
sys.path.append('..')
from models.post import Post
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from datetime import datetime

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


load_dotenv()

app = FastAPI(
    title="Post Similarity API",
    description="Find similar social media posts using vector embeddings",
    version="1.0.0"
);

# Serve frontend static files
app.mount(
    "/assets",
    StaticFiles(directory="frontend/dist/assets"),
    name="assets"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
print("loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Model loaded")

print("\n Connecting to Qdrant Cloud...")
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY'),
)

COLLECTION_NAME = 'social_posts'
print(f"Connected to collection: {COLLECTION_NAME}\n")

# Pydantic models
class PostCreate(BaseModel):
    post_id: str
    name: str
    caption: str
    media_url: str
    media_type: str = 'image'

class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    min_score: Optional[float] = 0.0

# routes crud api 

@app.get("/api")
def root():
    return {
        "message": "Post Similarity API",
        "status": "running",
        "endpoints": {
            "GET /posts": "Get all posts",
            "GET /posts/{post_id}": "Get specific post",
            "POST /posts": "Create new post",
            "POST /search": "Search similar posts by query",
            "GET /similar/{post_id}": "Find similar posts to a specific post",
            "DELETE /posts/{post_id}": "Delete a post",
            "GET /stats": "Get system statistics"
        }
    }



@app.get("/")
def serve_frontend():
    return FileResponse("frontend/dist/index.html")

@app.get("/posts")
def get_all_posts():
    
    try:
        posts = Post.get_all_posts()
        for post in posts:
            post['_id'] = str(post['_id'])
            post['created_at'] = post['created_at'].isoformat()
        
        return {
            "total": len(posts),
            "posts": posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/{post_id}")
def get_post(post_id: str):
#    get by id
    try:
        post = Post.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post['_id'] = str(post['_id'])
        post['created_at'] = post['created_at'].isoformat()
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/posts", status_code=201)
def create_post(post: PostCreate):
    # createpost 
    try:
        if not post.post_id.startswith('post_') or not post.post_id.replace('post_', '').isdigit():
            raise HTTPException(
                status_code=400, 
                detail="post_id must be in format 'post_001', 'post_002', etc."
            )
        existing = Post.get_post(post.post_id)
        if existing:
            raise HTTPException(status_code=400, detail="Post ID already exists")
        
       
        Post.create_post(
            post_id=post.post_id,
            name=post.name,
            caption=post.caption,
            media_url=post.media_url,
            media_type=post.media_type
        )
        
        # Create embedding
        text_to_embed = f"{post.name}: {post.caption}"
        embedding = model.encode(text_to_embed).tolist()
        
        # Convert post_id to integer for Qdrant
        post_id_num = int(post.post_id.replace('post_', ''))
        
        # Store in Qdrant
        from qdrant_client.models import PointStruct
        
        point = PointStruct(
            id=post_id_num,
            vector=embedding,
            payload={
                'post_id': post.post_id,
                'name': post.name,
                'caption': post.caption,
                'media_url': post.media_url,
                'media_type': post.media_type,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )
        
        return {
            "message": "Post created successfully",
            "post_id": post.post_id,
            "qdrant_id": post_id_num
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
def search_similar_posts(query: SearchQuery):
    """Find similar posts based on text query"""
    try:
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
# Create embedding for query
        query_embedding = model.encode(query.query).tolist()
        
        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=query.limit,
            score_threshold=query.min_score
        )
        
        results = []
        for result in search_results:
            results.append({
                'post_id': result.payload['post_id'],
                'name': result.payload['name'],
                'caption': result.payload['caption'],
                'media_url': result.payload['media_url'],
                'media_type': result.payload['media_type'],
                'similarity_score': round(result.score, 4),
                'similarity_percentage': f"{round(result.score * 100, 2)}%"
            })
        
        return {
            "query": query.query,
            "total_results": len(results),
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similar/{post_id}")
def find_similar_to_post(post_id: str, limit: int = 5, min_score: float = 0.0):
    try:
        # Validate post_id format
        if not post_id.startswith('post_') or not post_id.replace('post_', '').isdigit():
            raise HTTPException(
                status_code=400,
                detail="post_id must be in format 'post_001', 'post_002', etc."
            )
        
        # Convert string post_id to integer for Qdrant
        post_id_num = int(post_id.replace('post_', ''))
        
        # Get the postsvector from Qdrant
        post_data = qdrant_client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[post_id_num],
            with_vectors=True
        )
        
        if not post_data:
            raise HTTPException(status_code=404, detail="Post not found in vector database")
        
        post_vector = post_data[0].vector
        original_post = post_data[0].payload
        
        # Search for similar posts
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=post_vector,
            limit=limit + 1, 
            score_threshold=min_score
        )
        
        # Filter out the original post and format results
        results = []
        for result in search_results:
            if result.payload['post_id'] != post_id:
                results.append({
                    'post_id': result.payload['post_id'],
                    'name': result.payload['name'],
                    'caption': result.payload['caption'],
                    'media_url': result.payload['media_url'],
                    'media_type': result.payload['media_type'],
                    'similarity_score': round(result.score, 4),
                    'similarity_percentage': f"{round(result.score * 100, 2)}%"
                })
        
        return {
            "original_post": {
                "post_id": original_post['post_id'],
                "name": original_post['name'],
                "caption": original_post['caption']
            },
            "total_results": len(results[:limit]),
            "results": results[:limit]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/posts/{post_id}")
def delete_post(post_id: str):
    """Delete a post from both MongoDB and Qdrant"""
    try:
       
        if not post_id.startswith('post_') or not post_id.replace('post_', '').isdigit():
            raise HTTPException(
                status_code=400,
                detail="post_id must be in format 'post_001', 'post_002', etc."
            )
        
      
        post = Post.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        Post.delete_post(post_id)
        
        # Convert to integer for Qdrant
        post_id_num = int(post_id.replace('post_', ''))
        
        # Delete from Qdrant
        qdrant_client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=[post_id_num]
        )
        
        return {
            "message": "Post deleted successfully",
            "post_id": post_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_stats():
    """Get system statistics"""
    try:
        total_posts = len(Post.get_all_posts())

        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        
        return {
            "mongodb": {
                "total_posts": total_posts,
                "database": "social_media_db",
                "collection": "posts"
            },
            "qdrant": {
                "collection_name": COLLECTION_NAME,
                "total_vectors": collection_info.points_count,
                "vector_dimension": collection_info.config.params.vectors.size,
                "distance_metric": str(collection_info.config.params.vectors.distance)
            },
            "model": {
                "name": "all-MiniLM-L6-v2",
                "dimensions": 384
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        Post.get_all_posts()
        mongodb_status = "healthy"
    except:
        mongodb_status = "unhealthy"
    
    try:
        # Qdrant 
        qdrant_client.get_collection(COLLECTION_NAME)
        qdrant_status = "healthy"
    except:
        qdrant_status = "unhealthy"
    
    overall_status = "healthy" if mongodb_status == "healthy" and qdrant_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "services": {
            "mongodb": mongodb_status,
            "qdrant": qdrant_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print(" Starting Post Similarity API")
    print("="*60)
    print(f" Server: http://localhost:8000")
    print(f" Docs: http://localhost:8000/docs")
    print(f" Stats: http://localhost:8000/stats")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=7860)