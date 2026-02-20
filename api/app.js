const express = require("express");
const cors = require("cors");
const path = require("path");
const axios = require("axios");
const crypto = require("crypto");
require("dotenv").config();

const Post = require("../models/post");
const { QdrantClient } = require("@qdrant/js-client-rest");

const app = express();
const BASE_DIR = __dirname;
const FRONTEND_DIST = path.join(BASE_DIR, "..", "frontend", "dist");

app.use(express.json());
app.use(
  cors({
    origin: "*",
    credentials: true,
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["*"],
  }),
);
app.use("/assets", express.static(path.join(FRONTEND_DIST, "assets")));

const REQUIRED_ENV = ["QDRANT_URL", "QDRANT_API_KEY", "GROQ_API_KEY"];
const missingEnv = REQUIRED_ENV.filter((k) => !process.env[k]);
if (missingEnv.length > 0) {
  console.error("\nMissing env vars:", missingEnv.join(", "));
  process.exit(1);
}

const qdrantClient = new QdrantClient({
  url: process.env.QDRANT_URL,
  apiKey: process.env.QDRANT_API_KEY,
  checkCompatibility: false,
});
const { spawn } = require('child_process');

// Start embedding service if not already running
const embeddingProc = spawn('python', ['api/embedding_service.py'], {
  stdio: 'inherit',
  detached: false,
});
embeddingProc.on('error', (err) => console.error('Failed to start embedding service:', err));
process.on('exit', () => embeddingProc.kill());
const COLLECTION_NAME = "social_posts";
const LIKES_COLLECTION = "user_likes";
const EMBEDDING_SERVICE_URL =
  process.env.EMBEDDING_SERVICE_URL || "http://localhost:8001";

(async () => {
  try {
    const r = await axios.get(`${EMBEDDING_SERVICE_URL}/health`, {
      timeout: 5000,
    });
    console.log(`Embedding OK: ${r.data.model}`);
  } catch {
    console.error(`embedding unreachable at ${EMBEDDING_SERVICE_URL}`);
  }
  try {
    await qdrantClient.createCollection(LIKES_COLLECTION, {
      vectors: { size: 384, distance: "Cosine" },
    });
    console.log(`Created ${LIKES_COLLECTION}`);
  } catch {
    console.log(`  ${LIKES_COLLECTION} exists`);
  }
})();

// utilssss
async function getEmbedding(text) {
  try {
    const r = await axios.post(
      `${EMBEDDING_SERVICE_URL}/embed`,
      { text },
      { timeout: 10000 },
    );
    return r.data.embedding;
  } catch (e) {
    const conn = ["ECONNREFUSED", "ECONNRESET", "ENOTFOUND", "ETIMEDOUT"];
    if (conn.includes(e.code) || e.message?.includes("connect"))
      throw new Error(`Embedding unreachable (${e.code})`);
    throw new Error(`Embedding failed: ${e.message}`);
  }
}

async function generateLLMAnswer(prompt) {
  const r = await axios.post(
    "https://api.groq.com/openai/v1/chat/completions",
    {
      model: "llama-3.1-8b-instant",
      messages: [
        { role: "system", content: "You analyze social media posts." },
        { role: "user", content: prompt },
      ],
      temperature: 0.5,
      max_tokens: 800,
    },
    {
      headers: {
        Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
        "Content-Type": "application/json",
      },
      timeout: 30000,
    },
  );
  return r.data.choices[0].message.content.trim();
}

function shapePost(payload, score, source, meta = {}) {
  return {
    post_id: payload.post_id,
    name: payload.name,
    caption: payload.caption,
    media_url: payload.media_url || "",
    media_type: payload.media_type || "image",
    category: payload.category || "unknown",
    similarity_score: Math.round(score * 10000) / 10000,
    similarity_percentage:
      source === "random" ? "Random" : `${Math.round(score * 10000) / 100}%`,
    source,
    ...meta,
  };
}


const RANK_LABELS = [
  "primary",
  "secondary",
  "tertiary",
  "quaternary",
  "quinary",
  "senary",
  "septenary",
  "octonary",
];
const DECAY_LAMBDA = 0.05;

