# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional, List
# import sys
# sys.path.append('..')
# from models.post import Post
# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# import os
# from dotenv import load_dotenv
# import requests

# from datetime import datetime

# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse


# load_dotenv()

# app = FastAPI(
#     title="Post Similarity API",
#     description="Find similar social media posts using vector embeddings",
#     version="1.0.0"
# );

# # # Serve frontend static files                  PROD COMMENTED
# # app.mount(
# #     "/assets",
# #     StaticFiles(directory="frontend/dist/assets"),
# #     name="assets"
# # )
# import os
# from fastapi.staticfiles import StaticFiles

# ASSETS_PATH = "frontend/dist/assets"

# if os.path.exists(ASSETS_PATH):
#     app.mount(
#         "/assets",
#         StaticFiles(directory=ASSETS_PATH),
#         name="assets"
#     )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize
# print("loading embedding model...")
# model = SentenceTransformer('all-MiniLM-L6-v2')
# print("Model loaded")

# print("\n Connecting to Qdrant Cloud...")
# qdrant_client = QdrantClient(
#     url=os.getenv('QDRANT_URL'),
#     api_key=os.getenv('QDRANT_API_KEY'),
# )

# COLLECTION_NAME = 'social_posts'
# print(f"Connected to collection: {COLLECTION_NAME}\n")
# RAG_PROMPT_TEMPLATE = """
# You are a factual assistant.

# Answer the question using ONLY the context below.
# If the answer cannot be found in the context, say:
# "I don't know based on the provided posts."

# Context:
# {context}

# Question:
# {question}

# Answer:
# """
# HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
# HF_API_KEY = os.getenv("HF_API_KEY")

# def generate_llm_answer(prompt: str) -> str:
#     headers = {
#         "Authorization": f"Bearer {HF_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "inputs": prompt,
#         "parameters": {
#             "max_new_tokens": 200,
#             "temperature": 0.0
#         }
#     }

#     response = requests.post(
#         HF_API_URL,
#         headers=headers,
#         json=payload,
#         timeout=30
#     )

#     if response.status_code != 200:
#         raise Exception("LLM generation failed")

#     return response.json()[0]["generated_text"].strip()

# # Pydantic models
# class PostCreate(BaseModel):
#     post_id: str
#     name: str
#     caption: str
#     media_url: str
#     media_type: str = 'image'

# class SearchQuery(BaseModel):
#     query: str
#     limit: int = 10
#     min_score: Optional[float] = 0.0
# class RAGQuery(BaseModel):
#     question: str
#     limit: int = 5
#     min_score: float = 0.2


# class RAGResponse(BaseModel):
#     answer: str
#     sources: List[dict]

# # routes crud api 

# @app.get("/api")
# def root():
#     return {
#         "message": "Post Similarity API",
#         "status": "running",
#         "endpoints": {
#             "GET /posts": "Get all posts",
#             "GET /posts/{post_id}": "Get specific post",
#             "POST /posts": "Create new post",
#             "POST /search": "Search similar posts by query",
#             "GET /similar/{post_id}": "Find similar posts to a specific post",
#             "DELETE /posts/{post_id}": "Delete a post",
#             "GET /stats": "Get system statistics"
#         }
#     }



# @app.get("/")
# def serve_frontend():
#     return FileResponse("frontend/dist/index.html")

# @app.get("/posts")
# def get_all_posts():
    
#     try:
#         posts = Post.get_all_posts()
#         for post in posts:
#             post['_id'] = str(post['_id'])
#             post['created_at'] = post['created_at'].isoformat()
        
#         return {
#             "total": len(posts),
#             "posts": posts
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/posts/{post_id}")
# def get_post(post_id: str):
# #    get by id
#     try:
#         post = Post.get_post(post_id)
        
#         if not post:
#             raise HTTPException(status_code=404, detail="Post not found")
        
#         post['_id'] = str(post['_id'])
#         post['created_at'] = post['created_at'].isoformat()
#         return post
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/posts", status_code=201)
# def create_post(post: PostCreate):
#     # createpost 
#     try:
#         if not post.post_id.startswith('post_') or not post.post_id.replace('post_', '').isdigit():
#             raise HTTPException(
#                 status_code=400, 
#                 detail="post_id must be in format 'post_001', 'post_002', etc."
#             )
#         existing = Post.get_post(post.post_id)
#         if existing:
#             raise HTTPException(status_code=400, detail="Post ID already exists")
        
       
#         Post.create_post(
#             post_id=post.post_id,
#             name=post.name,
#             caption=post.caption,
#             media_url=post.media_url,
#             media_type=post.media_type
#         )
        
#         # Create embedding
#         text_to_embed = f"{post.name}: {post.caption}"
#         embedding = model.encode(text_to_embed).tolist()
        
