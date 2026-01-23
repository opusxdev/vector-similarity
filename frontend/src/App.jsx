// import React, { useState } from 'react';



// export default function App() {
//   const [query, setQuery] = useState('');
//   const [results, setResults] = useState([]);
//   const [loading, setLoading] = useState(false);

//   const handleSearch = async () => {
//     if (!query.trim()) return;

//     setLoading(true);
//     try {
//       // const response = await fetch('/search', {         PROD COMMENTED         
//       const response = await fetch("http://localhost:8000/search", {           
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ query: query, limit: 5 })
//       });
//       const data = await response.json();
//       setResults(data.results);
//     } catch (error) {
//       alert('Search failed');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter') handleSearch();
//   };

//   return (
//     <div style={{
//       background: '#000',
//       color: '#fff',
//       minHeight: '100vh',
//       padding: '40px 20px',
//       fontFamily: 'system-ui, sans-serif'
//     }}>
//       <div style={{ maxWidth: '800px', margin: '0 auto' }}>
//         <h1 style={{
//           fontSize: '32px',
//           marginBottom: '40px',
//           textAlign: 'center',
//           fontWeight: '400'
//         }}>
//           Vector Similarity Search
//         </h1>

//         <div style={{
//           display: 'flex',
//           gap: '10px',
//           marginBottom: '40px'
//         }}>
//           <input
//             type="text"
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyPress={handleKeyPress}
//             placeholder="Search posts..."
//             disabled={loading}
//             style={{
//               flex: 1,
//               padding: '12px 16px',
//               background: '#1a1a1a',
//               border: '1px solid #333',
//               color: '#fff',
//               fontSize: '16px',
//               outline: 'none'
//             }}
//             onFocus={(e) => e.target.style.borderColor = '#666'}
//             onBlur={(e) => e.target.style.borderColor = '#333'}
//           />
//           <button
//             onClick={handleSearch}
//             disabled={loading}
//             style={{
//               padding: '12px 32px',
//               background: loading ? '#666' : '#fff',
//               color: '#000',
//               border: 'none',
//               cursor: loading ? 'not-allowed' : 'pointer',
//               fontSize: '16px',
//               fontWeight: '500'
//             }}
//             onMouseEnter={(e) => {
//               if (!loading) e.target.style.background = '#ddd';
//             }}
//             onMouseLeave={(e) => {
//               if (!loading) e.target.style.background = '#fff';
//             }}
//           >
//             {loading ? 'Searching...' : 'Search'}
//           </button>
//         </div>

//         <div>
//           {results.length === 0 && !loading && query && (
//             <div style={{
//               textAlign: 'center',
//               color: '#666',
//               padding: '40px'
//             }}>
//               No results found
//             </div>
//           )}

//           {results.map((post) => (
//             <div
//               key={post.post_id}
//               style={{
//                 background: '#111',
//                 padding: '20px',
//                 marginBottom: '10px',
//                 border: '1px solid #222',
//                 display: 'flex',
//                 gap: '16px'
//               }}
//             >
//               <img
//                 src={post.media_url}
//                 alt={post.caption}
//                 style={{
//                   width: '80px',
//                   height: '80px',
//                   objectFit: 'cover',
//                   flexShrink: 0,
//                   background: '#222'
//                 }}
//                 onError={(e) => {
//                   e.target.src = 'https://via.placeholder.com/80x80/222/666?text=No+Image';
//                 }}
//               />
//               <div style={{ flex: 1 }}>
//                 <div style={{
//                   display: 'flex',
//                   justifyContent: 'space-between',
//                   marginBottom: '10px'
//                 }}>
//                   <div>
//                     <div style={{ fontWeight: '600' }}>{post.name}</div>
//                     <div style={{
//                       color: '#666',
//                       fontSize: '14px'
//                     }}>
//                       {post.post_id}
//                     </div>
//                   </div>
//                   <div style={{
//                     color: '#888',
//                     fontSize: '14px'
//                   }}>
//                     {post.similarity_percentage}
//                   </div>
//                 </div>
//                 <div style={{
//                   color: '#ccc',
//                   lineHeight: '1.5'
//                 }}>
//                   {post.caption}
//                 </div>
//               </div>
//             </div>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// }




// dev2 workinfg

import React, { useState } from "react";

