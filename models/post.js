const { MongoClient, ObjectId } = require('mongodb');
require('dotenv').config();

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DB_NAME = 'social_media_db';
const COLLECTION_NAME = 'posts';

let client = null;
let db = null;
let collection = null;

// Initialize MongoDB connection
async function initMongoDB() {
    if (client && client.topology && client.topology.isConnected()) {
        return collection;
    }

    try {
        client = new MongoClient(MONGODB_URI);
        await client.connect();
        console.log('✓ Connected to MongoDB');

        db = client.db(DB_NAME);
        collection = db.collection(COLLECTION_NAME);

        // Create index on post_id
        await collection.createIndex({ post_id: 1 }, { unique: true });

        return collection;
    } catch (error) {
        console.error('MongoDB connection error:', error);
        throw error;
    }
}

// Post class with static methods
class Post {
    static async getCollection() {
        if (!collection) {
            await initMongoDB();
        }
        return collection;
    }

    static async getAllPosts() {
        const coll = await this.getCollection();
        const posts = await coll.find({}).sort({ created_at: -1 }).toArray();
        return posts;
    }

    static async getPost(postId) {
        const coll = await this.getCollection();
        const post = await coll.findOne({ post_id: postId });
        return post;
    }

    static async createPost({ post_id, name, caption, media_url, media_type = 'image', category = 'unknown' }) {
        const coll = await this.getCollection();

        const postDoc = {
            post_id,
            name,
            caption,
            media_url,
            media_type,
            category,
            created_at: new Date(),
            updated_at: new Date()
        };

        const result = await coll.insertOne(postDoc);
        return { ...postDoc, _id: result.insertedId };
    }

    static async updatePost(postId, updateData) {
        const coll = await this.getCollection();

        const result = await coll.updateOne(
            { post_id: postId },
            {
                $set: {
                    ...updateData,
                    updated_at: new Date()
                }
            }
        );

        if (result.matchedCount === 0) {
            return null;
        }

        return await this.getPost(postId);
    }

    static async deletePost(postId) {
        const coll = await this.getCollection();
        const result = await coll.deleteOne({ post_id: postId });
        return result.deletedCount > 0;
    }

    static async searchPosts(query) {
        const coll = await this.getCollection();
        const posts = await coll.find({
            $or: [
                { name: { $regex: query, $options: 'i' } },
                { caption: { $regex: query, $options: 'i' } }
            ]
        }).toArray();
        return posts;
    }

    static async getPostCount() {
        const coll = await this.getCollection();
        return await coll.countDocuments();
    }

    static async syncMissingCategories(mapping) {
        const coll = await this.getCollection();
        console.log('Syncing categories in MongoDB...');
        for (const [postId, category] of Object.entries(mapping)) {
            await coll.updateOne(
                { post_id: postId, category: { $exists: false } },
                { $set: { category: category } }
            );
            // Also update "unknown" categories
            await coll.updateOne(
                { post_id: postId, category: "unknown" },
                { $set: { category: category } }
            );
        }
        console.log('✓ Category sync complete');
    }
}

// Graceful shutdown
process.on('SIGINT', async () => {
    if (client) {
        await client.close();
        console.log('MongoDB connection closed');
    }
    process.exit(0);
});

module.exports = Post;