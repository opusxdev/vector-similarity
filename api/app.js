const express = require('express');
const cors = require('cors');
const path = require('path');
const axios = require('axios');
const crypto = require('crypto');
require('dotenv').config();

const Post = require('../models/post');
const { QdrantClient } = require('@qdrant/js-client-rest');

const app = express();
const BASE_DIR = __dirname;
const FRONTEND_DIST = path.join(BASE_DIR, '..', 'frontend', 'dist');

app.use(express.json());
app.use(cors({
    origin: 'https://huggingface.co/spaces/opusdev/vector-similarity-api',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['*']
}));
app.use('/assets', express.static(path.join(FRONTEND_DIST, 'assets')));

// env validate 
const REQUIRED_ENV = ['QDRANT_URL', 'QDRANT_API_KEY', 'GROQ_API_KEY'];
const missingEnv = REQUIRED_ENV.filter(k => !process.env[k]);
if (missingEnv.length > 0) {
    console.error('\n Missing env vars:', missingEnv.join(', '));
    process.exit(1);
}

//qdrant
const qdrantClient = new QdrantClient({
    url: process.env.QDRANT_URL,
    apiKey: process.env.QDRANT_API_KEY,
    checkCompatibility: false,
});

const COLLECTION_NAME = 'social_posts';
const LIKES_COLLECTION = 'user_likes';
const EMBEDDING_SERVICE_URL = process.env.EMBEDDING_SERVICE_URL || 'http://localhost:8001';

(async () => {
    try {
        const r = await axios.get(`${EMBEDDING_SERVICE_URL}/health`, { timeout: 5000 });
        console.log(`embedding service OK: model=${r.data.model}`);
    } catch {
        console.error(` embedding service not reachable at ${EMBEDDING_SERVICE_URL}`);
    }
    try {
        await qdrantClient.createCollection(LIKES_COLLECTION, {
            vectors: { size: 384, distance: 'Cosine' },
        });
        console.log(`✓ Created ${LIKES_COLLECTION}`);
    } catch (e) {
        console.log(`${LIKES_COLLECTION}: ${e.message}`);
    }
})();

//utils
async function getEmbedding(text) {
    try {
        const r = await axios.post(`${EMBEDDING_SERVICE_URL}/embed`, { text }, { timeout: 10000 });
        return r.data.embedding;
    } catch (e) {
        if (e.code === 'ECONNREFUSED') throw new Error('Embedding service not running. Run: python api/embedding_service.py');
        throw new Error(`Embedding failed: ${e.message}`);
    }
}

async function generateLLMAnswer(prompt) {
    const r = await axios.post(
        'https://api.groq.com/openai/v1/chat/completions',
        {
            model: 'llama-3.1-8b-instant',
            messages: [
                { role: 'system', content: 'You analyze social media posts. Provide clear structured answers.' },
                { role: 'user', content: prompt },
            ],
            temperature: 0.5,
            max_tokens: 1000,
        },
        { headers: { 'Authorization': `Bearer ${process.env.GROQ_API_KEY}`, 'Content-Type': 'application/json' }, timeout: 30000 }
    );
    return r.data.choices[0].message.content.trim();
}

function shapePost(payload, score, source, basedOn = null) {
    return {
        post_id: payload.post_id,
        name: payload.name,
        caption: payload.caption,
        media_url: payload.media_url || '',
        media_type: payload.media_type || 'image',
        category: payload.category || 'unknown',
        similarity_score: Math.round(score * 10000) / 10000,
        similarity_percentage: source === 'random' ? 'Random' : `${Math.round(score * 10000) / 100}%`,
        source,
        ...(basedOn ? { based_on: basedOn } : {})
    };
}