export default function App() {
  /* ---------- VECTOR SEARCH STATE ---------- */
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  /* ---------- RAG STATE ---------- */
  const [question, setQuestion] = useState("");
  const [ragAnswer, setRagAnswer] = useState("");
  const [ragSources, setRagSources] = useState([]);
  const [ragLoading, setRagLoading] = useState(false);

  /* ---------- VECTOR SEARCH ---------- */
  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, limit: 5 }),
      });

      const data = await response.json();
      setResults(data.results || []);
    } catch {
      alert("Search failed");
    } finally {
      setLoading(false);
    }
  };

  /* ---------- RAG SEARCH ---------- */
  const handleRagAsk = async () => {
    if (!question.trim()) return;

    setRagLoading(true);
    setRagAnswer("");
    setRagSources([]);

    try {
      const response = await fetch("http://localhost:8000/rag", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          limit: 5,
          min_score: 0.2,
        }),
      });

      const data = await response.json();
      setRagAnswer(data.answer);
      setRagSources(data.sources || []);
    } catch {
      alert("RAG failed");
    } finally {
      setRagLoading(false);
    }
  };

  return (
    <div
      style={{
        background: "#000",
        color: "#fff",
        minHeight: "100vh",
        padding: "40px 20px",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div style={{ maxWidth: "900px", margin: "0 auto" }}>
        <h1 style={{ textAlign: "center", marginBottom: "80px" , fontSize: "40px" }}>
          Vector Similarity + RAG
        </h1>

      
        <h2>🔍 Vector Search</h2>
        <div style={{ display: "flex", gap: "10px", marginBottom: "30px" }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search posts..."
            style={inputStyle}
          />
          <button onClick={handleSearch} disabled={loading} style={btnStyle}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {results.map((post) => (
          <div key={post.post_id} style={{ ...cardStyle, display: "flex", gap: "16px" }}>
            <img
              src={post.media_url}
              alt={post.caption}
              style={{
                width: "120px",
                height: "120px",
                objectFit: "cover",
                borderRadius: "8px",
                flexShrink: 0,
                background: "#222",
              }}
              onError={(e) => {
                e.target.src = "https://via.placeholder.com/120x120/222/666?text=No+Image";
              }}
            />
            <div style={{ flex: 1 }}>
              <b>{post.name}</b>
              <div style={{ color: "#888", fontSize: "14px", marginBottom: "8px" }}>
                {post.post_id} • score: {post.similarity_score}
              </div>
              <p style={{ margin: 0, color: "#ccc", lineHeight: "1.5" }}>{post.caption}</p>
            </div>
          </div>
        ))}

       
        <hr style={{ margin: "50px 0", borderColor: "#222" }} />

        <h2>🧠 Ask RAG bro its really cool  </h2>
        <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question (e.g. pizza posts)"
            style={inputStyle}
          />
          <button onClick={handleRagAsk} disabled={ragLoading} style={btnStyle}>
            {ragLoading ? "Thinking..." : "Ask"}
          </button>
        </div>

        {ragAnswer && (
          <div style={{ ...cardStyle, background: "#111" }}>
            <h3 style={{ marginBottom: "16px" }}>Answer</h3>
            <div style={{ display: "flex", gap: "20px", alignItems: "flex-start" }}>
              {ragSources.length > 0 && ragSources[0].media_url && (
                <img
                  src={ragSources[0].media_url}
                  alt="Related post"
                  style={{
                    width: "200px",
                    height: "200px",
                    objectFit: "cover",
                    borderRadius: "12px",
                    flexShrink: 0,
                    background: "#222",
                  }}
                  onError={(e) => {
                    e.target.src = "https://via.placeholder.com/200x200/222/666?text=No+Image";
                  }}
                />
              )}
              <p style={{ 
                whiteSpace: "pre-wrap", 
                lineHeight: "1.6", 
                flex: 1,
                margin: 0 
              }}>
                {ragAnswer}
              </p>
            </div>
          </div>
        )}

        {ragSources.length > 0 && (
          <>
            <h3 style={{ marginTop: "30px" }}>Sources</h3>
            {ragSources.map((s, i) => (
              <div key={i} style={{ ...cardStyle, display: "flex", gap: "16px" }}>
                <img
                  src={s.media_url}
                  alt={s.caption}
                  style={{
                    width: "120px",
                    height: "120px",
                    objectFit: "cover",
                    borderRadius: "8px",
                    flexShrink: 0,
                    background: "#222",
                  }}
                  onError={(e) => {
                    e.target.src = "https://via.placeholder.com/120x120/222/666?text=No+Image";
                  }}
                />
                <div style={{ flex: 1 }}>
                  <b>{s.name}</b>
                  <div style={{ color: "#888", fontSize: "14px", marginBottom: "8px" }}>
                    {s.post_id} • score: {s.similarity_score}
                  </div>
                  <p style={{ margin: 0, color: "#ccc", lineHeight: "1.5" }}>{s.caption}</p>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}

/* ---------- STYLES ---------- */
const inputStyle = {
  flex: 1,
  padding: "12px",
  background: "#111",
  color: "#fff",
  border: "1px solid #333",
  fontSize: "16px",
};

const btnStyle = {
  padding: "12px 30px",
  background: "#fff",
  color: "#000",
  border: "none",
  cursor: "pointer",
};

const cardStyle = {
  background: "#0f0f0f",
  padding: "16px",
  marginBottom: "12px",
  border: "1px solid #222",
};