#         # Convert post_id to integer for Qdrant
#         post_id_num = int(post.post_id.replace('post_', ''))
        
#         # Store in Qdrant
#         from qdrant_client.models import PointStruct
        
#         point = PointStruct(
#             id=post_id_num,
#             vector=embedding,
#             payload={
#                 'post_id': post.post_id,
#                 'name': post.name,
#                 'caption': post.caption,
#                 'media_url': post.media_url,
#                 'media_type': post.media_type,
#                 'created_at': datetime.utcnow().isoformat()
#             }
#         )
        
#         qdrant_client.upsert(
#             collection_name=COLLECTION_NAME,
#             points=[point]
#         )
        
#         return {
#             "message": "Post created successfully",
#             "post_id": post.post_id,
#             "qdrant_id": post_id_num
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/search")
# def search_similar_posts(query: SearchQuery):
#     """Find similar posts based on text query"""
#     try:
#         if not query.query.strip():
#             raise HTTPException(status_code=400, detail="Query cannot be empty")
        
# # Create embedding for query
#         query_embedding = model.encode(query.query).tolist()
        
#         # Search in Qdrant
#         search_results = qdrant_client.search(
#             collection_name=COLLECTION_NAME,
#             query_vector=query_embedding,
#             limit=query.limit,
#             score_threshold=query.min_score
#         )
        
#         results = []
#         for result in search_results:
#             results.append({
#                 'post_id': result.payload['post_id'],
#                 'name': result.payload['name'],
#                 'caption': result.payload['caption'],
#                 'media_url': result.payload['media_url'],
#                 'media_type': result.payload['media_type'],
#                 'similarity_score': round(result.score, 4),
#                 'similarity_percentage': f"{round(result.score * 100, 2)}%"
#             })
        
#         return {
#             "query": query.query,
#             "total_results": len(results),
#             "results": results
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/similar/{post_id}")
# def find_similar_to_post(post_id: str, limit: int = 5, min_score: float = 0.0):
#     try:
#         # Validate post_id format
#         if not post_id.startswith('post_') or not post_id.replace('post_', '').isdigit():
#             raise HTTPException(
#                 status_code=400,
#                 detail="post_id must be in format 'post_001', 'post_002', etc."
#             )
        
#         # Convert string post_id to integer for Qdrant
#         post_id_num = int(post_id.replace('post_', ''))
        
#         # Get the postsvector from Qdrant
#         post_data = qdrant_client.retrieve(
#             collection_name=COLLECTION_NAME,
#             ids=[post_id_num],
#             with_vectors=True
#         )
        
#         if not post_data:
#             raise HTTPException(status_code=404, detail="Post not found in vector database")
        
#         post_vector = post_data[0].vector
#         original_post = post_data[0].payload
        
#         # Search for similar posts
#         search_results = qdrant_client.search(
#             collection_name=COLLECTION_NAME,
#             query_vector=post_vector,
#             limit=limit + 1, 
#             score_threshold=min_score
#         )
        
#         # Filter out the original post and format results
#         results = []
#         for result in search_results:
#             if result.payload['post_id'] != post_id:
#                 results.append({
#                     'post_id': result.payload['post_id'],
#                     'name': result.payload['name'],
#                     'caption': result.payload['caption'],
#                     'media_url': result.payload['media_url'],
#                     'media_type': result.payload['media_type'],
#                     'similarity_score': round(result.score, 4),
#                     'similarity_percentage': f"{round(result.score * 100, 2)}%"
#                 })
        
#         return {
#             "original_post": {
#                 "post_id": original_post['post_id'],
#                 "name": original_post['name'],
#                 "caption": original_post['caption']
#             },
#             "total_results": len(results[:limit]),
#             "results": results[:limit]
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.delete("/posts/{post_id}")
# def delete_post(post_id: str):
#     """Delete a post from both MongoDB and Qdrant"""
#     try:
       
#         if not post_id.startswith('post_') or not post_id.replace('post_', '').isdigit():
#             raise HTTPException(
#                 status_code=400,
#                 detail="post_id must be in format 'post_001', 'post_002', etc."
#             )
        
      
#         post = Post.get_post(post_id)
#         if not post:
#             raise HTTPException(status_code=404, detail="Post not found")
        
#         Post.delete_post(post_id)
        
#         # Convert to integer for Qdrant
#         post_id_num = int(post_id.replace('post_', ''))
        
#         # Delete from Qdrant
#         qdrant_client.delete(
#             collection_name=COLLECTION_NAME,
#             points_selector=[post_id_num]
#         )
        
#         return {
#             "message": "Post deleted successfully",
#             "post_id": post_id
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/stats")
# def get_stats():
#     """Get system statistics"""
#     try:
#         total_posts = len(Post.get_all_posts())