async function buildInterestSlots(sessionLikedIds, usedPostIds, neededCount) {
    const interest = [];

    console.log(`  [interest] seeds requested: ${JSON.stringify(sessionLikedIds)}`);

    if (!sessionLikedIds || sessionLikedIds.length === 0) return interest;

    // Validate format
    const validIds = sessionLikedIds.filter(id =>
        typeof id === 'string' && id.startsWith('post_') && id.replace('post_', '').match(/^\d+$/)
    );

    if (validIds.length === 0) {
        console.log(`  [interest] no valid post IDs in session_liked_ids`);
        return interest;
    }

    console.log(`  [interest] valid seeds: ${JSON.stringify(validIds)}`);

    // Fetcher for  vectors for all liked posts fromcollection
    const likedNums = validIds.map(id => parseInt(id.replace('post_', '')));
    let likedPostData;
    try {
        likedPostData = await qdrantClient.retrieve(COLLECTION_NAME, {
            ids: likedNums,
            with_vector: true
        });
    } catch (e) {
        console.log(`  [interest] retrieve error: ${e.message}`);
        return interest;
    }

    console.log(`  [interest] retrieved ${likedPostData.length} post vectors`);

    if (likedPostData.length === 0) return interest;
    const seeds = likedPostData.slice(0, neededCount);

    for (const seed of seeds) {
        if (interest.length >= neededCount) break;

        const seedPostId = seed.payload.post_id;
        console.log(`  [interest] searching similar to seed=${seedPostId}`);

        let hits
        try {
            hits = await qdrantClient.search(COLLECTION_NAME, {
                vector: seed.vector,
                limit: 50,        
                score_threshold: 0.0
            });
        } catch (e) {
            console.log(`  [interest] vector search error: ${e.message}`);
            continue;
        }

        let picked = false;
        for (const hit of hits) {
            const pid = hit.payload.post_id;

            if (usedPostIds.has(pid)) continue;
            if (pid === seedPostId) continue;
           //skiper
            if (validIds.includes(pid)) continue;

            console.log(`  [interest] ✓ picked post_id=${pid} score=${hit.score.toFixed(4)} (seed=${seedPostId})`);
            interest.push(shapePost(hit.payload, hit.score, 'personalized', seedPostId));
            usedPostIds.add(pid);
            picked = true;
            break;
        }

        if (!picked) {
            console.log(`  [interest] seed=${seedPostId} — no unused similar posts found`);
        }
    }

    return interest;
}

async function buildRandomSlots(usedPostIds, neededCount) {
    const randoms = [];
    try {
        const result = await qdrantClient.scroll(COLLECTION_NAME, {
            limit: 500,
            with_vector: false,
            with_payload: true
        });
        let pool = (result.points || []).filter(p => !usedPostIds.has(p.payload.post_id));
        for (let i = pool.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [pool[i], pool[j]] = [pool[j], pool[i]];
        }

        for (const post of pool.slice(0, neededCount)) {
            randoms.push(shapePost(post.payload, 0, 'random'));
            usedPostIds.add(post.payload.post_id);
        }
    } catch (e) {
        console.error('buildRandomSlots error:', e.message);
    }
    return randoms;
}

// routes 

app.get('/api', (req, res) => res.json({ message: 'Post Similarity API', status: 'running' }));
app.get('/', (req, res) => res.sendFile(path.join(FRONTEND_DIST, 'index.html')));

// random posts for bento preloader 
app.get('/random', async (req, res) => {
    try {
        const count = Math.min(parseInt(req.query.count) || 12, 50);
        const result = await qdrantClient.scroll(COLLECTION_NAME, {
            limit: 500,
            with_vector: false,
            with_payload: true
        });
        let pool = result.points || [];

       
        for (let i = pool.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [pool[i], pool[j]] = [pool[j], pool[i]];
        }

        const posts = pool.slice(0, count).map(p => ({
            post_id:   p.payload.post_id,
            name:      p.payload.name,
            caption:   p.payload.caption,
            media_url: p.payload.media_url  || '',
            media_type:p.payload.media_type || 'image',
            category:  p.payload.category   || 'unknown',
        }));

        res.json({ total: posts.length, posts });
    } catch (e) {
        console.error('/random error:', e.message);
        res.status(500).json({ detail: e.message });
    }
});

app.get('/posts', async (req, res) => {
    try {
        const posts = await Post.getAllPosts();
        posts.forEach(p => { p._id = p._id.toString(); p.created_at = p.created_at.toISOString(); });
        res.json({ total: posts.length, posts });
    } catch (e) { res.status(500).json({ detail: e.message }); }
});