function likeWeight(timestamp, posInBucket, bucketSize) {
  const ageHours =
    (Date.now() - new Date(timestamp).getTime()) / (1000 * 60 * 60);
  const recency = Math.exp(-DECAY_LAMBDA * ageHours);
  const position = 1 - (posInBucket / Math.max(bucketSize, 1)) * 0.5;
  return recency * position;
}

// Build ranked interest buckets from session_like_events
function computeInterestRanking(likeEvents) {
  if (!likeEvents || likeEvents.length === 0) return [];

  const buckets = {};
  likeEvents.forEach((ev, idx) => {
    let key = (ev.category || "").toLowerCase().trim();
    if (!key || key === "unknown") key = `_anon_${ev.post_id}`;
    if (!buckets[key]) buckets[key] = { category: key, events: [] };
    buckets[key].events.push({ ...ev, seqIdx: idx });
  });

  const now = Date.now();
  const scored = Object.values(buckets).map((bucket) => {
    const n = bucket.events.length;
    let totalScore = 0;
    bucket.events.forEach((ev, posInBucket) => {
      totalScore += likeWeight(ev.timestamp, posInBucket, n);
    });
    return {
      category: bucket.category,
      events: bucket.events,
      post_ids: bucket.events.map((e) => e.post_id),
      count: n,
      score: Math.round(totalScore * 1000) / 1000,
      lastSeen: Math.max(
        ...bucket.events.map((e) => new Date(e.timestamp).getTime()),
      ),
    };
  });

  scored.sort((a, b) =>
    b.score !== a.score ? b.score - a.score : b.lastSeen - a.lastSeen,
  );

  return scored.map((bucket, idx) => ({
    category: bucket.category.startsWith("_anon_") ? "liked" : bucket.category,
    events: bucket.events,
    post_ids: bucket.post_ids,
    count: bucket.count,
    score: bucket.score,
    rank: RANK_LABELS[idx] || `rank_${idx + 1}`,
    rank_idx: idx,
  }));
}
// 10post schema 
function computeBudget(rankedInterests) {
  const RANDOM = 2;
  const MAX_INT = 3;
  const iSlots = Math.min(rankedInterests.length, MAX_INT);
  return { query: 10 - RANDOM - iSlots, interest: iSlots, random: RANDOM };
}

async function scrollAllPosts() {
  let all = [],
    offset = null;
  do {
    const r = await qdrantClient.scroll(COLLECTION_NAME, {
      limit: 250,
      offset,
      with_vector: false,
      with_payload: true,
    });
    all.push(...(r.points || []));
    offset = r.next_page_offset;
  } while (offset != null);
  return all;
}

function pickRandomPosts(allPosts, usedPostIds, count) {
  if (count <= 0) return [];
  const pool = allPosts.filter(
    (p) => p.payload?.post_id && !usedPostIds.has(p.payload.post_id),
  );
// shuffler
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, count).map((p) => {
    usedPostIds.add(p.payload.post_id);
    return shapePost(p.payload, 0, "random");
  });
}

