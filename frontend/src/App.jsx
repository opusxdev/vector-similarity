import React, { useState } from 'react';



export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, limit: 5 })
      });
      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      alert('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleSearch();
  };

  return (
    <div style={{
      background: '#000',
      color: '#fff',
      minHeight: '100vh',
      padding: '40px 20px',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{
          fontSize: '32px',
          marginBottom: '40px',
          textAlign: 'center',
          fontWeight: '400'
        }}>
          Vector Similarity Search
        </h1>

        <div style={{
          display: 'flex',
          gap: '10px',
          marginBottom: '40px'
        }}>
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
              outline: 'none'
            }}
            onFocus={(e) => e.target.style.borderColor = '#666'}
            onBlur={(e) => e.target.style.borderColor = '#333'}
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
              fontWeight: '500'
            }}
            onMouseEnter={(e) => {
              if (!loading) e.target.style.background = '#ddd';
            }}
            onMouseLeave={(e) => {
              if (!loading) e.target.style.background = '#fff';
            }}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div>
          {results.length === 0 && !loading && query && (
            <div style={{
              textAlign: 'center',
              color: '#666',
              padding: '40px'
            }}>
              No results found
            </div>
          )}

          {results.map((post) => (
            <div
              key={post.post_id}
              style={{
                background: '#111',
                padding: '20px',
                marginBottom: '10px',
                border: '1px solid #222',
                display: 'flex',
                gap: '16px'
              }}
            >
              <img
                src={post.media_url}
                alt={post.caption}
                style={{
                  width: '80px',
                  height: '80px',
                  objectFit: 'cover',
                  flexShrink: 0,
                  background: '#222'
                }}
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/80x80/222/666?text=No+Image';
                }}
              />
              <div style={{ flex: 1 }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: '10px'
                }}>
                  <div>
                    <div style={{ fontWeight: '600' }}>{post.name}</div>
                    <div style={{
                      color: '#666',
                      fontSize: '14px'
                    }}>
                      {post.post_id}
                    </div>
                  </div>
                  <div style={{
                    color: '#888',
                    fontSize: '14px'
                  }}>
                    {post.similarity_percentage}
                  </div>
                </div>
                <div style={{
                  color: '#ccc',
                  lineHeight: '1.5'
                }}>
                  {post.caption}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}