app.get('/posts/:post_id', async (req, res) => {
    try {
        const post = await Post.getPost(req.params.post_id);
        if (!post) return res.status(404).json({ detail: 'Post not found' });
        post._id = post._id.toString();
        post.created_at = post.created_at.toISOString();
        res.json(post);
    } catch (e) { res.status(500).json({ detail: e.message }); }
});

app.post('/posts', async (req, res) => {
    try {
        const { post_id, name, caption, media_url, media_type = 'image', category = 'unknown' } = req.body;

        if (!post_id.startsWith('post_') || !post_id.replace('post_', '').match(/^\d+$/)) {
            return res.status(400).json({ detail: "post_id must be in format 'post_001'" });
        }
        if (await Post.getPost(post_id)) return res.status(400).json({ detail: 'Post already exists' });

        await Post.createPost({ post_id, name, caption, media_url, media_type });
        const embedding = await getEmbedding(`${name}: ${caption}`);
        const postIdNum = parseInt(post_id.replace('post_', ''));

        await qdrantClient.upsert(COLLECTION_NAME, {
            wait: true,
            points: [{ id: postIdNum, vector: embedding, payload: { post_id, name, caption, media_url, media_type, category, created_at: new Date().toISOString() } }]
        });
        res.status(201).json({ message: 'Post created', post_id });
    } catch (e) { res.status(500).json({ detail: e.message }); }
});

// Like 
app.post('/like', async (req, res) => {
    try {
        const { post_id, user_id = 'default_user' } = req.body;

        if (!post_id.startsWith('post_') || !post_id.replace('post_', '').match(/^\d+$/)) {
            return res.status(400).json({ detail: "post_id must be in format 'post_001'" });
        }

        const postIdNum = parseInt(post_id.replace('post_', ''));
        const postData = await qdrantClient.retrieve(COLLECTION_NAME, { ids: [postIdNum], with_vector: true });
        if (!postData?.length) return res.status(404).json({ detail: 'Post not found' });

        const likeId = parseInt(
            crypto.createHash('md5').update(`${user_id}_${post_id}`).digest('hex').substring(0, 8), 16
        );

        await qdrantClient.upsert(LIKES_COLLECTION, {
            wait: true,
            points: [{
                id: likeId,
                vector: postData[0].vector,
                payload: {
                    user_id,
                    post_id,
                    name:      postData[0].payload.name,
                    caption:   postData[0].payload.caption,
                    media_url: postData[0].payload.media_url || '',
                    category:  postData[0].payload.category  || 'unknown',
                    liked_at:  new Date().toISOString()
                }
            }]
        });

        console.log(`  /like OK: user=${user_id} post=${post_id} category=${postData[0].payload.category || 'unknown'}`);
        res.json({ message: 'Post liked', post_id, user_id });
    } catch (e) {
        console.error('Like error:', e);
        res.status(500).json({ detail: e.message });
    }
});

app.get('/likes/:user_id', async (req, res) => {
    try {
        try { await qdrantClient.getCollection(LIKES_COLLECTION); }
        catch { return res.json({ user_id: req.params.user_id, total_likes: 0, liked_posts: [] }); }

        const result = await qdrantClient.scroll(LIKES_COLLECTION, {
            filter: { must: [{ key: 'user_id', match: { value: req.params.user_id } }] },
            limit: 100,
            with_vector: false,
            with_payload: true
        });

        const liked_posts = (result?.points || []).map(pt => ({
            post_id:   pt.payload.post_id   || '',
            name:      pt.payload.name      || '',
            caption:   pt.payload.caption   || '',
            media_url: pt.payload.media_url || '',
            category:  pt.payload.category  || 'unknown',
            liked_at:  pt.payload.liked_at  || ''
        }));

        res.json({ user_id: req.params.user_id, total_likes: liked_posts.length, liked_posts });
    } catch (e) {
        res.json({ user_id: req.params.user_id, total_likes: 0, liked_posts: [] });
    }
});
// debug 
app.get('/debug/likes/:user_id', async (req, res) => {
    try {
        const result = await qdrantClient.scroll(LIKES_COLLECTION, {
            filter: { must: [{ key: 'user_id', match: { value: req.params.user_id } }] },
            limit: 200,
            with_vector: true,
            with_payload: true
        });
        const points = result?.points || [];
        res.json({
            total: points.length,
            points: points.map(pt => ({
                post_id:    pt.payload.post_id,
                category:   pt.payload.category,
                liked_at:   pt.payload.liked_at,
                has_vector: Array.isArray(pt.vector) && pt.vector.length > 0,
            }))
        });
    } catch (e) { res.status(500).json({ detail: e.message }); }
});