#         collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        
#         return {
#             "mongodb": {
#                 "total_posts": total_posts,
#                 "database": "social_media_db",
#                 "collection": "posts"
#             },
#             "qdrant": {
#                 "collection_name": COLLECTION_NAME,
#                 "total_vectors": collection_info.points_count,
#                 "vector_dimension": collection_info.config.params.vectors.size,
#                 "distance_metric": str(collection_info.config.params.vectors.distance)
#             },
#             "model": {
#                 "name": "all-MiniLM-L6-v2",
#                 "dimensions": 384
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     try:
#         Post.get_all_posts()
#         mongodb_status = "healthy"
#     except:
#         mongodb_status = "unhealthy"
    
#     try:
#         # Qdrant 
#         qdrant_client.get_collection(COLLECTION_NAME)
#         qdrant_status = "healthy"
#     except:
#         qdrant_status = "unhealthy"
    
#     overall_status = "healthy" if mongodb_status == "healthy" and qdrant_status == "healthy" else "unhealthy"
    
#     return {
#         "status": overall_status,
#         "services": {
#             "mongodb": mongodb_status,
#             "qdrant": qdrant_status
#         }
#     }


# @app.post("/rag", response_model=RAGResponse)
# def rag_answer(query: RAGQuery):

#     if not query.question.strip():
#         raise HTTPException(status_code=400, detail="Question cannot be empty")

#     # 1. Embed question
#     question_embedding = model.encode(query.question).tolist()

#     # 2. Retrieve relevant posts
#     search_results = qdrant_client.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=question_embedding,
#         limit=query.limit,
#         score_threshold=query.min_score
#     )

#     if not search_results:
#         return {
#             "answer": "I don't know based on the provided posts.",
#             "sources": []
#         }

#     # 3. Build context
#     context_blocks = []
#     sources = []

#     for i, result in enumerate(search_results, 1):
#         context_blocks.append(
#             f"[Post {i}] {result.payload['name']}: {result.payload['caption']}"
#         )

#         sources.append({
#             "post_id": result.payload["post_id"],
#             "name": result.payload["name"],
#             "caption": result.payload["caption"],
#             "similarity_score": round(result.score, 4)
#         })

#     context_text = "\n".join(context_blocks)

#     # 4. Prompt
#     prompt = RAG_PROMPT_TEMPLATE.format(
#         context=context_text,
#         question=query.question
#     )

#     # 5. Generate answer
#     try:
#         answer = generate_llm_answer(prompt)
#     except Exception:
#         raise HTTPException(status_code=500, detail="LLM failed to generate answer")

#     return {
#         "answer": answer,
#         "sources": sources
#     }



# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "="*60)
#     print(" Starting Post Similarity API")
#     print("="*60)
#     print(f" Server: http://localhost:8000")
#     print(f" Docs: http://localhost:8000/docs")
#     print(f" Stats: http://localhost:8000/stats")
#     print("="*60 + "\n")
    
#     uvicorn.run(app, host="0.0.0.0", port=7860)








# # dev 
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional, List
# import sys
# sys.path.append('..')

# from models.post import Post
# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# import os
# from dotenv import load_dotenv
# from datetime import datetime

# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse

# load_dotenv()

# app = FastAPI(
#     title="Post Similarity API",
#     description="Find similar social media posts using vector embeddings",
#     version="1.0.0"
# )

# # ---------- STATIC FRONTEND ----------
# ASSETS_PATH = "frontend/dist/assets"
# if os.path.exists(ASSETS_PATH):
#     app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="assets")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------- EMBEDDING MODEL ----------
# print("Loading embedding model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")
# print("Embedding model loaded")

# # ---------- QDRANT ----------
# print("Connecting to Qdrant...")
# qdrant_client = QdrantClient(
#     url=os.getenv("QDRANT_URL"),
#     api_key=os.getenv("QDRANT_API_KEY"),
# )

# COLLECTION_NAME = "social_posts"
# print(f"Connected to collection: {COLLECTION_NAME}")

# # ---------- RAG CONFIG ----------
# RAG_PROMPT_TEMPLATE = """
# You are a question-answering system.

# Rules:
# - Answer in plain English.
# - Do NOT mention post numbers.
# - Do NOT say "Post 1", "Post 2", or similar.
# - Do NOT repeat the context.
# - If the answer is not clearly present, say:
#   "I don't know based on the provided posts."

# Context:
# {context}

# Question:
# {question}

# Final Answer (one short paragraph):
# """


# HF_API_KEY = os.getenv("HF_API_KEY")
# if not HF_API_KEY:
#     raise RuntimeError("HF_API_KEY is missing in environment variables")

