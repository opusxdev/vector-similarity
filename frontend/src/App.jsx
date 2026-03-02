import React, { useState, useEffect, useRef } from "react";
import { Heart } from "lucide-react";

function CategorySelector({ categories, onApply, onSkip }) {
  const [selected, setSelected] = useState([]);
  const handleSelect = (cat) => {
    setSelected((prev) =>
      prev.includes(cat)
        ? prev.filter((c) => c !== cat)
        : prev.length < 3
        ? [...prev, cat]
        : prev
    );
  };
  return (
    <div style={{
      background: '#0a0a0a',
      border: '1px solid #1a1a1a',
      borderRadius: 12,
      padding: '40px 32px',
      maxWidth: 500,
      margin: '40px auto',
      boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6)',
      textAlign: 'center',
      animation: 'fadeInUp 0.6s ease-out'
    }}>
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(15px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      <h2 style={{ 
        fontSize: '28px',
        fontWeight: 400,
        marginBottom: '8px',
        background: 'linear-gradient(to bottom,#10775f,#139c77,#33b89b)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        letterSpacing: '-0.5px'
      }}>Select Interests</h2>
      <p style={{ 
        color: '#666', 
        fontSize: '13px', 
        marginBottom: 32,
        lineHeight: '1.5'
      }}>The algorithm needs a starting point. Choose 3 categories to begin your personalized feed.</p>
      
      <div style={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 8, 
        justifyContent: 'center', 
        marginBottom: 36 
      }}>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => handleSelect(cat)}
            style={{
              background: selected.includes(cat) ? '#33b89b' : '#111',
              color: selected.includes(cat) ? '#000' : '#888',
              border: '1px solid',
              borderColor: selected.includes(cat) ? '#33b89b' : '#222',
              borderRadius: 6,
              padding: '7px 14px',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '12px',
              transition: 'all 0.2s ease',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            {cat}
          </button>
        ))}
      </div>
      
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
        <button
          onClick={() => onApply(selected)}
          disabled={selected.length !== 3}
          style={{
            background: selected.length === 3 ? '#fff' : '#1a1a1a',
            color: selected.length === 3 ? '#000' : '#444',
            border: 'none',
            borderRadius: 8,
            padding: '12px 32px',
            fontWeight: 700,
            fontSize: '14px',
            cursor: selected.length === 3 ? 'pointer' : 'not-allowed',
            transition: 'all 0.3s ease',
            flex: 1,
            textTransform: 'uppercase'
          }}
        >Initialize Feed</button>
        <button
          onClick={onSkip}
          style={{
            background: 'transparent',
            color: '#444',
            border: '1px solid #222',
            borderRadius: 8,
            padding: '12px 24px',
            fontWeight: 600,
            fontSize: '14px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            textTransform: 'uppercase'
          }}
          onMouseOver={(e) => e.target.style.color = '#fff'}
          onMouseOut={(e) => e.target.style.color = '#444'}
        >Skip</button>
      </div>
    </div>
  );
}

// List of all categories
const ALL_CATEGORIES = [
  'nature', 'tech', 'healthcare', 'food', 'art', 'education', 'travel', 'music', 'sports', 'ai', 'web3', 'socialmedia', 'finance', 'movies', 'stocks', 'vehicles', 'cafes'
];

const API_BASE = "http://localhost:7860";
const USER_ID = "default_user";

const SOURCE_BADGE = {
  query: { bg: "#1a4d2e", color: "#4ade80", text: "Query Match" },
  interest: { bg: "#1e3a8a", color: "#60a5fa", text: "For You" },
  random: { bg: "#4c1d95", color: "#a78bfa", text: "Discover" },
};
const RANK_COLOR = {
  primary: "#f59e0b",
  secondary: "#60a5fa",
  tertiary: "#a78bfa",
  quaternary: "#34d399",
  quinary: "#f472b6",
  senary: "#38bdf8",
  septenary: "#fb923c",
  octonary: "#4ade80",
};
const CATEGORY_COLOR = {
  tech: "#3b82f6",
  ai: "#8b5cf6",
  healthcare: "#10b981",
  web3: "#f59e0b",
  socialmedia: "#ec4899",
  food: "#f97316",
  sports: "#06b6d4",
  finance: "#84cc16",
  movies: "#ef4444",
  music: "#a855f7",
  education: "#14b8a6",
  travel: "#6366f1",
  art: "#f43f5e",
  nature: "#22c55e",
  unknown: "#6b7280",
  liked: "#f59e0b",
  stocks: "#84cc16",
  crypto: "#f59e0b",
};
const getCatColor = (c) => CATEGORY_COLOR[c?.toLowerCase()] || "#6b7280";
const getBadge = (s) => SOURCE_BADGE[s] || SOURCE_BADGE.query;

