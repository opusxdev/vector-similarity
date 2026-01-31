// dev4 c2
import React, { useState, useEffect, useRef } from 'react';
import { Heart } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [likedPosts, setLikedPosts] = useState(new Set());
  const [lastLikedPosts, setLastLikedPosts] = useState([]); // keep up to 2 most recent liked post IDs
  const userId = 'default_user';

  const [question, setQuestion] = useState('');
  const [ragAnswer, setRagAnswer] = useState('');
  const [ragSources, setRagSources] = useState([]);
  const [ragLoading, setRagLoading] = useState(false);

  useEffect(() => {
    loadUserLikes();
  }, []);

  const loadUserLikes = async () => {
    try {
      // const response = await fetch(`http://localhost:7860/likes/${userId}`);       // dev

      const response = await fetch(`/likes/${userId}`);                               // prod
      const data = await response.json();
      if (data.liked_posts && Array.isArray(data.liked_posts)) {
        const likedPostIds = new Set(data.liked_posts.map(p => p.post_id));
        setLikedPosts(likedPostIds);
        // set lastLikedPosts to the most recent up to 2 likes (if available)
        try {
          const sorted = data.liked_posts.slice().sort((a, b) => {
            if (!a.liked_at) return 1;
            if (!b.liked_at) return -1;
            return new Date(b.liked_at) - new Date(a.liked_at);
          });
          const recent = sorted.slice(0, 2).map(p => p.post_id).filter(Boolean);
          if (recent.length > 0) {
            setLastLikedPosts(recent);
          }
        } catch (e) {
          // ignore sorting errors
        }
      }
    } catch (error) {
      console.error('Error loading likes:', error);
      setLikedPosts(new Set());
    }
  };

  const handleLike = async (postId) => {
    try {
      console.log('[handleLike] sending like for', postId, 'user:', userId);
      // const response = await fetch('http://localhost:7860/like', {           //dev

      const response = await fetch('/like', {                                 //prod
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_id: postId, user_id: userId })
      });

      if (response.ok) {
        setLikedPosts(prev => new Set([...prev, postId]));
        // maintain recent list of liked posts (unique, most recent first), keep up to 2
        setLastLikedPosts(prev => {
          const arr = [postId, ...prev.filter(id => id !== postId)].slice(0, 2);
          return arr;
        });
      } else {
        const errText = await response.text();
        console.error('[handleLike] like failed', response.status, errText);
      }
    } catch (error) {
      console.error('Error liking post:', error);
      alert('Failed to like post');
    }
  };

  const handleSearch = async (searchQuery) => {
    const q = typeof searchQuery === 'string' ? searchQuery : query;
    if (!q.trim()) return;

    setLoading(true);
    try {
      const payload = {
        query: q,
        limit: 10,
        user_id: userId,
        last_liked_post_ids: lastLikedPosts
      };
      console.log('[handleSearch] payload ->', payload);

      // const response = await fetch('http://localhost:7860/search', {         // dev 

      const response = await fetch('/search', {                                // prod 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      console.log('[handleSearch] response breakdown ->', data.breakdown);
      setResults(data.results || []);
      setQuery(q);
    } catch (error) {
      console.error(error);
      alert('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const searchInputRef = useRef(null);

  const handleRefresh = () => {
    // Focus the top search input and select its contents so the user can type a new keyword
    if (searchInputRef.current) {
      searchInputRef.current.focus();
      try { searchInputRef.current.select(); } catch (e) { /* ignore if not selectable */ }
    }

    // Scroll up so the user can see the search box
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  const handleRagAsk = async () => {
    if (!question.trim()) return;

    setRagLoading(true);
    setRagAnswer('');
    setRagSources([]);

    try {
      // const response = await fetch('http://localhost:7860/rag', {       //    dev
      
      const response = await fetch('/rag', {                                 //prod
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          limit: 5,
          min_score: 0.1
        })
      });

      const data = await response.json();
      setRagAnswer(data.answer || '');
      setRagSources(data.sources || []);
    } catch (error) {
      console.error(error);
      alert('RAG failed');
    } finally {
      setRagLoading(false);
    }
  };

  const handleRagKeyPress = (e) => {
    if (e.key === 'Enter') handleRagAsk();
  };

  const getSourceBadge = (source) => {
    const badges = {
      query: { bg: '#1a4d2e', text: 'Query Match', color: '#4ade80' },
      personalized: { bg: '#1e3a8a', text: 'For You', color: '#60a5fa' },
      random: { bg: '#4c1d95', text: 'Discover', color: '#a78bfa' }
    };
    return badges[source] || badges.query;
  };

  const getCategoryColor = (category) => {
    const colors = {
      tech: '#3b82f6',
      ai: '#8b5cf6',
      healthcare: '#10b981',
      web3: '#f59e0b',
      socialmedia: '#ec4899',
      food: '#f97316',
      sports: '#06b6d4',
      finance: '#84cc16',
      movies: '#ef4444',
      music: '#a855f7',
      education: '#14b8a6',
      travel: '#6366f1',
      art: '#f43f5e',
      nature: '#22c55e'
    };
    return colors[category] || '#6b7280';
  };

  return (
    <div
      style={{
        background: '#000',
        color: '#fff',
        minHeight: '100vh',
        padding: '40px 20px',
        fontFamily: 'system-ui, sans-serif'
      }}
    >
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <h1
          style={{
            fontSize: '40px',
            marginBottom: '50px',
            textAlign: 'center',
            fontWeight: 400
          }}
        >
           the-algorithm 
        </h1>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
          <input
            ref={searchInputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search posts..."
            disabled={loading}
            style={{
              flex: 1,
              padding: '12px 16px',
              background: '#1a1a1a',
              border: '1px solid #333',
              color: '#fff',
              fontSize: '16px',
              outline: 'none',
              borderRadius: '8px'
            }}
          />

          <button
            onClick={handleSearch}
            disabled={loading}
            style={{
              padding: '12px 32px',
              background: loading ? '#666' : '#fff',
              color: '#000',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: 500,
              borderRadius: '8px'
            }}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div>
          {results.length === 0 && !loading && query && (
            <div
              style={{
                textAlign: 'center',
                color: '#666',
                padding: '40px'
              }}
            >
              No results found
            </div>
          )}

          {results.map((post, idx) => {
            const badge = getSourceBadge(post.source);
            const categoryColor = getCategoryColor(post.category);
            const isLiked = likedPosts.has(post.post_id);
            
            return (
              <React.Fragment key={post.post_id}>
                <div
                style={{
                  background: '#111',
                  padding: '20px',
                  marginBottom: '10px',
                  border: '1px solid #222',
                  borderRadius: '12px',
                  display: 'flex',
                  gap: '16px',
                  position: 'relative'
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    top: '12px',
                    right: '12px',
                    background: badge.bg,
                    color: badge.color,
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: 600
                  }}
                >
                  {badge.text}
                </div>

                {post.media_url && (
                  <img
                    src={post.media_url}
                    alt={post.caption}
                    style={{
                      width: '80px',
                      height: '80px',
                      objectFit: 'cover',
                      flexShrink: 0,
                      background: '#222',
                      borderRadius: '8px'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                )}
                
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: '10px',
                      alignItems: 'center',
                      paddingRight: '80px'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, marginBottom: '4px' }}>{post.name}</div>
                      {post.based_on && (
                        <div style={{ color: '#9ae6b4', fontSize: '12px', marginBottom: '6px' }}>
                          Based on liked post: {post.based_on}
                        </div>
                      )}
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <div
                          style={{
                            color: '#666',
                            fontSize: '14px'
                          }}
                        >
                          {post.post_id}
                        </div>
                        {post.category && (
                          <div
                            style={{
                              background: categoryColor + '20',
                              color: categoryColor,
                              padding: '2px 8px',
                              borderRadius: '6px',
                              fontSize: '12px',
                              fontWeight: 500
                            }}
                          >
                            {post.category}
                          </div>
                        )}
                      </div>
                    </div>
                    <div
                      style={{
                        color: '#888',
                        fontSize: '14px'
                      }}
                    >
                      {post.similarity_percentage}
                    </div>
                  </div>
                  <div
                    style={{
                      color: '#ccc',
                      lineHeight: '1.5',
                      marginBottom: '12px'
                    }}
                  >
                    {post.caption}
                  </div>
                  
                  <button
                    onClick={() => handleLike(post.post_id)}
                    disabled={isLiked}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '8px 16px',
                      background: isLiked ? '#dc2626' : '#1a1a1a',
                      color: isLiked ? '#fff' : '#888',
                      border: `1px solid ${isLiked ? '#dc2626' : '#333'}`,
                      borderRadius: '20px',
                      cursor: isLiked ? 'default' : 'pointer',
                      fontSize: '14px',
                      fontWeight: 500,
                      transition: 'all 0.2s'
                    }}
                  >
                    <Heart
                      size={16}
                      fill={isLiked ? '#fff' : 'none'}
                      stroke={isLiked ? '#fff' : '#888'}
                    />
                    {isLiked ? 'Liked' : 'Like'}
                  </button>
                </div>
              </div>

                {idx === 9 && results.length >= 10 && (
                  <div style={{ display: 'flex', justifyContent: 'center', margin: '12px 0' }}>
                    <button
                      onClick={handleRefresh}
                      disabled={loading}
                      style={{
                        padding: '10px 18px',
                        background: '#fff',
                        color: '#000',
                        borderRadius: '8px',
                        border: 'none',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontWeight: 600
                      }}
                    >
                      {loading ? 'Searching...' : 'Perform a new search'}
                    </button>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        <hr style={{ margin: '50px 0', borderColor: '#222' }} />

        {/* <h2>🧠 Ask RAG</h2>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleRagKeyPress}
            placeholder="Ask a question (e.g. posts about travel, food, coding...)"
            disabled={ragLoading}
            style={{
              flex: 1,
              padding: '12px 16px',
              background: '#1a1a1a',
              border: '1px solid #333',
              color: '#fff',
              fontSize: '16px',
              outline: 'none',
              borderRadius: '8px'
            }}
          />
          <button
            onClick={handleRagAsk}
            disabled={ragLoading}
            style={{
              padding: '12px 32px',
              background: ragLoading ? '#666' : '#fff',
              color: '#000',
              border: 'none',
              cursor: ragLoading ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: 500,
              borderRadius: '8px'
            }}
          >
            {ragLoading ? 'Thinking...' : 'Ask'}
          </button>
        </div> */}

        {ragAnswer && (
          <div
            style={{
              background: '#111',
              padding: '20px',
              border: '1px solid #222',
              borderRadius: '12px',
              marginBottom: '24px'
            }}
          >
            <h3 style={{ marginBottom: '16px' }}>Answer</h3>
            <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>
              {ragSources.length > 0 && ragSources[0].media_url && (
                <img
                  src={ragSources[0].media_url}
                  alt="Related post"
                  style={{
                    width: '200px',
                    height: '200px',
                    objectFit: 'cover',
                    borderRadius: '12px',
                    flexShrink: 0,
                    background: '#222'
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              )}
              <p
                style={{
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.6',
                  flex: 1,
                  margin: 0
                }}
              >
                {ragAnswer}
              </p>
            </div>
          </div>
        )}

        {ragSources.length > 0 && (
          <>
            <h3 style={{ marginTop: '10px', marginBottom: '12px' }}>
              Sources ({ragSources.length})
            </h3>
            {ragSources.map((s, i) => (
              <div
                key={i}
                style={{
                  background: '#0f0f0f',
                  padding: '16px',
                  marginBottom: '12px',
                  border: '1px solid #222',
                  borderRadius: '12px',
                  display: 'flex',
                  gap: '16px'
                }}
              >
                {s.media_url && (
                  <img
                    src={s.media_url}
                    alt={s.caption || 'Post image'}
                    style={{
                      width: '120px',
                      height: '120px',
                      objectFit: 'cover',
                      borderRadius: '8px',
                      flexShrink: 0,
                      background: '#222'
                    }}
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                )}
                <div style={{ flex: 1 }}>
                  <b>{s.name}</b>
                  <div
                    style={{
                      color: '#888',
                      fontSize: '14px',
                      marginBottom: '8px'
                    }}
                  >
                    {s.post_id} • score: {s.similarity_score}
                  </div>
                  <p
                    style={{
                      margin: 0,
                      color: '#ccc',
                      lineHeight: '1.5'
                    }}
                  >
                    {s.caption}
                  </p>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}