async function buildInterestPosts(rankedInterests, usedPostIds, slotCount) {
  if (slotCount <= 0 || !rankedInterests.length) return [];
  const results = [];

  for (const interest of rankedInterests.slice(0, slotCount)) {
    console.log(
      `  [${interest.rank}] cat="${interest.category}" n=${interest.count} score=${interest.score}`,
    );

    const nums = interest.post_ids
      .map((pid) => parseInt(pid.replace("post_", "")))
      .filter((n) => !isNaN(n));

//vectrRetieveal
    let retrieved = [];
    try {
      retrieved = await qdrantClient.retrieve(COLLECTION_NAME, {
        ids: nums,
        with_vector: true,
        with_payload: false,
      });
    } catch (e) {
      console.log(`    retrieve failed: ${e.message}`);
    }

    const items = retrieved
      .map((r) => {
        if (!Array.isArray(r.vector) || !r.vector.length) return null;
        const postId = `post_${r.id}`;
        const evIdx = interest.events.findIndex((e) => e.post_id === postId);
        const weight =
          evIdx >= 0
            ? likeWeight(
                interest.events[evIdx].timestamp,
                evIdx,
                interest.events.length,
              )
            : 0.5;
        return { vector: r.vector, weight };
      })
      .filter(Boolean);

    if (!items.length) {
      console.log(`    no vectors — collapse`);
      results.push(null);
      continue;
    }



    const totalW = items.reduce((s, v) => s + v.weight, 0);
    const dim = items[0].vector.length;
    const centroid = new Array(dim).fill(0);
    items.forEach(({ vector, weight }) => {
      vector.forEach((val, i) => {
        centroid[i] += val * (weight / totalW);
      });
    });

    // relvance search — skipe used n liked post
    let hits = [];
    try {
      hits = await qdrantClient.search(COLLECTION_NAME, {
        vector: centroid,
        limit: 100,
        score_threshold: 0.0,
      });
    } catch (e) {
      console.log(`    centroid search failed: ${e.message}`);
      results.push(null);
      continue;
    }

    let filled = false;
    for (const hit of hits) {
      const pid = hit.payload?.post_id;
      if (!pid || usedPostIds.has(pid) || interest.post_ids.includes(pid))
        continue;
      usedPostIds.add(pid);
      results.push(
        shapePost(hit.payload, hit.score, "interest", {
          interest_rank: interest.rank,
          interest_rank_idx: interest.rank_idx,
          interest_category: interest.category,
          interest_count: interest.count,
          interest_score: interest.score,
        }),
      );
      console.log(`picked ${pid} score=${hit.score.toFixed(4)}`);
      filled = true;
      break;
    }
    if (!filled) {
      console.log(`no post — collapse to query`);
      results.push(null);
    }
  }
  return results;
}

async function buildQueryPosts(
  queryEmbedding,
  usedPostIds,
  needed,
  minScore = 0.0,
) {
  if (needed <= 0) return [];
  let hits = [];
  try {
    hits = await qdrantClient.search(COLLECTION_NAME, {
      vector: queryEmbedding,
      limit: needed + 100,
      score_threshold: minScore,
    });
  } catch (e) {
    console.error("Query search failed:", e.message);
    return [];
  }
  const posts = [];
  for (const r of hits) {
    if (posts.length >= needed) break;
    const pid = r.payload?.post_id;
    if (!pid || usedPostIds.has(pid)) continue;
    posts.push(shapePost(r.payload, r.score, "query"));
    usedPostIds.add(pid);
  }
  return posts;
}

// postjumbleness 
function assembleFeed(queryPosts, interestPosts, randomPosts) {
  const base = [...queryPosts];
  const anchors = [2, 4, 6];
  interestPosts.forEach((ip, idx) => {
    const pos = anchors[idx] !== undefined ? anchors[idx] : idx * 2 + 2;
    base.splice(Math.min(pos, base.length), 0, ip);
  });
  const result = [...base];
  const total = result.length + randomPosts.length;
  randomPosts.forEach((rp, i) => {
    const pos = Math.floor(((i + 1) / (randomPosts.length + 1)) * total);
    result.splice(Math.min(pos, result.length), 0, rp);
  });
  return result;
}

// prompt and template for ai 
const RAG_SYSTEM_PROMPT = `You are an intelligent AI assistant specialized in analyzing social media posts and providing insightful answers. 

BEHAVIOR GUIDELINES:
1. For KEY INSIGHTS: Ground your analysis in the provided context (social media posts)
   - Extract key insights directly from source posts
   - Reference post authors and content
   - Cite specific data points from sources
   
2. For AI PERSPECTIVE: Provide INDEPENDENT analytical viewpoint
   - Do NOT repeat or summarize source data
   - Do NOT cite the provided posts
   - Focus solely on the query topic itself
   - Offer your own reasoning about the query
   - Discuss implications, risks, opportunities based on the query topic
   - Challenge or expand on the topic from fresh angles
   
3. Maintain professional yet conversational tone
4. Be honest about limitations
5. Clearly separate source-based insights from independent perspective`;