const BENTO_PATTERN = [
  { col: 1, row: 2 },
  { col: 2, row: 1 },
  { col: 1, row: 1 },
  { col: 1, row: 1 },
  { col: 1, row: 1 },
  { col: 2, row: 2 },
  { col: 1, row: 1 },
  { col: 1, row: 2 },
  { col: 2, row: 1 },
  { col: 1, row: 1 },
  { col: 1, row: 1 },
  { col: 2, row: 1 },
];

function BentoCard({ post, span, visible, animDelay }) {
  const cc = getCatColor(post.category),
    isBig = span.col === 2 && span.row === 2,
    isWide = span.col === 2 && span.row === 1;
  return (
    <div
      style={{
        gridColumn: `span ${span.col}`,
        gridRow: `span ${span.row}`,
        background: post.media_url
          ? `#0e0e0e url("${post.media_url}") center/cover no-repeat`
          : "#0e0e0e",
        border: "1px solid #1e1e1e",
        borderRadius: "10px",
        overflow: "hidden",
        position: "relative",
        opacity: visible ? 1 : 0,
        transform: visible ? "scale(1)" : "scale(0.95)",
        transition: `opacity 0.45s ease ${animDelay}ms, transform 0.45s ease ${animDelay}ms`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 1,
          background: post.media_url
            ? "linear-gradient(to bottom,transparent 20%,rgba(0,0,0,.55) 60%,rgba(0,0,0,.92) 100%)"
            : "linear-gradient(to bottom,#111 0%,#0a0a0a 100%)",
        }}
      />
      <div
        style={{
          padding: isBig ? "11px 12px" : isWide ? "8px 10px" : "7px 9px",
          position: "relative",
          zIndex: 2,
        }}
      >
        {post.category && post.category !== "unknown" && (
          <div
            style={{
              display: "inline-block",
              background: cc + "28",
              color: cc,
              fontSize: "8px",
              fontWeight: 800,
              letterSpacing: "0.6px",
              padding: "2px 6px",
              borderRadius: "4px",
              marginBottom: "4px",
              textTransform: "uppercase",
            }}
          >
            {post.category}
          </div>
        )}
        <div
          style={{
            fontWeight: 700,
            fontSize: isBig ? "12px" : "11px",
            color: "#f0f0f0",
            lineHeight: 1.3,
            marginBottom: "3px",
            overflow: "hidden",
            display: "-webkit-box",
            WebkitLineClamp: isBig ? 2 : 1,
            WebkitBoxOrient: "vertical",
          }}
        >
          {post.name}
        </div>
        <div
          style={{
            fontSize: "9px",
            color: post.media_url ? "rgba(255,255,255,.55)" : "#555",
            lineHeight: 1.35,
            overflow: "hidden",
            display: "-webkit-box",
            WebkitLineClamp: isBig ? 3 : 2,
            WebkitBoxOrient: "vertical",
          }}
        >
          {post.caption}
        </div>
      </div>
    </div>
  );
}

