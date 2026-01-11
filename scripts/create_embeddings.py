import sys
sys.path.append('..')

from models.post import Post
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize embedding model
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Model loaded (384 dimensions)")

# Initialize Qdrant client (Cloud)
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')

if not QDRANT_URL or not QDRANT_API_KEY:
    print("❌ Error: QDRANT_URL or QDRANT_API_KEY not found in .env file!")
    sys.exit(1)

print(f"\n🔗 Connecting to Qdrant Cloud...")
print(f"   URL: {QDRANT_URL}")

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

COLLECTION_NAME = 'social_posts'

def create_collection():
    """Create Qdrant collection"""
    try:
        # Check if collection exists
        collections = qdrant_client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if COLLECTION_NAME in collection_names:
            print(f"🗑️  Deleting existing collection: {COLLECTION_NAME}")
            qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
    except Exception as e:
        print(f"Note: {e}")
    
    # Create new collection
    print(f"🆕 Creating collection: {COLLECTION_NAME}")
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,  # all-MiniLM-L6-v2 produces 384-dimensional vectors
            distance=Distance.COSINE
        )
    )
    print(f"✓ Collection created successfully")

def create_embedding(text):
    """Create embedding for text"""
    embedding = model.encode(text)
    return embedding.tolist()

def embed_all_posts():
    """Fetch posts from MongoDB and store embeddings in Qdrant"""
    print("\n📊 Fetching posts from MongoDB...")
    posts = Post.get_all_posts()
    print(f"✓ Found {len(posts)} posts\n")
    
    if not posts:
        print("❌ No posts found in database!")
        return
    
    print("🔄 Creating embeddings and storing in Qdrant...")
    points = []
    
    for i, post in enumerate(posts, 1):
        # Combine name and caption for richer embedding
        text_to_embed = f"{post['name']}: {post['caption']}"
        
        # Create embedding
        embedding = create_embedding(text_to_embed)
        
        # Convert post_id string to integer hash for Qdrant
        # We'll extract the number from "post_001" format
        post_id_num = int(post['post_id'].replace('post_', ''))
        
        # Prepare point for Qdrant (use integer ID)
        point = PointStruct(
            id=post_id_num,  # Changed: Use integer instead of string
            vector=embedding,
            payload={
                'post_id': post['post_id'],  # Keep original string ID in payload
                'name': post['name'],
                'caption': post['caption'],
                'media_url': post['media_url'],
                'media_type': post['media_type'],
                'created_at': post['created_at'].isoformat()
            }
        )
        
        points.append(point)
        print(f"  [{i}/{len(posts)}] ✓ Embedded: {post['post_id']} - {post['name']}")
    
    # Upload all points to Qdrant
    print("\n☁️  Uploading to Qdrant Cloud...")
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    
    print(f"\n✅ Successfully stored {len(points)} embeddings in Qdrant Cloud!")

def verify_collection():
    """Verify collection was created properly"""
    print("\n🔍 Verifying collection...")
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    print(f"\n=== Collection Info ===")
    print(f"✓ Collection name: {COLLECTION_NAME}")
    print(f"✓ Total vectors: {collection_info.points_count}")
    print(f"✓ Vector size: {collection_info.config.params.vectors.size}")
    print(f"✓ Distance metric: {collection_info.config.params.vectors.distance}")

def main():
    print("=" * 60)
    print("🚀 EMBEDDING CREATION SCRIPT")
    print("=" * 60)
    
    try:
        create_collection()
        embed_all_posts()
        verify_collection()
        
        print("\n" + "=" * 60)
        print("✅ PROCESS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()