const RAG_ANALYSIS_PROMPT = (question, contextBlocks, sourceData) => `
TASK: Analyze the following social media posts and provide TWO different types of answers to the user's query.

USER QUERY: "${question}"

CONTEXT POSTS (for KEY INSIGHTS ONLY):
${contextBlocks.join("\n---\n")}

RESPONSE REQUIREMENTS:
You must provide your response in JSON format with the following structure:
{
  "key_insights": [
    {"point": "insight statement", "post_reference": "post_id or author name", "explanation": "explanation grounded in source data"},
    ... (exactly 5 points)
  ],
  "ai_perspective": "Write a comprehensive 6-line paragraph expressing YOUR INDEPENDENT perspective and analysis on the query topic itself. Do NOT reference the provided posts. Do NOT summarize source data. Instead, analyze the query topic from your own reasoning and provide insights that stand alone.",
  "summary": "2-3 sentence executive summary of findings"
}

IMPORTANT DISTINCTION:

KEY INSIGHTS (Based on provided posts):
- Must be grounded in the source posts provided
- Frame using: "According to the posts...", "The data suggests...", "Based on analysis..."
- Always reference the source post or author
- Extract specific information from the posts
- Make connections between multiple sources when relevant

AI PERSPECTIVE (Independent Analysis):
- Do NOT look at or reference the provided posts
- Analyze the QUERY TOPIC itself
- Provide your own reasoning about the topic
- Discuss implications, risks, benefits of the topic
- Challenge assumptions in the query
- Offer forward-thinking analysis
- Example: If query is "Is pizza and coke a deadly combo?"
  → Your perspective discusses nutrition science, body chemistry, health impacts
  → NOT what social media posts said about pizza and coke
  → Your own independent analysis of why/why not it's dangerous

GUIDELINES FOR KEY INSIGHTS:
- Each insight must be distinct and add unique value
- Extract from source posts only
- Always reference the source post or author
- Make connections between multiple sources when relevant
- Use data-grounded framing

GUIDELINES FOR AI PERSPECTIVE:
- Write in first person
- Discuss the query topic deeply from your analytical viewpoint
- Do NOT cite or reference the provided posts at all
- Offer independent reasoning and expert analysis
- Include 2-3 substantive points about the topic
- Express appropriate uncertainty where relevant
- Make this completely independent from key_insights

Format your response ONLY as valid JSON, no additional text.`;

async function generateStructuredRAGAnswer(question, contextBlocks, sourceData) {
  try {
    const prompt = RAG_ANALYSIS_PROMPT(question, contextBlocks, sourceData);
    
    const response = await axios.post(
      "https://api.groq.com/openai/v1/chat/completions",
      {
        model: "llama-3.1-8b-instant",
        messages: [
          { 
            role: "system", 
            content: RAG_SYSTEM_PROMPT 
          },
          { 
            role: "user", 
            content: prompt 
          },
        ],
        temperature: 0.7,
        max_tokens: 1000,
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
          "Content-Type": "application/json",
        },
        timeout: 30000,
      },
    );

    const content = response.data.choices[0].message.content.trim();
    
    // Parse JSON response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error("Invalid JSON response from LLM");
    }
    
    return JSON.parse(jsonMatch[0]);
  } catch (error) {
    console.error("Error generating structured RAG answer:", error.message);
    throw error;
  }
}