# HF_MODEL = "google/flan-t5-small"
# HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# from transformers import pipeline

# print("Loading local LLM...")
# llm = pipeline(
#     "text2text-generation",
#     model="google/flan-t5-small",
#     max_new_tokens=200
# )
# print("Local LLM loaded")

# def generate_llm_answer(prompt: str) -> str:
#     result = llm(prompt)
#     return result[0]["generated_text"].strip()
# def clean_answer(text: str) -> str:
#     blacklist = ["[Post", "Post 1", "Post 2", "Post 3"]
#     for token in blacklist:
#         text = text.replace(token, "")
#     return text.strip()


# # ---------- SCHEMAS ----------
# class PostCreate(BaseModel):
#     post_id: str
#     name: str
#     caption: str
#     media_url: str
#     media_type: str = "image"

# class SearchQuery(BaseModel):
#     query: str
#     limit: int = 10
#     min_score: Optional[float] = 0.0

# class RAGQuery(BaseModel):
#     question: str
#     limit: int = 5
#     min_score: float = 0.2

# class RAGResponse(BaseModel):
#     answer: str
#     sources: List[dict]

# # ---------- ROUTES ----------
# @app.get("/")
# def serve_frontend():
#     return FileResponse("frontend/dist/index.html")

# @app.post("/search")
# def search_similar_posts(query: SearchQuery):
#     embedding = model.encode(query.query).tolist()
#     results = qdrant_client.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=embedding,
#         limit=query.limit,
#         score_threshold=query.min_score,
#     )

#     return {
#         "results": [
#             {
#                 "post_id": r.payload["post_id"],
#                 "name": r.payload["name"],
#                 "caption": r.payload["caption"],
#                 "media_url": r.payload["media_url"],
#                 "media_type": r.payload["media_type"],
#                 "similarity_score": round(r.score, 4),
#             }
#             for r in results
#         ]
#     }

# @app.post("/rag", response_model=RAGResponse)
# def rag_answer(query: RAGQuery):
#     question_embedding = model.encode(query.question).tolist()

#     search_results = qdrant_client.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=question_embedding,
#         limit=query.limit,
#         score_threshold=query.min_score,
#     )

#     if not search_results:
#         return {
#             "answer": "I don't know based on the provided posts.",
#             "sources": [],
#         }

#     context = []
#     sources = []

#     for i, r in enumerate(search_results, 1):
#         context.append(f"[Post {i}] {r.payload['name']}: {r.payload['caption']}")
#         sources.append({
#             "post_id": r.payload["post_id"],
#             "name": r.payload["name"],
#             "caption": r.payload["caption"],
#             "similarity_score": round(r.score, 4),
#         })

#     prompt = RAG_PROMPT_TEMPLATE.format(
#         context="\n".join(context),
#         question=query.question,
#     )

#     try:
#         raw_answer = generate_llm_answer(prompt)
#         answer = clean_answer(raw_answer)

#     except Exception:
#         raise HTTPException(status_code=500, detail="LLM failed to generate answer")

#     return {
#         "answer": answer,
#         "sources": sources,
#     }

# # ---------- MAIN ----------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)









#dev 2 
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from pydantic import BaseModel
# from typing import Optional, List
# import os
# from dotenv import load_dotenv
# from datetime import datetime
# import sys

# sys.path.append("..")

# from models.post import Post
# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# from transformers import pipeline

# # --------------------------------------------------
# # INIT
# # --------------------------------------------------
# load_dotenv()

# app = FastAPI(
#     title="Post Similarity + RAG API",
#     description="Vector similarity search with local RAG",
#     version="1.0.0",
# )

# # --------------------------------------------------
# # STATIC FRONTEND
# # --------------------------------------------------
# ASSETS_PATH = "frontend/dist/assets"
# if os.path.exists(ASSETS_PATH):
#     app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="assets")

# @app.get("/")
# def serve_frontend():
#     return FileResponse("frontend/dist/index.html")

# # --------------------------------------------------
# # CORS
# # --------------------------------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --------------------------------------------------
# # EMBEDDING MODEL
# # --------------------------------------------------
# print("Loading embedding model...")
# embedder = SentenceTransformer("all-MiniLM-L6-v2")
# print("Embedding model loaded")

# # --------------------------------------------------
# # LOCAL LLM (FLAN)
# # --------------------------------------------------
# print("Loading local LLM (FLAN)...")
# # llm = pipeline(
# #     "text2text-generation",
# #     model="google/flan-t5-small",
# #     max_new_tokens=200,
# # )
# llm = pipeline(
#     "text2text-generation",
#     model="google/flan-t5-base",
#     max_new_tokens=256,
#     temperature=0.2,
#     do_sample= False
# )

# print("Local LLM loaded")