function BentoGrid({ posts, visible }) {
  const [cv, setCv] = useState(false);
  useEffect(() => {
    if (posts.length > 0) {
      const t = setTimeout(() => setCv(true), 80);
      return () => clearTimeout(t);
    }
  }, [posts]);
  if (!posts.length)
    return (
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4,1fr)",
          gridAutoRows: "60px",
          gap: "5px",
          marginBottom: "28px",
        }}
      >
        {BENTO_PATTERN.map((s, i) => (
          <div
            key={i}
            style={{
              gridColumn: `span ${s.col}`,
              gridRow: `span ${s.row}`,
              background: "#0e0e0e",
              borderRadius: "10px",
              animation: `pulse 1.8s ease-in-out ${i * 60}ms infinite`,
            }}
          />
        ))}
        <style>{`@keyframes pulse{0%,100%{opacity:.25}50%{opacity:.5}}`}</style>
      </div>
    );
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4,1fr)",
        gridAutoRows: "60px",
        gap: "5px",
        marginBottom: "28px",
        opacity: visible ? 1 : 0,
        transform: visible ? "none" : "translateY(8px)",
        transition: "opacity .5s ease,transform .5s ease",
      }}
    >
      {posts.slice(0, 12).map((p, i) => (
        <BentoCard
          key={p.post_id}
          post={p}
          span={BENTO_PATTERN[i] || { col: 1, row: 1 }}
          visible={cv}
          animDelay={i * 35}
        />
      ))}
    </div>
  );
}

function InterestPills({ rankedInterests }) {
  if (!rankedInterests?.length) return null;
  return (
    <div
      style={{
        display: "flex",
        gap: "6px",
        flexWrap: "wrap",
        marginBottom: "16px",
        alignItems: "center",
      }}
    >
      <span
        style={{
          fontSize: "9px",
          color: "#444",
          letterSpacing: "1px",
          textTransform: "uppercase",
          marginRight: "2px",
        }}
      >
        Your interests
      </span>
      {rankedInterests.map((r) => {
        const rc = RANK_COLOR[r.rank] || "#6b7280",
          cc = getCatColor(r.category);
        return (
          <div
            key={r.rank}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "4px",
              background: rc + "12",
              border: `1px solid ${rc}33`,
              borderRadius: "20px",
              padding: "3px 9px",
            }}
          >
            <span
              style={{
                fontSize: "8px",
                color: rc,
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: "0.4px",
              }}
            >
              {r.rank}
            </span>
            <span style={{ fontSize: "9px", color: cc, fontWeight: 700 }}>
              {r.category}
            </span>
            <span style={{ fontSize: "8px", color: "#555" }}>{r.count}♥</span>
          </div>
        );
      })}
    </div>
  );
}

// rag component 
function RAGResponse({ data, loading }) {
  if (!data && !loading) return null;

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: "40px" }}>
        <div
          style={{
            display: "inline-block",
            width: "24px",
            height: "24px",
            border: "2px solid #222",
            borderTopColor: "#fff",
            borderRadius: "50%",
            animation: "spin .8s linear infinite",
          }}
        />
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div
      style={{
        background: "#0a0a0a",
        border: "1px solid #1a1a1a",
        borderRadius: "12px",
        padding: "24px",
        marginBottom: "28px",
      }}
    >
{/* img loader for rag */}
      {data.featured_image?.url && (
        <div style={{ marginBottom: "24px" }}>
          <img
            src={data.featured_image.url}
            alt="Featured"
            style={{
              width: "100%",
              height: "auto",
              maxHeight: "300px",
              objectFit: "cover",
              borderRadius: "10px",
              marginBottom: "8px",
            }}
            onError={(e) => {
              e.target.style.display = "none";
            }}
          />
          <div style={{ fontSize: "11px", color: "#666" }}>
            From: <strong>{data.featured_image.source}</strong>
          </div>
        </div>
      )}