app.post("/rag", async (req, res) => {
  try {
    const { question, limit = 5, min_score = 0.1, user_id = "default_user" } = req.body;
    
    if (!question?.trim()) {
      return res.status(400).json({ detail: "Question required" });
    }

    console.log(`\n${"═".repeat(60)}`);
    console.log(`RAG REQUEST: "${question}" | user=${user_id} | limit=${limit}`);

    // Step 1: Get embeddings for the question
    const questionEmbedding = await getEmbedding(question);

    // Step 2: Search for relevant posts
    const hits = await qdrantClient.search(COLLECTION_NAME, {
      vector: questionEmbedding,
      limit: Math.max(limit, 5),
      score_threshold: min_score,
    });

    if (!hits?.length) {
      return res.json({
        query: question,
        status: "no_relevant_content",
        answer: "I apologize, but I couldn't find relevant posts to answer your question. Please try a different search term.",
        key_insights: [],
        ai_perspective: "The current database doesn't contain sufficient information to provide a meaningful analysis.",
        featured_image: null,
        source_posts: [],
      });
    }

    // Step 3: Prepare context blocks and source data
    const contextBlocks = [];
    const sourceData = [];
    const allSourcePosts = [];

    hits.forEach((hit, index) => {
      const { 
        caption = "", 
        name = "", 
        post_id = "",
        media_url = "",
        media_type = "image",
        category = "unknown"
      } = hit.payload;

      // Build context for LLM
      const contextBlock = `[Post ${index + 1}] Author: ${name} | Category: ${category}\nContent: ${caption}`;
      contextBlocks.push(contextBlock);

      // Store source data for reference
      sourceData.push({
        post_id,
        name,
        caption,
        media_url,
        media_type,
        category,
        similarity_score: Math.round(hit.score * 10000) / 10000,
        similarity_percentage: `${Math.round(hit.score * 10000) / 100}%`,
      });

      // Add to all posts (we'll select first as featured, rest for bottom)
      allSourcePosts.push({
        post_id,
        name,
        caption,
        media_url,
        media_type,
        category,
        similarity_score: Math.round(hit.score * 10000) / 10000,
      });
    });

    // Step 4: Generate structured answer using LLM with system prompt
    let analysisResult;
    try {
      analysisResult = await generateStructuredRAGAnswer(question, contextBlocks, sourceData);
      console.log(`RAG Analysis generated successfully`);
    } catch (error) {
      console.error("Failed to generate structured analysis:", error.message);
      // Fallback response
      analysisResult = {
        key_insights: contextBlocks.slice(0, 5).map((block, i) => ({
          point: `Post insight ${i + 1}`,
          post_reference: sourceData[i]?.name || "Unknown",
          explanation: sourceData[i]?.caption || block,
        })),
        ai_perspective: "The provided posts contain relevant information, but I encountered a limitation in generating a detailed perspective. Please review the source posts directly for comprehensive analysis.",
        summary: "Analysis based on relevant social media posts.",
      };
    }
    const featuredImage = allSourcePosts[0]?.media_url || null;
    const sourcePosts = allSourcePosts.slice(0, 5).map((post) => ({
      post_id: post.post_id,
      name: post.name,
      caption: post.caption,
      media_url: post.media_url,
      media_type: post.media_type,
      category: post.category,
      similarity_score: post.similarity_score,
    }));

    const response = {
      query: question,
      user_id,
      status: "success",
      timestamp: new Date().toISOString(),

      summary: analysisResult.summary || "Analysis complete",

      featured_image: {
        url: featuredImage,
        source: allSourcePosts[0]?.name || "Top result",
        post_id: allSourcePosts[0]?.post_id || "",
      },
      key_insights: analysisResult.key_insights?.slice(0, 5).map((insight, idx) => ({
        rank: idx + 1,
        point: insight.point || insight.explanation,
        post_reference: insight.post_reference,
        explanation: insight.explanation,
        source_post: sourceData[idx] || null,
      })) || [],

      ai_perspective: analysisResult.ai_perspective || "Unable to generate perspective",
      source_posts: sourcePosts,
      metadata: {
        total_relevant_posts: hits.length,
        posts_analyzed: contextBlocks.length,
        min_similarity_score: min_score,
        top_similarity: sourceData[0]?.similarity_score || 0,
      },
    };

    console.log(`RAG RESPONSE: ${response.key_insights.length} insights | ${sourcePosts.length} posts`);
    console.log(`${"═".repeat(60)}\n`);

    res.json(response);
  } catch (error) {
    console.error("RAG error:", error.message);
    res.status(500).json({ 
      detail: error.message,
      hint: "Check that GROQ_API_KEY and Qdrant connection are properly configured"
    });
  }
});

// routes handler
app.get("/api", (req, res) =>
  res.json({ message: "Smart Ranking API", status: "running" }),
);
app.get("/", (req, res) =>
  res.sendFile(path.join(FRONTEND_DIST, "index.html")),
);