# def generate_llm_answer(prompt: str) -> str:
#     result = llm(prompt)
#     return result[0]["generated_text"].strip()

# def clean_answer(text: str) -> str:
#     # Remove hashtags
#     words = [w for w in text.split() if not w.startswith("#")]
#     text = " ".join(words)

#     # Cut off if model starts listing content
#     for stop in ["Context:", "Sources:", "Post", ":"]:
#         if stop in text:
#             text = text.split(stop)[0]

#     # Limit length (force summarization)
#     return text.strip()[:300]

# # --------------------------------------------------
# # QDRANT
# # --------------------------------------------------
# qdrant = QdrantClient(
#     url=os.getenv("QDRANT_URL"),
#     api_key=os.getenv("QDRANT_API_KEY"),
# )

# COLLECTION_NAME = "social_posts"

# # --------------------------------------------------
# # RAG PROMPT (FIXED)
# # --------------------------------------------------
# RAG_PROMPT_TEMPLATE = """
# You are an assistant answering questions using social media posts.

# Instructions:
# - Answer in ONE or TWO sentences only.
# - Summarize the information.
# - Do NOT copy captions.
# - Do NOT include hashtags.
# - Do NOT list multiple posts.
# - Do NOT mention names unless needed.
# - If the answer is unclear, say:
#   "I don't know based on the provided posts."

# Context:
# {context}

# Question:
# {question}

# Answer:
# """

# # --------------------------------------------------
# # SCHEMAS
# # --------------------------------------------------
# class SearchQuery(BaseModel):
#     query: str
#     limit: int = 10
#     min_score: Optional[float] = 0.0

# class RAGQuery(BaseModel):
#     question: str
#     limit: int = 5
#     min_score: float = 0.2

# class RAGResponse(BaseModel):
#     answer: str
#     sources: List[dict]

# # --------------------------------------------------
# # SEARCH
# # --------------------------------------------------
# @app.post("/search")
# def search_similar_posts(query: SearchQuery):
#     if not query.query.strip():
#         raise HTTPException(status_code=400, detail="Query cannot be empty")

#     vector = embedder.encode(query.query).tolist()

#     results = qdrant.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=vector,
#         limit=query.limit,
#         score_threshold=query.min_score,
#     )

#     return {
#         "results": [
#             {
#                 "post_id": r.payload["post_id"],
#                 "name": r.payload["name"],
#                 "caption": r.payload["caption"],
#                 "media_url": r.payload["media_url"],
#                 "media_type": r.payload["media_type"],
#                 "similarity_score": round(r.score, 4),
#             }
#             for r in results
#         ]
#     }

# # --------------------------------------------------
# # RAG
# # --------------------------------------------------
# @app.post("/rag", response_model=RAGResponse)
# def rag_answer(query: RAGQuery):
#     if not query.question.strip():
#         raise HTTPException(status_code=400, detail="Question cannot be empty")

#     question_vector = embedder.encode(query.question).tolist()

#     hits = qdrant.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=question_vector,
#         limit=query.limit,
#         score_threshold=query.min_score,
#     )

#     if not hits:
#         return {
#             "answer": "I don't know based on the provided posts.",
#             "sources": [],
#         }

#     context_blocks = []
#     sources = []

#     for i, h in enumerate(hits, 1):
#         context_blocks.append(
#             f"{h.payload['name']}: {h.payload['caption']}"
#         )
#         sources.append({
#             "post_id": h.payload["post_id"],
#             "name": h.payload["name"],
#             "caption": h.payload["caption"],
#             "similarity_score": round(h.score, 4),
#         })

#     prompt = RAG_PROMPT_TEMPLATE.format(
#         context="\n".join(context_blocks),
#         question=query.question,
#     )

#     try:
#         raw_answer = generate_llm_answer(prompt)
#         answer = clean_answer(raw_answer)
#     except Exception:
#         raise HTTPException(status_code=500, detail="LLM failed to generate answer")

#     return {
#         "answer": answer,
#         "sources": sources,
#     }

# # --------------------------------------------------
# # MAIN
# # --------------------------------------------------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)





# dev3   working rag plus vector 
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from pydantic import BaseModel
# from typing import Optional, List
# import os
# from dotenv import load_dotenv
# import sys

# sys.path.append("..")

# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# from transformers import pipeline

# # --------------------------------------------------
# # INIT
# # --------------------------------------------------
# load_dotenv()

# app = FastAPI(
#     title="Post Similarity + RAG API",
#     description="Vector similarity search with grounded local RAG",
#     version="1.1.0",
# )

# # --------------------------------------------------
# # STATIC FRONTEND
# # --------------------------------------------------
# ASSETS_PATH = "frontend/dist/assets"
# if os.path.exists(ASSETS_PATH):
#     app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="assets")