app.post('/search', async (req, res) => {
    try {
        const {
            query,
            min_score        = 0.0,
            user_id          = 'default_user',
            session_liked_ids = [],   
        } = req.body;

        if (!query?.trim()) return res.status(400).json({ detail: 'Query cannot be empty' });

        const hasSessionLikes = Array.isArray(session_liked_ids) && session_liked_ids.length > 0;


        console.log(`/search  query="${query}"  user="${user_id}"`);
        console.log(`session_liked_ids: ${JSON.stringify(session_liked_ids)}`);
        console.log(`mode: ${hasSessionLikes ? 'INTEREST (personalized)' : 'RANDOM (first search)'}`);


        //query and get 8 queryresultsssss
        const queryEmbedding = await getEmbedding(query);

        const searchResults = await qdrantClient.search(COLLECTION_NAME, {
            vector: queryEmbedding,
            limit: 8,
            score_threshold: min_score
        });

        const results     = [];
        const usedPostIds = new Set();

        for (const r of searchResults) {
            results.push(shapePost(r.payload, r.score, 'query'));
            usedPostIds.add(r.payload.post_id);
        }

        console.log(`  query posts: ${results.length}`);

        // extra 2 (either random or interactionbased)
        const EXTRA = 2;

        if (!hasSessionLikes) {

            const randoms = await buildRandomSlots(usedPostIds, EXTRA);
            results.push(...randoms);
            console.log(`  random posts added: ${randoms.length}`);
        } else {
            const interest = await buildInterestSlots(session_liked_ids, usedPostIds, EXTRA);
            results.push(...interest);
            console.log(`  interest posts added: ${interest.length}`);
            const gap = EXTRA - interest.length;
            if (gap > 0) {
                const padded = await buildRandomSlots(usedPostIds, gap);
                results.push(...padded);
                console.log(`  padded ${padded.length} random (sparse session likes)`);
            }
        }

        const breakdown = {
            query_based:  results.filter(r => r.source === 'query').length,
            personalized: results.filter(r => r.source === 'personalized').length,
            random:       results.filter(r => r.source === 'random').length,
            mode:         hasSessionLikes ? 'personalized' : 'random',
        };

        console.log(`  final: ${JSON.stringify(breakdown)}`);
        console.log(`  posts: ${results.map(r => `${r.post_id}(${r.source})`).join(', ')}`);

        res.json({ query, user_id, total_results: results.length, breakdown, results });

    } catch (e) {
        console.error('Search error:', e);
        res.status(500).json({ detail: e.message });
    }
});

app.get('/similar/:post_id', async (req, res) => {
    try {
        const { post_id } = req.params;
        const limit     = parseInt(req.query.limit)       || 5;
        const min_score = parseFloat(req.query.min_score) || 0.0;

        if (!post_id.startsWith('post_') || !post_id.replace('post_', '').match(/^\d+$/)) {
            return res.status(400).json({ detail: "post_id must be in format 'post_001'" });
        }

        const postIdNum = parseInt(post_id.replace('post_', ''));
        const postData  = await qdrantClient.retrieve(COLLECTION_NAME, { ids: [postIdNum], with_vector: true });
        if (!postData?.length) return res.status(404).json({ detail: 'Post not found' });

        const hits = await qdrantClient.search(COLLECTION_NAME, {
            vector: postData[0].vector, limit: limit + 1, score_threshold: min_score
        });

        const results = hits
            .filter(r => r.payload.post_id !== post_id)
            .slice(0, limit)
            .map(r => ({
                post_id: r.payload.post_id, name: r.payload.name, caption: r.payload.caption,
                media_url: r.payload.media_url, media_type: r.payload.media_type,
                similarity_score: Math.round(r.score * 10000) / 10000,
                similarity_percentage: `${Math.round(r.score * 10000) / 100}%`
            }));

        res.json({ original_post: { post_id: postData[0].payload.post_id, name: postData[0].payload.name }, total_results: results.length, results });
    } catch (e) { res.status(500).json({ detail: e.message }); }
});