app.get("/random", async (req, res) => {
  try {
    const count = Math.min(parseInt(req.query.count) || 12, 50);
    const all = await scrollAllPosts();
    for (let i = all.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [all[i], all[j]] = [all[j], all[i]];
    }
    res.json({
      total: count,
      posts: all.slice(0, count).map((p) => ({
        post_id: p.payload.post_id,
        name: p.payload.name,
        caption: p.payload.caption,
        media_url: p.payload.media_url || "",
        media_type: p.payload.media_type || "image",
        category: p.payload.category || "unknown",
      })),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

app.get("/posts", async (req, res) => {
  try {
    const posts = await Post.getAllPosts();
    posts.forEach((p) => {
      p._id = p._id.toString();
      p.created_at = p.created_at.toISOString();
    });
    res.json({ total: posts.length, posts });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});
app.get("/posts/:post_id", async (req, res) => {
  try {
    const post = await Post.getPost(req.params.post_id);
    if (!post) return res.status(404).json({ detail: "Post not found" });
    post._id = post._id.toString();
    post.created_at = post.created_at.toISOString();
    res.json(post);
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});
app.post("/posts", async (req, res) => {
  try {
    const {
      post_id,
      name,
      caption,
      media_url,
      media_type = "image",
      category = "unknown",
    } = req.body;
    if (
      !post_id.startsWith("post_") ||
      !post_id.replace("post_", "").match(/^\d+$/)
    )
      return res
        .status(400)
        .json({ detail: "post_id must be in format 'post_001'" });
    if (await Post.getPost(post_id))
      return res.status(400).json({ detail: "Post already exists" });
    await Post.createPost({ post_id, name, caption, media_url, media_type });
    const embedding = await getEmbedding(`${name}: ${caption}`);
    const postIdNum = parseInt(post_id.replace("post_", ""));
    await qdrantClient.upsert(COLLECTION_NAME, {
      wait: true,
      points: [
        {
          id: postIdNum,
          vector: embedding,
          payload: {
            post_id,
            name,
            caption,
            media_url,
            media_type,
            category,
            created_at: new Date().toISOString(),
          },
        },
      ],
    });
    res.status(201).json({ message: "Post created", post_id });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// like handler 
app.post("/like", async (req, res) => {
  try {
    const { post_id, user_id = "default_user" } = req.body;
    if (
      !post_id.startsWith("post_") ||
      !post_id.replace("post_", "").match(/^\d+$/)
    )
      return res
        .status(400)
        .json({ detail: "post_id must be in format 'post_001'" });
    const postIdNum = parseInt(post_id.replace("post_", ""));
    const postData = await qdrantClient.retrieve(COLLECTION_NAME, {
      ids: [postIdNum],
      with_vector: true,
    });
    if (!postData?.length)
      return res.status(404).json({ detail: "Post not found" });
    const category = postData[0].payload.category || "unknown";
    const liked_at = new Date().toISOString();
    const likeId = parseInt(
      crypto
        .createHash("md5")
        .update(`${user_id}_${post_id}_${liked_at}`)
        .digest("hex")
        .substring(0, 8),
      16,
    );
    await qdrantClient.upsert(LIKES_COLLECTION, {
      wait: true,
      points: [
        {
          id: likeId,
          vector: postData[0].vector,
          payload: {
            user_id,
            post_id,
            category,
            name: postData[0].payload.name,
            caption: postData[0].payload.caption,
            media_url: postData[0].payload.media_url || "",
            liked_at,
          },
        },
      ],
    });
    console.log(`  /like: ${post_id} cat="${category}" user=${user_id}`);
    res.json({ message: "Post liked", post_id, user_id, category, liked_at });
  } catch (e) {
    console.error("Like error:", e);
    res.status(500).json({ detail: e.message });
  }
});

app.get("/likes/:user_id", async (req, res) => {
  try {
    try {
      await qdrantClient.getCollection(LIKES_COLLECTION);
    } catch {
      return res.json({
        user_id: req.params.user_id,
        total_likes: 0,
        liked_posts: [],
      });
    }
    const result = await qdrantClient.scroll(LIKES_COLLECTION, {
      filter: {
        must: [{ key: "user_id", match: { value: req.params.user_id } }],
      },
      limit: 500,
      with_vector: false,
      with_payload: true,
    });
    const liked_posts = (result?.points || [])
      .map((pt) => ({
        post_id: pt.payload.post_id || "",
        name: pt.payload.name || "",
        caption: pt.payload.caption || "",
        media_url: pt.payload.media_url || "",
        category: pt.payload.category || "unknown",
        liked_at: pt.payload.liked_at || new Date(0).toISOString(),
      }))
      .sort((a, b) => new Date(a.liked_at) - new Date(b.liked_at));
    res.json({
      user_id: req.params.user_id,
      total_likes: liked_posts.length,
      liked_posts,
    });
  } catch (e) {
    res.json({ user_id: req.params.user_id, total_likes: 0, liked_posts: [] });
  }
});
// mainSearch handlere
app.post("/search", async (req, res) => {
  try {
    const {
      query,
      min_score = 0.0,
      user_id = "default_user",
      session_like_events = [],
    } = req.body;
    if (!query?.trim())
      return res.status(400).json({ detail: "Query cannot be empty" });

    // Computingg interest ranking fresh on every search
    const rankedInterests = computeInterestRanking(session_like_events);
    const budget = computeBudget(rankedInterests);

    console.log(`\n${"═".repeat(60)}`);
    console.log(`SEARCH: "${query}" | events=${session_like_events.length}`);
    console.log(
      `RANKING: ${rankedInterests.map((r) => `${r.rank}=${r.category}(n=${r.count},s=${r.score})`).join(" > ") || "none"}`,
    );
    console.log(
      `BUDGET: q=${budget.query} i=${budget.interest} r=${budget.random}`,
    );

    const queryEmbedding = await getEmbedding(query);
    const usedPostIds = new Set();
    const allPosts = await scrollAllPosts();
    const randomPosts = pickRandomPosts(allPosts, usedPostIds, budget.random);
    console.log(`RANDOMS: [${randomPosts.map((p) => p.post_id).join(", ")}]`);

    const rawInterest = await buildInterestPosts(
      rankedInterests,
      usedPostIds,
      budget.interest,
    );
    const interestPosts = rawInterest.filter((s) => s !== null);
    const collapsed = rawInterest.filter((s) => s === null).length;
    console.log(
      `INTEREST: [${interestPosts.map((p) => `${p.post_id}[${p.interest_rank}]`).join(", ") || "none"}]`,
    );
    const queryNeeded = budget.query + collapsed;
    const queryPosts = await buildQueryPosts(
      queryEmbedding,
      usedPostIds,
      queryNeeded,
      min_score,
    );
    console.log(`QUERY: [${queryPosts.map((p) => p.post_id).join(", ")}]`);

    let feed = assembleFeed(queryPosts, interestPosts, randomPosts);

    if (feed.length < 10) {
      const still = 10 - feed.length;
      console.log(`  Padding ${still} more query results to reach 10`);
      const pad = await buildQueryPosts(
        queryEmbedding,
        usedPostIds,
        still,
        0.0,
      );
      if (pad.length < still) {
        const lastResort = pickRandomPosts(
          allPosts,
          usedPostIds,
          still - pad.length,
        );
        feed = [...feed, ...pad, ...lastResort];
      } else {
        feed = [...feed, ...pad];
      }
    }

    const seenFinal = new Set();
    feed = feed
      .filter((p) => {
        if (seenFinal.has(p.post_id)) return false;
        seenFinal.add(p.post_id);
        return true;
      })
      .slice(0, 10);

    const breakdown = {
      total: feed.length,
      query_based: feed.filter((r) => r.source === "query").length,
      interest_based: feed.filter((r) => r.source === "interest").length,
      random: feed.filter((r) => r.source === "random").length,
      budget,
      ranked_interests: rankedInterests,
    };

    console.log(
      `FINAL (${feed.length}): q=${breakdown.query_based} i=${breakdown.interest_based} r=${breakdown.random}`,
    );
    res.json({
      query,
      user_id,
      total_results: feed.length,
      breakdown,
      results: feed,
    });
  } catch (e) {
    console.error("Search error:", e);
    res.status(500).json({ detail: e.message });
  }
});

app.get("/similar/:post_id", async (req, res) => {
  try {
    const { post_id } = req.params;
    const limit = parseInt(req.query.limit) || 5,
      min_score = parseFloat(req.query.min_score) || 0.0;
    if (
      !post_id.startsWith("post_") ||
      !post_id.replace("post_", "").match(/^\d+$/)
    )
      return res
        .status(400)
        .json({ detail: "post_id must be in format 'post_001'" });
    const pid = parseInt(post_id.replace("post_", ""));
    const pd = await qdrantClient.retrieve(COLLECTION_NAME, {
      ids: [pid],
      with_vector: true,
    });
    if (!pd?.length) return res.status(404).json({ detail: "Post not found" });
    const hits = await qdrantClient.search(COLLECTION_NAME, {
      vector: pd[0].vector,
      limit: limit + 1,
      score_threshold: min_score,
    });
    const results = hits
      .filter((r) => r.payload.post_id !== post_id)
      .slice(0, limit)
      .map((r) => ({
        post_id: r.payload.post_id,
        name: r.payload.name,
        caption: r.payload.caption,
        media_url: r.payload.media_url,
        media_type: r.payload.media_type,
        similarity_score: Math.round(r.score * 10000) / 10000,
        similarity_percentage: `${Math.round(r.score * 10000) / 100}%`,
      }));
    res.json({
      original_post: {
        post_id: pd[0].payload.post_id,
        name: pd[0].payload.name,
      },
      total_results: results.length,
      results,
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

app.delete("/posts/:post_id", async (req, res) => {
  try {
    const { post_id } = req.params;
    if (
      !post_id.startsWith("post_") ||
      !post_id.replace("post_", "").match(/^\d+$/)
    )
      return res
        .status(400)
        .json({ detail: "post_id must be in format 'post_001'" });
    if (!(await Post.getPost(post_id)))
      return res.status(404).json({ detail: "Post not found" });
    await Post.deletePost(post_id);
    await qdrantClient.delete(COLLECTION_NAME, {
      wait: true,
      points: [parseInt(post_id.replace("post_", ""))],
    });
    res.json({ message: "Post deleted", post_id });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

app.get("/stats", async (req, res) => {
  try {
    const tp = (await Post.getAllPosts()).length;
    const [ci, li] = await Promise.all([
      qdrantClient.getCollection(COLLECTION_NAME),
      qdrantClient.getCollection(LIKES_COLLECTION),
    ]);
    res.json({
      mongodb: { total_posts: tp },
      qdrant: { vectors: ci.points_count, dim: ci.config.params.vectors.size },
      likes: { total: li.points_count },
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

app.get("/health", async (req, res) => {
  const ok = async (fn) => {
    try {
      await fn();
      return "healthy";
    } catch {
      return "unhealthy";
    }
  };
  const [m, q, e] = await Promise.all([
    ok(() => Post.getAllPosts()),
    ok(() => qdrantClient.getCollection(COLLECTION_NAME)),
    ok(() => axios.get(`${EMBEDDING_SERVICE_URL}/health`, { timeout: 3000 })),
  ]);
  res.json({
    status: [m, q, e].every((s) => s === "healthy") ? "healthy" : "degraded",
    services: { mongodb: m, qdrant: q, embedding: e },
  });
});

app.get("/debug/likes/:user_id", async (req, res) => {
  try {
    const r = await qdrantClient.scroll(LIKES_COLLECTION, {
      filter: {
        must: [{ key: "user_id", match: { value: req.params.user_id } }],
      },
      limit: 200,
      with_vector: false,
      with_payload: true,
    });
    const pts = (r?.points || []).sort(
      (a, b) => new Date(a.payload.liked_at) - new Date(b.payload.liked_at),
    );
    res.json({
      total: pts.length,
      points: pts.map((p) => ({
        post_id: p.payload.post_id,
        category: p.payload.category,
        liked_at: p.payload.liked_at,
      })),
    });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

app.post("/debug/ranking", (req, res) => {
  const { session_like_events = [] } = req.body;
  const ranked = computeInterestRanking(session_like_events);
  const budget = computeBudget(ranked);
  res.json({
    event_count: session_like_events.length,
    ranked_interests: ranked,
    budget,
  });
});

const PORT = process.env.PORT || 7860;
app.listen(PORT, "0.0.0.0", () => {
  console.log(
    `\n${"═".repeat(50)}\n Smart Ranking API — http://localhost:${PORT}\n${"═".repeat(50)}\n`,
  );
});
module.exports = app;