# @app.get("/")
# def serve_frontend():
#     return FileResponse("frontend/dist/index.html")

# # --------------------------------------------------
# # CORS
# # --------------------------------------------------
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --------------------------------------------------
# # EMBEDDING MODEL
# # --------------------------------------------------
# print("Loading embedding model...")
# embedder = SentenceTransformer("all-MiniLM-L6-v2")
# print("Embedding model loaded")

# # --------------------------------------------------
# # LOCAL LLM (FLAN-T5 BASE)
# # --------------------------------------------------
# print("Loading local LLM...")
# llm = pipeline(
#     "text2text-generation",
#     model="google/flan-t5-base",
#     max_new_tokens=180,
#     temperature=0.0,
#     do_sample=False,
# )
# print("Local LLM loaded")

# def generate_llm_answer(prompt: str) -> str:
#     result = llm(prompt)
#     return result[0]["generated_text"].strip()

# def clean_answer(text: str) -> str:
#     text = text.strip()

#     # hard stop on leakage
#     for stop in ["Context:", "Sources:", "Post", "\n"]:
#         if stop in text:
#             text = text.split(stop)[0]

#     return text[:300]

# # --------------------------------------------------
# # QDRANT
# # --------------------------------------------------
# qdrant = QdrantClient(
#     url=os.getenv("QDRANT_URL"),
#     api_key=os.getenv("QDRANT_API_KEY"),
# )

# COLLECTION_NAME = "social_posts"

# # --------------------------------------------------
# # RAG PROMPT (STRICT)
# # --------------------------------------------------
# RAG_PROMPT_TEMPLATE = """
# You are a retrieval-based assistant.

# Rules:
# - Answer ONLY using the information in the Context.
# - If the Context does not clearly answer the question, say exactly:
#   "I don't know based on the provided posts."
# - Do NOT guess.
# - Do NOT use outside knowledge.
# - Answer in ONE short sentence.

# Context:
# {context}

# Question:
# {question}

# Answer:
# """

# # --------------------------------------------------
# # SCHEMAS
# # --------------------------------------------------
# # class SearchQuery(BaseModel):
# #     query: str
# #     limit: int = 10
# #     min_score: Optional[float] = 0.3


# # vector fix
# class SearchQuery(BaseModel):
#     query: str
#     limit: int = 5  # HARD DEFAULT

# class RAGQuery(BaseModel):
#     question: str
#     limit: int = 5
#     min_score: float = 0.5

# class RAGResponse(BaseModel):
#     answer: str
#     sources: List[dict]

# # --------------------------------------------------
# # SEARCH ENDPOINT
# # --------------------------------------------------
# # @app.post("/search")
# # def search_similar_posts(query: SearchQuery):
# #     if not query.query.strip():
# #         raise HTTPException(status_code=400, detail="Query cannot be empty")

# #     vector = embedder.encode(query.query).tolist()

# #     results = qdrant.search(
# #         collection_name=COLLECTION_NAME,
# #         query_vector=vector,
# #         limit=query.limit,
# #         score_threshold=query.min_score,
# #     )

# #     return {
# #         "results": [
# #             {
# #                 "post_id": r.payload["post_id"],
# #                 "name": r.payload["name"],
# #                 "caption": r.payload["caption"],
# #                 "media_url": r.payload["media_url"],
# #                 "media_type": r.payload["media_type"],
# #                 "similarity_score": round(r.score, 4),
# #             }
# #             for r in results
# #         ]
# #     }

# # fix vector search 
# @app.post("/search")
# def search_similar_posts(query: SearchQuery):
#     if not query.query.strip():
#         raise HTTPException(status_code=400, detail="Query cannot be empty")

#     vector = embedder.encode(query.query).tolist()

#     # 🔥 ALWAYS fetch top K — NO threshold
#     results = qdrant.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=vector,
#         limit=5,  # FORCE TOP 5
#         with_payload=True,
#     )

#     # Even if similarity is low — still return closest
#     return {
#         "results": [
#             {
#                 "post_id": r.payload.get("post_id"),
#                 "name": r.payload.get("name"),
#                 "caption": r.payload.get("caption"),
#                 "media_url": r.payload.get("media_url"),
#                 "media_type": r.payload.get("media_type"),
#                 "similarity_score": round(r.score, 4),
#             }
#             for r in results
#         ]
#     }


# # --------------------------------------------------
# # RAG ENDPOINT (FIXED)
# # --------------------------------------------------
# @app.post("/rag", response_model=RAGResponse)
# def rag_answer(query: RAGQuery):
#     if not query.question.strip():
#         raise HTTPException(status_code=400, detail="Question cannot be empty")

#     question_lower = query.question.lower()