app.delete('/posts/:post_id', async (req, res) => {
    try {
        const { post_id } = req.params;
        if (!post_id.startsWith('post_') || !post_id.replace('post_', '').match(/^\d+$/)) {
            return res.status(400).json({ detail: "post_id must be in format 'post_001'" });
        }
        if (!(await Post.getPost(post_id))) return res.status(404).json({ detail: 'Post not found' });
        await Post.deletePost(post_id);
        await qdrantClient.delete(COLLECTION_NAME, { wait: true, points: [parseInt(post_id.replace('post_', ''))] });
        res.json({ message: 'Post deleted', post_id });
    } catch (e) { res.status(500).json({ detail: e.message }); }
});

app.get('/stats', async (req, res) => {
    try {
        const totalPosts = (await Post.getAllPosts()).length;
        const [ci, li] = await Promise.all([
            qdrantClient.getCollection(COLLECTION_NAME),
            qdrantClient.getCollection(LIKES_COLLECTION)
        ]);
        res.json({
            mongodb: { total_posts: totalPosts },
            qdrant:  { vectors: ci.points_count, dim: ci.config.params.vectors.size },
            likes:   { total: li.points_count },
        });
    } catch (e) { res.status(500).json({ detail: e.message }); }
});

const RAG_PROMPT = `You analyze social media posts.
Context:
{context}
Question: {question}
1. Model Answer: General knowledge answer.
2. Database Evidence: Evidence from posts above only.`;

app.post('/rag', async (req, res) => {
    try {
        const { question, limit = 5, min_score = 0.1 } = req.body;
        if (!question?.trim()) return res.status(400).json({ detail: 'Question required' });

        const qv = await getEmbedding(question);
        const hits = await qdrantClient.search(COLLECTION_NAME, { vector: qv, limit, score_threshold: min_score });

        if (!hits?.length) return res.json({ answer: 'No relevant posts found.', sources: [] });

        const blocks = [], sources = [];
        hits.forEach((h, i) => {
            const { caption = '', name = '', post_id = '' } = h.payload;
            if (caption) blocks.push(`Post ${i + 1} (${name}, ${post_id}):\n${caption}`);
            sources.push({ post_id, name, caption, media_url: h.payload.media_url || '', media_type: h.payload.media_type || 'image', similarity_score: Math.round(h.score * 10000) / 10000 });
        });

        const prompt = RAG_PROMPT.replace('{context}', blocks.join('\n\n') || 'None').replace('{question}', question);
        let answer;
        try { answer = await generateLLMAnswer(prompt); }
        catch { answer = `Posts found:\n${blocks.join('\n')}`; }

        res.json({ answer, sources });
    } catch (e) { res.status(500).json({ detail: e.message }); }
});

app.get('/health', async (req, res) => {
    const ok = async fn => { try { await fn(); return 'healthy'; } catch { return 'unhealthy'; } };
    const [mongodb, qdrant, embedding] = await Promise.all([
        ok(() => Post.getAllPosts()),
        ok(() => qdrantClient.getCollection(COLLECTION_NAME)),
        ok(() => axios.get(`${EMBEDDING_SERVICE_URL}/health`, { timeout: 3000 }))
    ]);
    const status = [mongodb, qdrant, embedding].every(s => s === 'healthy') ? 'healthy' : 'degraded';
    res.json({ status, services: { mongodb, qdrant, embedding } });
});

const PORT = process.env.PORT || 7860;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n${'═'.repeat(50)}`);
    console.log(` Post Similarity API — session-interest mode`);
    console.log(`${'═'.repeat(50)}`);
    console.log(` http://localhost:${PORT}`);
    console.log(` Debug: http://localhost:${PORT}/debug/likes/default_user`);
    console.log(`${'═'.repeat(50)}\n`);
});

module.exports = app;