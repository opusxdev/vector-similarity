

# dev3 

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
import requests
import random

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


load_dotenv()

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "..", "frontend", "dist")

app = FastAPI(
    title="Post Similarity API",
    description="Find similar social media posts using vector embeddings",
    version="1.0.0"
);

# Serve frontend static files
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")),
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
LIKES_COLLECTION = 'user_likes'
print(f"Connected to collection: {COLLECTION_NAME}\n")

# Create likes collection if it doesn't exist
try:
    from qdrant_client.models import Distance, VectorParams
    qdrant_client.create_collection(
        collection_name=LIKES_COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print(f"✓ Created likes collection: {LIKES_COLLECTION}")
except Exception as e:
    print(f"Likes collection already exists or error: {e}")

# RAG prompt template
RAG_PROMPT_TEMPLATE = """You are a helpful assistant analyzing social media posts to answer questions.

Context (Social Media Posts):
{context}

Question: {question}

Provide your answer in TWO clear sections:

1. Model Answer: Use your general knowledge and reasoning to answer the question comprehensively.

2. Database Evidence: Based ONLY on the posts above, what specific information supports or relates to this question? Quote or paraphrase relevant parts from the posts. If the posts don't contain relevant information, state "The provided posts do not contain information about this topic."

Format your response exactly as shown above with clear section headers."""


def generate_llm_answer(prompt: str) -> str:
    """Call Groq chat completion API to generate the RAG answer."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that analyzes social media posts. Always provide clear, structured answers with both general knowledge and specific evidence from provided posts.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.5,
        "max_tokens": 1000,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        print("Groq API Error:", resp.status_code, resp.text)
        resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()

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
    user_id: Optional[str] = "default_user"
    last_liked_post_ids: Optional[List[str]] = None  # Optional: prefer personalization based on up to 2 recently liked posts

class LikeRequest(BaseModel):
    post_id: str
    user_id: str = "default_user"

class RAGQuery(BaseModel):
    question: str
    limit: int = 5
    min_score: float = 0.1

class RAGResponse(BaseModel):
    answer: str
    sources: List[dict]

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
            "POST /like": "Like a post",
            "GET /likes/{user_id}": "Get user's liked posts",
            "GET /similar/{post_id}": "Find similar posts to a specific post",
            "DELETE /posts/{post_id}": "Delete a post",
            "GET /stats": "Get system statistics"
        }
    }



@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

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

@app.post("/like")
def like_post(like_req: LikeRequest):
    """Store user's liked post vector"""
    try:
        # Validate post_id format
        if not like_req.post_id.startswith('post_') or not like_req.post_id.replace('post_', '').isdigit():
            raise HTTPException(
                status_code=400,
                detail="post_id must be in format 'post_001', 'post_002', etc."
            )
        
        post_id_num = int(like_req.post_id.replace('post_', ''))
        
        # Get the post vector from main collection
        post_data = qdrant_client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[post_id_num],
            with_vectors=True
        )
        
        if not post_data:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post_vector = post_data[0].vector
        post_payload = post_data[0].payload
        
        # Store in likes collection with unique ID per user-post combination
        from qdrant_client.models import PointStruct
        import hashlib
        
        # Create unique ID for this like
        like_id_str = f"{like_req.user_id}_{like_req.post_id}"
        like_id = int(hashlib.md5(like_id_str.encode()).hexdigest()[:8], 16)
        
        like_point = PointStruct(
            id=like_id,
            vector=post_vector,
            payload={
                'user_id': like_req.user_id,
                'post_id': like_req.post_id,
                'name': post_payload['name'],
                'caption': post_payload['caption'],
                'media_url': post_payload.get('media_url', ''),
                'liked_at': datetime.utcnow().isoformat()
            }
        )
        
        qdrant_client.upsert(
            collection_name=LIKES_COLLECTION,
            points=[like_point]
        )
        
        return {
            "message": "Post liked successfully",
            "post_id": like_req.post_id,
            "user_id": like_req.user_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# iso
@app.get("/likes/{user_id}")
def get_user_likes(user_id: str):
    """Get all posts liked by a user"""
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Check if collection exists
        try:
            qdrant_client.get_collection(LIKES_COLLECTION)
        except Exception as e:
            # Collection doesn't exist, return empty likes
            return {
                "user_id": user_id,
                "total_likes": 0,
                "liked_posts": []
            }
        
        # Search for all likes by this user
        scroll_result = qdrant_client.scroll(
            collection_name=LIKES_COLLECTION,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=100,
            with_vectors=False,
            with_payload=True
        )
        
        liked_posts = []
        if scroll_result and len(scroll_result) > 0:
            for point in scroll_result[0]:
                liked_posts.append({
                    'post_id': point.payload.get('post_id', ''),
                    'name': point.payload.get('name', ''),
                    'caption': point.payload.get('caption', ''),
                    'media_url': point.payload.get('media_url', ''),
                    'liked_at': point.payload.get('liked_at', '')
                })
        
        return {
            "user_id": user_id,
            "total_likes": len(liked_posts),
            "liked_posts": liked_posts
        }
    
    except Exception as e:
        print(f"Error in get_user_likes: {e}")
        # Return empty response instead of 500 error
        return {
            "user_id": user_id,
            "total_likes": 0,
            "liked_posts": []
        }



#iso2
@app.post("/search")
def search_similar_posts(query: SearchQuery):
    """
    Find similar posts based on text query.
    Returns:
    - 8 query-based results matching the search
    - 2 personalized results (based on user's likes) OR random from different categories
    """
    try:
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        print(f"/search called - query='{query.query}', user_id='{query.user_id}', last_liked_post_ids={query.last_liked_post_ids}")
        
        # Create embedding for query
        query_embedding = model.encode(query.query).tolist()
        
        # Get query-based results (8 posts)
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=8,
            score_threshold=query.min_score
        )
        
        results = []
        used_post_ids = set()
        query_categories = set()
        
        # Add query-based results
        for result in search_results:
            category = result.payload.get('category', 'unknown')
            query_categories.add(category)
            
            results.append({
                'post_id': result.payload['post_id'],
                'name': result.payload['name'],
                'caption': result.payload['caption'],
                'media_url': result.payload.get('media_url', ''),
                'media_type': result.payload.get('media_type', 'image'),
                'category': category,
                'similarity_score': round(result.score, 4),
                'similarity_percentage': f"{round(result.score * 100, 2)}%",
                'source': 'query'
            })
            used_post_ids.add(result.payload['post_id'])
        
        print(f"Query results: {len(results)}, Categories: {query_categories}")
        
        # Try to get personalized recommendations based on user's liked posts
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        import numpy as np
        
        personalized_added = 0
        
        try:
            # If frontend provided a list of most-recently-liked post ids, prefer personalization from those posts
            if query.last_liked_post_ids:
                try:
                    # Ensure it's a list and process up to 2 ids
                    liked_ids = [lid for lid in (query.last_liked_post_ids or []) if isinstance(lid, str)][:2]
                    for lid in liked_ids:
                        if (not lid.startswith('post_') or not lid.replace('post_', '').isdigit()):
                            print(f"Skipping invalid liked id: {lid}")
                            continue
                        liked_post_num = int(lid.replace('post_', ''))
                        liked_post_data = qdrant_client.retrieve(
                            collection_name=COLLECTION_NAME,
                            ids=[liked_post_num],
                            with_vectors=True
                        )

                        if not liked_post_data or len(liked_post_data) == 0:
                            continue

                        liked_vector = liked_post_data[0].vector

                        # Search for posts similar to the liked post vector
                        personalized_results = qdrant_client.search(
                            collection_name=COLLECTION_NAME,
                            query_vector=liked_vector,
                            limit=30,
                            score_threshold=0.2
                        )

                        for result in personalized_results:
                            post_id = result.payload['post_id']
                            # Skip if already used or is the liked post itself
                            if post_id in used_post_ids or post_id == lid:
                                continue

                            # Add one personalized result per liked_id until we have 2
                            if personalized_added < 2:
                                results.append({
                                    'post_id': post_id,
                                    'name': result.payload['name'],
                                    'caption': result.payload['caption'],
                                    'media_url': result.payload.get('media_url', ''),
                                    'media_type': result.payload.get('media_type', 'image'),
                                    'category': result.payload.get('category', 'unknown'),
                                    'similarity_score': round(result.score, 4),
                                    'similarity_percentage': f"{round(result.score * 100, 2)}%",
                                    'source': 'personalized',
                                    'based_on': lid
                                })
                                used_post_ids.add(post_id)
                                personalized_added += 1

                                if personalized_added >= 2:
                                    break

                        if personalized_added >= 2:
                            break

                    print(f"Personalized posts added using last_liked_post_ids: {personalized_added}")
                except Exception as e:
                    print(f"Error personalizing from last_liked_post_ids: {e}")

            # If we didn't add enough personalized posts yet, fall back to averaging user's liked vectors
            if personalized_added < 2:
                print("FALLBACK: trying average liked-vectors personalization")
                # Check if likes collection exists
                qdrant_client.get_collection(LIKES_COLLECTION)
                
                # Get user's liked posts
                user_likes = qdrant_client.scroll(
                    collection_name=LIKES_COLLECTION,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="user_id",
                                match=MatchValue(value=query.user_id)
                            )
                        ]
                    ),
                    limit=50,  # Get more likes for better recommendations
                    with_vectors=True,
                    with_payload=True
                )[0]
                
                if user_likes and len(user_likes) > 0:
                    print(f"Found {len(user_likes)} liked posts by user (fallback)")
                    
                    # Average the vectors of liked posts
                    liked_vectors = [point.vector for point in user_likes]
                    avg_vector = np.mean(liked_vectors, axis=0).tolist()
                    
                    # Search for posts similar to what user has liked
                    personalized_results = qdrant_client.search(
                        collection_name=COLLECTION_NAME,
                        query_vector=avg_vector,
                        limit=30,  # Get many to filter from
                        score_threshold=0.25  # Lower threshold for personalization
                    )
                    
                    # Filter: Only add posts that are NOT in the current query categories
                    # This ensures personalized posts are from different topics
                    for result in personalized_results:
                        post_category = result.payload.get('category', 'unknown')
                        post_id = result.payload['post_id']
                        
                        # Skip if already used or same category as query results
                        if post_id in used_post_ids:
                            continue
                        if post_category in query_categories and len(query_categories) > 0:
                            continue
                        
                        if personalized_added < 2:
                            results.append({
                                'post_id': post_id,
                                'name': result.payload['name'],
                                'caption': result.payload['caption'],
                                'media_url': result.payload.get('media_url', ''),
                                'media_type': result.payload.get('media_type', 'image'),
                                'category': post_category,
                                'similarity_score': round(result.score, 4),
                                'similarity_percentage': f"{round(result.score * 100, 2)}%",
                                'source': 'personalized'
                            })
                            used_post_ids.add(post_id)
                            personalized_added += 1
                            print(f"Added personalized post from category: {post_category}")
                            
                            if personalized_added >= 2:
                                break
                    
                    print(f"Personalized posts added: {personalized_added}")
                else:
                    print("No liked posts found for user (fallback)")
        except Exception as e:
            print(f"Personalization error: {e}")

        # FINAL RELAXED FALLBACK: If we still don't have 2 personalized posts, try again
        # using the liked ids but allow posts from any category (ignore query_categories)
        if personalized_added < 2 and query.last_liked_post_ids:
            try:
                print("FINAL FALLBACK: attempting relaxed personalization using liked ids (ignoring categories)")
                for lid in (query.last_liked_post_ids or [])[:2]:
                    if not lid or not isinstance(lid, str):
                        continue
                    if (not lid.startswith('post_') or not lid.replace('post_', '').isdigit()):
                        continue
                    liked_num = int(lid.replace('post_', ''))
                    liked_data = qdrant_client.retrieve(
                        collection_name=COLLECTION_NAME,
                        ids=[liked_num],
                        with_vectors=True
                    )
                    if not liked_data:
                        continue
                    vec = liked_data[0].vector
                    # search with low threshold and don't care about category
                    relaxed_hits = qdrant_client.search(
                        collection_name=COLLECTION_NAME,
                        query_vector=vec,
                        limit=20,
                        score_threshold=0.0
                    )
                    for r in relaxed_hits:
                        pid = r.payload['post_id']
                        if pid in used_post_ids or pid == lid:
                            continue
                        results.append({
                            'post_id': pid,
                            'name': r.payload.get('name', ''),
                            'caption': r.payload.get('caption', ''),
                            'media_url': r.payload.get('media_url', ''),
                            'media_type': r.payload.get('media_type', 'image'),
                            'category': r.payload.get('category', 'unknown'),
                            'similarity_score': round(r.score, 4),
                            'similarity_percentage': f"{round(r.score * 100, 2)}%",
                            'source': 'personalized_relaxed',
                            'based_on': lid
                        })
                        used_post_ids.add(pid)
                        personalized_added += 1
                        print(f"FINAL FALLBACK added personalized post {pid} based on {lid}")
                        if personalized_added >= 2:
                            break
                    if personalized_added >= 2:
                        break
            except Exception as e:
                print(f"Final relaxed personalization error: {e}")
        
        # Fill remaining slots with random posts from DIFFERENT categories
        random_added = 0
        needed = 10 - len(results)
        
        if needed > 0:
            try:
                # Get all posts
                scroll_result = qdrant_client.scroll(
                    collection_name=COLLECTION_NAME,
                    limit=200,  # Get many posts
                    with_vectors=False,
                    with_payload=True
                )
                
                all_posts = scroll_result[0]
                
                # Filter: posts from different categories, not already used
                available_posts = [
                    p for p in all_posts 
                    if p.payload['post_id'] not in used_post_ids
                    and p.payload.get('category', 'unknown') not in query_categories
                ]
                
                print(f"Available random posts from different categories: {len(available_posts)}")
                
                # If no posts from different categories, just use any unused posts
                if not available_posts:
                    available_posts = [
                        p for p in all_posts 
                        if p.payload['post_id'] not in used_post_ids
                    ]
                    print(f"Fallback: Using any available posts: {len(available_posts)}")
                
                # Randomly shuffle and pick
                if available_posts:
                    random.shuffle(available_posts)
                    for post in available_posts[:needed]:
                        results.append({
                            'post_id': post.payload['post_id'],
                            'name': post.payload['name'],
                            'caption': post.payload['caption'],
                            'media_url': post.payload.get('media_url', ''),
                            'media_type': post.payload.get('media_type', 'image'),
                            'category': post.payload.get('category', 'unknown'),
                            'similarity_score': 0.0,
                            'similarity_percentage': "Random",
                            'source': 'random'
                        })
                        random_added += 1
                        print(f"Added random post from category: {post.payload.get('category')}")
                
                print(f"Random posts added: {random_added}")
            except Exception as e:
                print(f"Random posts error: {e}")
        
        breakdown = {
            "query_based": len([r for r in results if r['source'] == 'query']),
            "personalized": len([r for r in results if r['source'] == 'personalized']),
            "random": len([r for r in results if r['source'] == 'random'])
        }
        
        print(f"Final breakdown: {breakdown}")
        print(f"Total results: {len(results)}")
        
        return {
            "query": query.query,
            "user_id": query.user_id,
            "total_results": len(results),
            "breakdown": breakdown,
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
#iso2
@app.get("/similar/{post_id}")
def find_similar_to_post(post_id: str, limit: int = 5, min_score: float = 0.0):
    try:
        if not post_id.startswith('post_') or not post_id.replace('post_', '').isdigit():
            raise HTTPException(
                status_code=400,
                detail="post_id must be in format 'post_001', 'post_002', etc."
            )
        
        post_id_num = int(post_id.replace('post_', ''))
        
        post_data = qdrant_client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[post_id_num],
            with_vectors=True
        )
        
        if not post_data:
            raise HTTPException(status_code=404, detail="Post not found in vector database")
        
        post_vector = post_data[0].vector
        original_post = post_data[0].payload
        
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=post_vector,
            limit=limit + 1, 
            score_threshold=min_score
        )
        
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
        
        post_id_num = int(post_id.replace('post_', ''))
        
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
        likes_info = qdrant_client.get_collection(LIKES_COLLECTION)
        
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
            "likes": {
                "collection_name": LIKES_COLLECTION,
                "total_likes": likes_info.points_count
            },
            "model": {
                "name": "all-MiniLM-L6-v2",
                "dimensions": 384
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag", response_model=RAGResponse)
def rag_answer(body: RAGQuery):
    """
    RAG endpoint: retrieves similar posts from Qdrant and asks the LLM
    to answer using the improved prompt template.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # 1) Embed question
    try:
        question_embedding = model.encode(body.question).tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed question: {e}")

    # 2) Retrieve from Qdrant
    try:
        hits = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=question_embedding,
            limit=body.limit,
            score_threshold=body.min_score,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")

    if not hits:
        return RAGResponse(
            answer="Model Answer:\nI don't have enough information to answer this question.\n\nDatabase Evidence:\nThe provided posts do not contain information about this topic.",
            sources=[],
        )

    # 3) Build context with more details for better LLM understanding
    context_blocks = []
    sources: List[dict] = []

    for idx, h in enumerate(hits):
        caption = h.payload.get("caption", "") or ""
        name = h.payload.get("name", "") or ""
        post_id = h.payload.get("post_id", "")
        
        if caption:
            context_entry = f"Post {idx + 1} (by {name}, ID: {post_id}):\n{caption}"
            context_blocks.append(context_entry)

        sources.append({
            "post_id": post_id,
            "name": name,
            "caption": caption,
            "media_url": h.payload.get("media_url", ""),
            "media_type": h.payload.get("media_type", "image"),
            "similarity_score": round(h.score, 4),
        })

    context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant posts found."

    prompt = RAG_PROMPT_TEMPLATE.format(
        context=context_text,
        question=body.question,
    )

    # 4) Call LLM
    try:
        answer_text = generate_llm_answer(prompt)
    except Exception as e:
        print("LLM error in /rag:", e)
        model_part = "Model Answer:\nBased on the retrieved posts, here is what I found.\n"
        if context_blocks:
            evidence_part = "Database Evidence:\n" + "\n".join([f"- {block}" for block in context_blocks])
        else:
            evidence_part = "Database Evidence:\nThe provided posts do not contain information about this topic."
        answer_text = f"{model_part}\n{evidence_part}"

    return RAGResponse(answer=answer_text, sources=sources)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        Post.get_all_posts()
        mongodb_status = "healthy"
    except:
        mongodb_status = "unhealthy"
    
    try:
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