#     # 🔒 Intent guard: dataset has NO locations
#     if "where" in question_lower:
#         return {
#             "answer": "I don't know based on the provided posts.",
#             "sources": [],
#         }

#     vector = embedder.encode(query.question).tolist()

#     hits = qdrant.search(
#         collection_name=COLLECTION_NAME,
#         query_vector=vector,
#         limit=query.limit,
#         score_threshold=query.min_score,
#     )

#     if not hits:
#         return {
#             "answer": "I don't know based on the provided posts.",
#             "sources": [],
#         }

#     context_blocks = []
#     sources = []

#     for h in hits:
#         context_blocks.append(h.payload["caption"])
#         sources.append({
#             "post_id": h.payload["post_id"],
#             "name": h.payload["name"],
#             "caption": h.payload["caption"],
#             "similarity_score": round(h.score, 4),
#         })

#     prompt = RAG_PROMPT_TEMPLATE.format(
#         context="\n".join(context_blocks),
#         question=query.question,
#     )

#     try:
#         raw_answer = generate_llm_answer(prompt)
#         answer = clean_answer(raw_answer)
#     except Exception:
#         raise HTTPException(status_code=500, detail="LLM failed to generate answer")

#     if not answer or "i don't know" not in answer.lower() and len(answer) < 3:
#         answer = "I don't know based on the provided posts."

#     return {
#         "answer": answer,
#         "sources": sources,
#     }

# # --------------------------------------------------
# # MAIN
# # --------------------------------------------------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)





# dev4 try 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import sys

sys.path.append("..")

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from transformers import pipeline

# --------------------------------------------------
# INIT
# --------------------------------------------------
load_dotenv()

app = FastAPI(
    title="Post Similarity + RAG API",
    description="Guaranteed top-K vector similarity search with grounded RAG",
    version="1.2.0",
)

# --------------------------------------------------
# STATIC FRONTEND
# --------------------------------------------------
ASSETS_PATH = "frontend/dist/assets"
if os.path.exists(ASSETS_PATH):
    app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="assets")

@app.get("/")
def serve_frontend():
    return FileResponse("frontend/dist/index.html")

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------
print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model loaded")

# --------------------------------------------------
# LLM CONFIGURATION
# --------------------------------------------------
import requests

# Choose your LLM provider: "groq", "huggingface", "openai", "mistral", or "local"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # default to Groq (FREE!)

if LLM_PROVIDER == "local":
    print("Loading local LLM (FLAN-T5)...")
    llm = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        max_new_tokens=512,
        temperature=0.5,
        do_sample=True,
        top_p=0.9,
    )
    print("Local LLM loaded")
elif LLM_PROVIDER in ["openai", "mistral", "groq", "huggingface"]:
    print(f"Using {LLM_PROVIDER.upper()} API")
    llm = None
    
    # Validate API key is set
    if LLM_PROVIDER == "groq" and not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set in .env file!")
    elif LLM_PROVIDER == "openai" and not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set in .env file!")
    elif LLM_PROVIDER == "mistral" and not os.getenv("MISTRAL_API_KEY"):
        raise ValueError("MISTRAL_API_KEY is not set in .env file!")
    elif LLM_PROVIDER == "huggingface" and not os.getenv("HF_API_KEY"):
        raise ValueError("HF_API_KEY is not set in .env file!")
else:
    raise ValueError(f"Invalid LLM_PROVIDER: {LLM_PROVIDER}")