{/* summary  */}
      {data.summary && (
        <div style={{ marginBottom: "24px" }}>
          <h4 style={{ marginBottom: "10px", fontSize: "14px", color: "#aaa" }}>
            Summary
          </h4>
          <p
            style={{
              margin: 0,
              color: "#ccc",
              lineHeight: "1.6",
              fontSize: "13px",
            }}
          >
            {data.summary}
          </p>
        </div>
      )}
      {data.key_insights && data.key_insights.length > 0 && (
        <div style={{ marginBottom: "24px" }}>
          <h4 style={{ marginBottom: "14px", fontSize: "14px", color: "#aaa" }}>
            Key Insights ({data.key_insights.length})
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {data.key_insights.map((insight, idx) => (
              <div
                key={idx}
                style={{
                  background: "#111",
                  padding: "14px",
                  borderRadius: "8px",
                  border: "1px solid #1a1a1a",
                }}
              >
                <div style={{ display: "flex", gap: "10px" }}>
                  <div
                    style={{
                      background: "#60a5fa",
                      color: "#000",
                      width: "24px",
                      height: "24px",
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontWeight: 700,
                      fontSize: "12px",
                      flexShrink: 0,
                    }}
                  >
                    {insight.rank}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div
                      style={{
                        fontWeight: 600,
                        fontSize: "13px",
                        marginBottom: "6px",
                        color: "#fff",
                      }}
                    >
                      {insight.point}
                    </div>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#aaa",
                        lineHeight: "1.5",
                        marginBottom: "6px",
                      }}
                    >
                      {insight.explanation}
                    </div>
                    <div
                      style={{
                        fontSize: "11px",
                        color: "#666",
                      }}
                    >
                       Source: <strong>{insight.post_reference}</strong>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.ai_perspective && (
        <div style={{ marginBottom: "24px" }}>
          <h4 style={{ marginBottom: "12px", fontSize: "14px", color: "#aaa" }}>
            AI's Perspective
          </h4>
          <div
            style={{
              background: "#111",
              padding: "16px",
              borderRadius: "8px",
              border: "1px solid #1a1a1a",
              borderLeft: "3px solid #8b5cf6",
            }}
          >
            <p
              style={{
                margin: 0,
                color: "#ccc",
                lineHeight: "1.6",
                fontSize: "13px",
                whiteSpace: "pre-wrap",
              }}
            >
              {data.ai_perspective}
            </p>
          </div>
        </div>
      )}

      {/* Source Posts Grid */}
      {data.source_posts && data.source_posts.length > 0 && (
        <div>
          <h4 style={{ marginBottom: "14px", fontSize: "14px", color: "#aaa" }}>
            Source Posts ({data.source_posts.length})
          </h4>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "12px",
            }}
          >
            {data.source_posts.map((post, idx) => (
              <div
                key={idx}
                style={{
                  background: "#111",
                  border: "1px solid #1a1a1a",
                  borderRadius: "8px",
                  overflow: "hidden",
                }}
              >
                {post.media_url && (
                  <img
                    src={post.media_url}
                    alt={post.name}
                    style={{
                      width: "100%",
                      height: "120px",
                      objectFit: "cover",
                      background: "#0a0a0a",
                    }}
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
                  />
                )}
                <div style={{ padding: "12px" }}>
                  <div
                    style={{
                      fontWeight: 600,
                      fontSize: "12px",
                      marginBottom: "6px",
                      color: "#fff",
                    }}
                  >
                    {post.name}
                  </div>
                  <div
                    style={{
                      fontSize: "11px",
                      color: "#aaa",
                      lineHeight: "1.4",
                      marginBottom: "8px",
                      overflow: "hidden",
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                    }}
                  >
                    {post.caption}
                  </div>
                  <div style={{ fontSize: "10px", color: "#666" }}>
                    Score: <strong>{post.similarity_score}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {data.metadata && (
        <div
          style={{
            marginTop: "20px",
            padding: "12px",
            background: "#000",
            border: "1px solid #1a1a1a",
            borderRadius: "8px",
            fontSize: "10px",
            color: "#666",
          }}
        >
          <div>Total posts analyzed: {data.metadata.posts_analyzed}</div>
          <div>Top similarity: {data.metadata.top_similarity}</div>
        </div>
      )}
    </div>
  );
}

export default function App() {
    const [showCatSelector, setShowCatSelector] = useState(() => {
      return sessionStorage.getItem('first_search_done') !== 'true';
    });
    
    const handleApplyInitialCats = async (selectedCats) => {
      sessionStorage.setItem('first_search_done', 'true');
      setShowCatSelector(false);
      try {
        const res = await fetch(API_BASE + '/posts');
        const data = await res.json();
        const allPosts = data.posts || [];
        let catPosts = [];
        selectedCats.forEach(cat => {
          const filtered = allPosts
            .filter((p) => (p.category || '').toLowerCase() === cat.toLowerCase())
            .map((p) => ({ ...p, source: 'query' }));
          
          const shuffled = [...filtered].sort(() => Math.random() - 0.5);
          catPosts = catPosts.concat(shuffled.slice(0, 2));
        });

        const otherPosts = allPosts
          .filter((p) => !selectedCats.includes((p.category || '').toLowerCase()))
          .map((p) => ({ ...p, source: 'random' }))
          .sort(() => Math.random() - 0.5);

        const randomFour = otherPosts.slice(0, 4);
        let postsToShow = [...catPosts, ...randomFour];

        postsToShow.sort(() => Math.random() - 0.5);
        setResults(postsToShow);
        setBreakdown({
          budget: { query: catPosts.length, interest: 0, random: randomFour.length },
          query_based: catPosts.length,
          interest_based: 0,
          random: randomFour.length,
          total: postsToShow.length,
          ranked_interests: [],
        });
        setShowBento(false);
      } catch (err) {
        console.error('[init cats]', err);
        setError('Failed to load initial posts');
      }
    };

    const handleSkipInitialCats = () => {
      sessionStorage.setItem('first_search_done', 'true');
      setShowCatSelector(false);
    };
    useEffect(() => {
      if (sessionStorage.getItem('first_search_done') !== 'true') {
        setShowCatSelector(true);
      }
    }, []);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [breakdown, setBreakdown] = useState(null);
  const [bentoPosts, setBentoPosts] = useState([]);
  const [bentoLoaded, setBentoLoaded] = useState(false);
  const [showBento, setShowBento] = useState(true);
  const [likeEvents, setLikeEvents] = useState([]);
  const leRef = useRef([]);
  const [likedIds, setLikedIds] = useState(new Set());
  const liRef = useRef(new Set());
  leRef.current = likeEvents;
  liRef.current = likedIds;

  const searchInputRef = useRef(null);

//   rag handlerss 
  const [question, setQuestion] = useState("");
  const [ragData, setRagData] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  function handleRagKeyPress(e) {
    if (e.key === "Enter") {
      handleRagAsk();
    }
  }

  async function handleRagAsk() {
    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    setRagLoading(true);
    setRagData(null);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/rag`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question.trim(),
          limit: 5,
          min_score: 0.1,
          user_id: USER_ID,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }

      const data = await res.json();
      console.log("[RAG Response]", data);

      if (data.key_insights) {
        setRagData(data);
      } else if (data.answer) {
        setRagData({
          summary: data.answer,
          key_insights: [],
          ai_perspective:
            "No AI perspective available with this response format.",
          source_posts: data.sources || [],
          featured_image: null,
        });
      }
    } catch (err) {
      console.error("[RAG Error]", err);
      setError(`RAG failed: ${err.message}`);
    } finally {
      setRagLoading(false);
    }
  }

// handlers 

  useEffect(() => {
    fetch(`${API_BASE}/random?count=12`)
      .then((r) => r.json())
      .then((d) => {
        if (d.posts?.length) {
          setBentoPosts(d.posts);
          setBentoLoaded(true);
        }
      })
      .catch(() => {});
    fetch(`${API_BASE}/likes/${USER_ID}`)
      .then((r) => r.json())
      .then((d) => {
        if (!d.liked_posts?.length) return;
        const evs = d.liked_posts.map((p) => ({
          post_id: p.post_id,
          category: p.category || "unknown",
          timestamp: p.liked_at,
        }));
        const ids = new Set(d.liked_posts.map((p) => p.post_id));
        setLikeEvents(evs);
        setLikedIds(ids);
        leRef.current = evs;
        liRef.current = ids;
        console.log(`[mount] restored ${evs.length} events`);
      })
      .catch(() => {});
  }, []);

  async function handleLike(postId) {
    if (liRef.current.has(postId)) return;
    try {
      const res = await fetch(`${API_BASE}/like`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_id: postId, user_id: USER_ID }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const ev = {
        post_id: data.post_id,
        category: data.category || "unknown",
        timestamp: data.liked_at || new Date().toISOString(),
      };
      leRef.current = [...leRef.current, ev];
      liRef.current = new Set([...liRef.current, postId]);
      setLikeEvents([...leRef.current]);
      setLikedIds(new Set(liRef.current));
      console.log(
        `[like] ${postId} cat="${ev.category}" total=${leRef.current.length}`,
      );
      setError("");
    } catch (err) {
      console.error("[like]", err);
      setError(`Like failed: ${err.message}`);
    }
  }

  async function handleSearch(overrideQuery) {
    const q = typeof overrideQuery === "string" ? overrideQuery : query;
    if (!q.trim()) {
      setError("Please enter a search query");
      return;
    }
    const currentEvents = leRef.current;
    console.log(`[search] "${q}" | ${currentEvents.length} events`);
    setLoading(true);
    setError("");
    setShowBento(false);
    setResults([]);
    setBreakdown(null);
    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: q,
          user_id: USER_ID,
          session_like_events: currentEvents,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      const data = await res.json();
      console.log(`[search] breakdown:`, data.breakdown);
      const seen = new Set();
      const deduped = (data.results || []).filter((p) => {
        if (seen.has(p.post_id)) return false;
        seen.add(p.post_id);
        return true;
      });
      setResults(deduped);
      setBreakdown(data.breakdown || null);
    } catch (err) {
      console.error("[search]", err);
      setError(`Search failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  function handleNewSearch() {
    setResults([]);
    setBreakdown(null);
    setShowBento(true);
    setTimeout(() => {
      searchInputRef.current?.focus();
      searchInputRef.current?.select();
    }, 50);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  let modeLabel = "✦ Search to begin",
    modeColor = "#333";
  if (breakdown) {
    const ib = breakdown.interest_based || 0,
      qb = breakdown.query_based || 0,
      rb = breakdown.random || 0,
      ri = breakdown.ranked_interests || [];
    if (ib > 0) {
      modeLabel = `✦ Personalized  ·  ${ib} interest  ·  ${qb} query  ·  ${rb} random  ·  primary: ${ri[0]?.category || ""}`;
      modeColor = "#60a5fa";
    } else {
      modeLabel = `✦ Discovery  ·  ${qb} query  ·  ${rb} random`;
      modeColor = "#a78bfa";
    }
  }

  return (
    <div
      style={{
        background: "#000",
        color: "#fff",
        minHeight: "100vh",
        padding: "36px 20px 60px",
        fontFamily: "system-ui,sans-serif",
      }}
    >
      <div style={{ maxWidth: "860px", margin: "0 auto" }}>
        <h1
          style={{
            fontSize: "38px",
            marginBottom: "8px",
            textAlign: "center",
            fontWeight: 400,
            background:
              "linear-gradient(to bottom,#064e40,#0b6b58,#10775f,#139c77,#33b89b)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          the-algorithm
        </h1>
        <div
          style={{
            textAlign: "center",
            fontSize: "11px",
            color: modeColor,
            marginBottom: "20px",
            minHeight: "16px",
            transition: "color .3s ease",
          }}
        >
          {modeLabel}
        </div>
        {error && (
          <div
            style={{
              background: "#7f1d1d",
              border: "1px solid #dc2626",
              color: "#fca5a5",
              padding: "10px 14px",
              borderRadius: "8px",
              marginBottom: "16px",
              fontSize: "13px",
            }}
          >
            {error}
          </div>
        )}

        {/* search section  */}
        <div style={{ display: "flex", gap: "8px", marginBottom: "24px" }}>
          <input
            ref={searchInputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter") handleSearch();
            }}
            placeholder="Search posts…"
            disabled={loading}
            style={{
              flex: 1,
              padding: "11px 14px",
              background: "#111",
              border: "1px solid #222",
              color: "#fff",
              fontSize: "15px",
              outline: "none",
              borderRadius: "8px",
            }}
          />
          <button
            onClick={() => handleSearch()}
            disabled={loading}
            style={{
              padding: "11px 28px",
              background: loading ? "#333" : "#fff",
              color: "#000",
              border: "none",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: "15px",
              fontWeight: 600,
              borderRadius: "8px",
            }}
          >
            {loading ? "…" : "Search"}
          </button>
        </div>

        {showCatSelector && (
          <CategorySelector
            categories={ALL_CATEGORIES}
            onApply={handleApplyInitialCats}
            onSkip={handleSkipInitialCats}
          />
        )}

        {showBento && results.length === 0 && !loading && (
          <div>
            <div
              style={{
                fontSize: "20px",
                color: "white",
                letterSpacing: "1.5px",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}
            >
              SPOTLIGHT{" "}
              <img
                src="../src/assets/image.png"
                style={{
                  width: "22px",
                  height: "22px",
                  objectFit: "contain",
                  zIndex: 2,
                }}
              />
            </div>
            <BentoGrid posts={bentoPosts} visible={bentoLoaded} />
          </div>
        )}
        {loading && (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <div
              style={{
                display: "inline-block",
                width: "24px",
                height: "24px",
                border: "2px solid #222",
                borderTopColor: "#fff",
                borderRadius: "50%",
                animation: "spin .8s linear infinite",
              }}
            />
            <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
          </div>
        )}
        {!loading && results.length === 0 && query && (
          <div
            style={{
              textAlign: "center",
              color: "#333",
              padding: "40px",
              fontSize: "14px",
            }}
          >
            No results found
          </div>
        )}

        {results.length > 0 && breakdown?.ranked_interests?.length > 0 && (
          <InterestPills rankedInterests={breakdown.ranked_interests} />
        )}

        {results.length > 0 && (
          <div
            style={{
              marginBottom: "12px",
              padding: "8px 12px",
              background: "#0a0a0a",
              border: "1px solid #1a1a1a",
              borderRadius: "7px",
              fontSize: "10px",
              color: "#555",
              fontFamily: "monospace",
            }}
          >
            events:
            <span style={{ color: "#4ade80" }}> {likeEvents.length}</span> |
            budget:
            <span style={{ color: "#60a5fa" }}>
              {" "}
              q={breakdown?.budget?.query} i={breakdown?.budget?.interest} r=
              {breakdown?.budget?.random}
            </span>{" "}
            | actual:
            <span style={{ color: "#a78bfa" }}>
              {" "}
              q={breakdown?.query_based} i={breakdown?.interest_based} r=
              {breakdown?.random}
            </span>{" "}
            | total:
            <span
              style={{ color: breakdown?.total === 10 ? "#4ade80" : "#ef4444" }}
            >
              {" "}
              {breakdown?.total}
            </span>
          </div>
        )}

        {results.map((post, idx) => {
          const badge = getBadge(post.source),
            catColor = getCatColor(post.category),
            liked = likedIds.has(post.post_id),
            rankColor = post.interest_rank
              ? RANK_COLOR[post.interest_rank] || "#60a5fa"
              : null;
          return (
            <React.Fragment key={`${post.post_id}_${idx}`}>
              <div
                style={{
                  background: "#111",
                  padding: "18px",
                  marginBottom: "8px",
                  border: `1px solid ${post.source === "interest" ? "#1e3a8a55" : "#1a1a1a"}`,
                  borderRadius: "10px",
                  display: "flex",
                  gap: "14px",
                  position: "relative",
                  boxShadow:
                    post.source === "interest" ? "0 0 0 1px #1e3a8a22" : "none",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: "11px",
                    right: "11px",
                    background: badge.bg,
                    color: badge.color,
                    padding: "3px 10px",
                    borderRadius: "10px",
                    fontSize: "10px",
                    fontWeight: 700,
                  }}
                >
                  {badge.text}
                </div>
                {rankColor && post.interest_rank && (
                  <div
                    style={{
                      position: "absolute",
                      top: "11px",
                      right: "105px",
                      background: rankColor + "18",
                      color: rankColor,
                      padding: "3px 8px",
                      borderRadius: "10px",
                      fontSize: "9px",
                      fontWeight: 800,
                      textTransform: "uppercase",
                    }}
                  >
                    {post.interest_rank}
                  </div>
                )}
                {post.media_url && (
                  <img
                    src={post.media_url}
                    alt=""
                    style={{
                      width: "72px",
                      height: "72px",
                      objectFit: "cover",
                      flexShrink: 0,
                      borderRadius: "7px",
                      background: "#1a1a1a",
                    }}
                    onError={(e) => {
                      e.target.style.display = "none";
                    }}
                  />
                )}
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "7px",
                      alignItems: "flex-start",
                      paddingRight: "90px",
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontWeight: 600,
                          fontSize: "14px",
                          marginBottom: "3px",
                        }}
                      >
                        {post.name}
                      </div>
                      {post.interest_rank && post.interest_category && (
                        <div
                          style={{
                            color: rankColor || "#60a5fa",
                            fontSize: "10px",
                            marginBottom: "4px",
                            opacity: 0.85,
                          }}
                        >
                          ↳ {post.interest_rank} interest ·{" "}
                          {post.interest_category}
                        </div>
                      )}
                      <div
                        style={{
                          display: "flex",
                          gap: "7px",
                          alignItems: "center",
                        }}
                      >
                        <span style={{ color: "#333", fontSize: "11px" }}>
                          {post.post_id}
                        </span>
                        {post.category && post.category !== "unknown" && (
                          <span
                            style={{
                              background: catColor + "1a",
                              color: catColor,
                              padding: "1px 7px",
                              borderRadius: "5px",
                              fontSize: "10px",
                              fontWeight: 700,
                            }}
                          >
                            {post.category}
                          </span>
                        )}
                      </div>
                    </div>
                    <span
                      style={{ color: "#444", fontSize: "11px", flexShrink: 0 }}
                    >
                      {post.similarity_percentage}
                    </span>
                  </div>
                  <div
                    style={{
                      color: "#aaa",
                      lineHeight: "1.5",
                      marginBottom: "10px",
                      fontSize: "13px",
                    }}
                  >
                    {post.caption}
                  </div>
                  <button
                    onClick={() => handleLike(post.post_id)}
                    disabled={liked}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "5px",
                      padding: "6px 13px",
                      background: liked ? "#dc2626" : "#1a1a1a",
                      color: liked ? "#fff" : "#555",
                      border: `1px solid ${liked ? "#dc2626" : "#222"}`,
                      borderRadius: "18px",
                      cursor: liked ? "default" : "pointer",
                      fontSize: "12px",
                      fontWeight: 500,
                    }}
                  >
                    <Heart
                      size={12}
                      fill={liked ? "#fff" : "none"}
                      stroke={liked ? "#fff" : "#555"}
                    />
                    {liked ? "Liked" : "Like"}
                  </button>
                </div>
              </div>
              {idx === results.length - 1 && results.length >= 8 && (
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    margin: "18px 0",
                  }}
                >
                  <button
                    onClick={handleNewSearch}
                    style={{
                      padding: "10px 26px",
                      background: "#fff",
                      color: "#000",
                      borderRadius: "8px",
                      border: "none",
                      cursor: "pointer",
                      fontWeight: 600,
                      fontSize: "13px",
                    }}
                  >
                    New Search
                  </button>
                </div>
              )}
            </React.Fragment>
          );
        })}

        <hr style={{ margin: "48px 0 32px", borderColor: "#0f0f0f" }} />

 {/* rag section  */}
 
        {/* <div>
          <h2
            style={{
              marginBottom: "18px",
              fontWeight: 500,
              fontSize: "18px",
              color: "#fff",
            }}
          >
            🧠 Ask RAG
          </h2>
          <div style={{ display: "flex", gap: "8px", marginBottom: "24px" }}>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleRagKeyPress}
              placeholder="Ask about the posts…"
              disabled={ragLoading}
              style={{
                flex: 1,
                padding: "11px 14px",
                background: "#111",
                border: "1px solid #222",
                color: "#fff",
                fontSize: "15px",
                outline: "none",
                borderRadius: "8px",
              }}
            />
            <button
              onClick={handleRagAsk}
              disabled={ragLoading}
              style={{
                padding: "11px 28px",
                background: ragLoading ? "#333" : "#fff",
                color: "#000",
                border: "none",
                cursor: ragLoading ? "not-allowed" : "pointer",
                fontSize: "15px",
                fontWeight: 600,
                borderRadius: "8px",
              }}
            >
              {ragLoading ? "Thinking…" : "Ask"}
            </button>
          </div>

          
          <RAGResponse data={ragData} loading={ragLoading} />
        </div> */}
      </div>
    </div>
  );
}