// dev4 c2
import React, { useState, useEffect } from 'react';
import { Heart } from 'lucide-react';

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [likedPosts, setLikedPosts] = useState(new Set());
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
      const response = await fetch(`http://localhost:7860/likes/${userId}`);
      const data = await response.json();
      if (data.liked_posts && Array.isArray(data.liked_posts)) {
        const likedPostIds = new Set(data.liked_posts.map(p => p.post_id));
        setLikedPosts(likedPostIds);
      }
    } catch (error) {
      console.error('Error loading likes:', error);
      setLikedPosts(new Set());
    }
  };

  const handleLike = async (postId) => {
    try {
      const response = await fetch('http://localhost:7860/like', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_id: postId, user_id: userId })
      });

      if (response.ok) {
        setLikedPosts(prev => new Set([...prev, postId]));
      }
    } catch (error) {
      console.error('Error liking post:', error);
      alert('Failed to like post');
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:7860/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query, 
          limit: 10,
          user_id: userId 
        })
      });
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error(error);
      alert('Search failed');
    } finally {
      setLoading(false);
    }
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
      const response = await fetch('http://localhost:7860/rag', {
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
          🔍 Vector Similarity + RAG
        </h1>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
          <input
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

          {results.map((post) => {
            const badge = getSourceBadge(post.source);
            const categoryColor = getCategoryColor(post.category);
            const isLiked = likedPosts.has(post.post_id);
            
            return (
              <div
                key={post.post_id}
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
            );
          })}
        </div>

        <hr style={{ margin: '50px 0', borderColor: '#222' }} />

        <h2>🧠 Ask RAGYY</h2>
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
        </div>

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