def generate_llm_answer(prompt: str) -> str:
    if LLM_PROVIDER == "local":
        result = llm(prompt)
        return result[0]["generated_text"].strip()
    
    elif LLM_PROVIDER == "groq":
        # GROQ - FREE & SUPER FAST!
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",  # Faster model, still great quality
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that provides detailed, well-structured answers with clear reasoning."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1,
            "stream": False
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        # Debug: print response if error
        if response.status_code != 200:
            print(f"groq API Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    
   
def clean_answer(text: str) -> str:
    text = text.strip()
    # Keep full response - API models format well
    return text

# --------------------------------------------------
# QDRANT
# --------------------------------------------------
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION_NAME = "social_posts"

# --------------------------------------------------
# RAG PROMPT
# --------------------------------------------------
# RAG_PROMPT_TEMPLATE = """
# You are a retrieval-based assistant.

# Rules:
# - Answer ONLY using the information in the Context.
# - If the Context does not clearly answer the question, say exactly:
#   "I don't know based on the provided posts."
# - Do NOT guess.
# - Answer in ONE short sentence.

# Context:
# {context}

# Question:
# {question}

# Answer:
# """
# RAG_PROMPT_TEMPLATE = """
# You are a hybrid assistant combining your own general knowledge with retrieval-based evidence.

# Instructions:
# 1. First, answer the Question using your own general knowledge and reasoning.
#    - This part may go beyond the Context.
#    - Keep it concise and accurate.
# 2. Then, provide a separate paragraph that is strictly grounded in the Context.
#    - Use ONLY the information present in the Context.
#    - Do NOT add assumptions or external knowledge.
#    - If the Context does not answer the question, say exactly:
#      "I don't know based on the provided posts."

# Formatting Rules:
# - Output must have exactly TWO sections:
#   1. "Model Answer:"
#   2. "Database Evidence:"
# - The "Database Evidence" section must be a short framed paragraph based only on the Context.
# - Do NOT merge the two sections.
# - Do NOT guess or hallucinate in the database-based section.

# Context:
# {context}

# Question:
# {question}

# Answer:
# Model Answer:
# <your own answer here>

# Database Evidence:
# <answer derived strictly from the context here>
# """





RAG_PROMPT_TEMPLATE = """
You are a hybrid assistant that combines your own general knowledge with retrieval-based evidence.

Primary Objective:
Provide a comprehensive, well-structured answer in two clearly separated parts:
1. An expanded answer based on your own general knowledge and reasoning.
2. A detailed, well-framed answer strictly grounded in the retrieved Context.

Instructions:

SECTION 1 – Model Answer:
- First, answer the Question using your own general knowledge and reasoning.
- Provide a detailed explanation (multiple sentences or short paragraphs).
- You may include background, explanations, examples, or clarifications.
- Do NOT reference the Context explicitly in this section.
- Do NOT mention databases, retrieval, or documents.

SECTION 2 – Database Evidence:
- Provide a detailed paragraph (or multiple sentences) based ONLY on the Context.
- Rephrase and summarize the Context in a coherent, explanatory manner.
- Do NOT add any new facts, assumptions, or external knowledge.
- Do NOT contradict the Context.
- If the Context does not clearly answer the Question, say exactly:
  "I don't know based on the provided posts."

Formatting Rules:
- Output must contain exactly TWO section headers:
  "Model Answer:" and "Database Evidence:"
- Each section may contain multiple sentences or short paragraphs.
- Do NOT merge or cross-reference the two sections.
- Do NOT guess or hallucinate in the Database Evidence section.

Context:
{context}

Question:
{question}

Answer:

Model Answer:
<expanded explanation here>

Database Evidence:
<expanded explanation strictly derived from the context here>
"""


# --------------------------------------------------
# SCHEMAS
# --------------------------------------------------
class SearchQuery(BaseModel):
    query: str

class RAGQuery(BaseModel):
    question: str

class RAGResponse(BaseModel):
    answer: str
    sources: List[dict]

# --------------------------------------------------
# VECTOR SEARCH (FIXED)
# --------------------------------------------------
@app.post("/search")
def search_similar_posts(query: SearchQuery):
    if not query.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    vector = embedder.encode(query.query).tolist()

    # 🔥 ALWAYS RETURN TOP 5 — NO SCORE THRESHOLD
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=5,
        with_payload=True,
    )

    return {
        "results": [
            {
                "post_id": r.payload.get("post_id"),
                "name": r.payload.get("name"),
                "caption": r.payload.get("caption"),
                "media_url": r.payload.get("media_url"),
                "media_type": r.payload.get("media_type"),
                "similarity_score": round(r.score, 4),
            }
            for r in results
        ]
    }

# --------------------------------------------------
# RAG ENDPOINT (STABLE)
# --------------------------------------------------
@app.post("/rag", response_model=RAGResponse)
def rag_answer(query: RAGQuery):
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    vector = embedder.encode(query.question).tolist()

    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=5,  # TOP 5 ALWAYS
        with_payload=True,
    )

    if not hits:
        return {
            "answer": "I don't know based on the provided posts.",
            "sources": [],
        }

    context_blocks = []
    sources = []

    for h in hits:
        caption = h.payload.get("caption", "")
        if caption:
            context_blocks.append(caption)

        sources.append({
            "post_id": h.payload.get("post_id"),
            "name": h.payload.get("name"),
            "caption": caption,
            "media_url": h.payload.get("media_url"),
            "media_type": h.payload.get("media_type"),
            "similarity_score": round(h.score, 4),
        })

    prompt = RAG_PROMPT_TEMPLATE.format(
        context="\n".join(context_blocks),
        question=query.question,
    )

    try:
        raw_answer = generate_llm_answer(prompt)
        answer = clean_answer(raw_answer)
    except Exception as e:
        print(f"❌ LLM Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLM failed to generate answer: {str(e)}")

    if not answer or len(answer) < 3:
        answer = "I don't know based on the provided posts."

    return {
        "answer": answer,
        "sources": sources,
    }

# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
