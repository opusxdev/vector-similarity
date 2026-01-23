from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/vector_db')
client = MongoClient(MONGO_URI)
db = client['social_media_db']
posts_collection = db['posts']

# Create unique index on post_id
posts_collection.create_index('post_id', unique=True)

class Post:
    @staticmethod
    def create_post(post_id, name, caption, media_url, media_type='image'):
        """Create a new post"""
        post = {
            'post_id': post_id,
            'name': name,
            'caption': caption,
            'media_url': media_url,
            'media_type': media_type,  # 'image' or 'video'
            'created_at': datetime.utcnow()
        }
        
        result = posts_collection.insert_one(post)
        return str(result.inserted_id)
    
    @staticmethod
    def get_post(post_id):
        """Get a post by ID"""
        return posts_collection.find_one({'post_id': post_id})
    
    @staticmethod
    def get_all_posts():
        """Get all posts"""
        return list(posts_collection.find())
    
    @staticmethod
    def delete_post(post_id):
        """Delete a post"""
        return posts_collection.delete_one({'post_id': post_id})

if __name__ == '__main__':
    print("Testing MongoDB connection...")
    try:
        # check for connectionsuccess
        client.admin.command('ping')
        print("MongoDB connected successfully!")
        print(f"Database: {db.name}")
        print(f"Collection: {posts_collection.name}")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")



