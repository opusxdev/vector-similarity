const { MongoClient, ObjectId } = require('mongodb');
require('dotenv').config();

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DB_NAME = 'social_media_db';
const COLLECTION_NAME = 'posts';
const COMMENTS_COLLECTION = 'comments';
const SAVES_COLLECTION = 'saved_posts';
const SHARES_COLLECTION = 'shares';

let client = null;
let db = null;
let collection = null;
let commentsCollection = null;
let savesCollection = null;
let sharesCollection = null;

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
        commentsCollection = db.collection(COMMENTS_COLLECTION);
        savesCollection = db.collection(SAVES_COLLECTION);
        sharesCollection = db.collection(SHARES_COLLECTION);

        // Create indexes on post_id
        await collection.createIndex({ post_id: 1 }, { unique: true });
        await commentsCollection.createIndex({ post_id: 1 });
        await commentsCollection.createIndex({ user_id: 1 });
        await commentsCollection.createIndex({ created_at: -1 });
        await savesCollection.createIndex({ post_id: 1 });
        await savesCollection.createIndex({ user_id: 1 });
        await savesCollection.createIndex({ user_id: 1, post_id: 1 }, { unique: true });
        await sharesCollection.createIndex({ post_id: 1 });
        await sharesCollection.createIndex({ shared_by: 1 });

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

    // ===== COMMENTS METHODS =====
    static async addComment(postId, userId, commentText) {
        await this.getCollection(); // Ensure DB is initialized
        const comment = {
            _id: new ObjectId(),
            post_id: postId,
            user_id: userId,
            text: commentText,
            created_at: new Date(),
            likes: 0
        };
        await commentsCollection.insertOne(comment);
        return comment;
    }

    static async getComments(postId) {
        await this.getCollection();
        return await commentsCollection.find({ post_id: postId })
            .sort({ created_at: -1 })
            .toArray();
    }

    static async deleteComment(commentId) {
        await this.getCollection();
        const result = await commentsCollection.deleteOne({ _id: new ObjectId(commentId) });
        return result.deletedCount > 0;
    }

    static async getCommentCount(postId) {
        await this.getCollection();
        return await commentsCollection.countDocuments({ post_id: postId });
    }

    // ===== SAVES METHODS =====
    static async savePost(postId, userId) {
        await this.getCollection();
        const savedPost = {
            _id: new ObjectId(),
            post_id: postId,
            user_id: userId,
            saved_at: new Date()
        };
        await savesCollection.insertOne(savedPost);
        return savedPost;
    }

    static async removeSavedPost(postId, userId) {
        await this.getCollection();
        const result = await savesCollection.deleteOne({
            post_id: postId,
            user_id: userId
        });
        return result.deletedCount > 0;
    }

    static async getSavedPosts(userId) {
        await this.getCollection();
        const saved = await savesCollection.find({ user_id: userId })
            .sort({ saved_at: -1 })
            .toArray();
        
        // Fetch full post details
        const posts = [];
        for (const savedItem of saved) {
            const post = await this.getPost(savedItem.post_id);
            if (post) {
                posts.push({ ...post, saved_at: savedItem.saved_at });
            }
        }
        return posts;
    }

    static async isPostSaved(postId, userId) {
        await this.getCollection();
        const saved = await savesCollection.findOne({
            post_id: postId,
            user_id: userId
        });
        return !!saved;
    }

    static async getSaveCount(postId) {
        await this.getCollection();
        return await savesCollection.countDocuments({ post_id: postId });
    }

    // ===== SHARES METHODS =====
    static async sharePost(postId, sharedBy, platform = 'direct') {
        await this.getCollection();
        const share = {
            _id: new ObjectId(),
            post_id: postId,
            shared_by: sharedBy,
            platform: platform,
            shared_at: new Date()
        };
        await sharesCollection.insertOne(share);
        return share;
    }

    static async getShares(postId) {
        await this.getCollection();
        return await sharesCollection.find({ post_id: postId })
            .sort({ shared_at: -1 })
            .toArray();
    }

    static async getShareCount(postId) {
        await this.getCollection();
        return await sharesCollection.countDocuments({ post_id: postId });
    }

    static async getUserShares(userId) {
        await this.getCollection();
        return await sharesCollection.find({ shared_by: userId })
            .sort({ shared_at: -1 })
            .toArray();
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