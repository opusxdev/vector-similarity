// v2 
import React, { useState, useEffect, useRef } from 'react';
import { Heart } from 'lucide-react';

const DEV_MODE = false ;
const API_BASE = DEV_MODE ? 'http://localhost:7860' : '';
const USER_ID  = 'default_user';

const SOURCE_BADGE = {
    query:        { bg: '#1a4d2e', color: '#4ade80', text: 'Query Match' },
    personalized: { bg: '#1e3a8a', color: '#60a5fa', text: 'For You'     },
    random:       { bg: '#4c1d95', color: '#a78bfa', text: 'Discover'    },
};

const CATEGORY_COLOR = {
    tech: '#3b82f6', ai: '#8b5cf6', healthcare: '#10b981', web3: '#f59e0b',
    socialmedia: '#ec4899', food: '#f97316', sports: '#06b6d4', finance: '#84cc16',
    movies: '#ef4444', music: '#a855f7', education: '#14b8a6', travel: '#6366f1',
    art: '#f43f5e', nature: '#22c55e', unknown: '#6b7280',
};

const getBadge    = s => SOURCE_BADGE[s] || SOURCE_BADGE.query;
const getCatColor = c => CATEGORY_COLOR[c?.toLowerCase()] || '#6b7280';
// bento Pattern 
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

// benti card 

function BentoCard({ post, span, visible, animDelay }) {
    const catColor = getCatColor(post.category);
    const isBig    = span.col === 2 && span.row === 2;
    const isWide   = span.col === 2 && span.row === 1;
    const isTall   = span.col === 1 && span.row === 2;
    const isSquare = span.col === 1 && span.row === 1;


    const captionLines = isBig ? 3 : isTall ? 2 : isWide ? 1 : 1;
    const nameLines = isBig ? 2 : 1;

    return (
        <div style={{
            gridColumn: `span ${span.col}`,
            gridRow:    `span ${span.row}`,
            background:          post.media_url
                ? `#0e0e0e url("${post.media_url}") center/cover no-repeat`
                : '#0e0e0e',
            border:              '1px solid #1e1e1e',
            borderRadius:        '10px',
            overflow:            'hidden',
            position:            'relative',
            opacity:             visible ? 1 : 0,
            transform:           visible ? 'scale(1)' : 'scale(0.95)',
            transition:          `opacity 0.45s ease ${animDelay}ms, transform 0.45s ease ${animDelay}ms`,
            display:             'flex',
            flexDirection:       'column',
            justifyContent:      'flex-end',  
        }}>

            <div style={{
                position:   'absolute',
                inset:      0,
                background: post.media_url
                    ? 'linear-gradient(to bottom, transparent 20%, rgba(0,0,0,0.55) 60%, rgba(0,0,0,0.92) 100%)'
                    : 'linear-gradient(to bottom, #111 0%, #0a0a0a 100%)',
                zIndex:     1,
            }} />

            <div style={{
                padding:    isBig ? '11px 12px' : isWide ? '8px 10px' : '7px 9px',
                position:   'relative',
                zIndex:     2,
            }}>

                {post.category && post.category !== 'unknown' && (
                    <div style={{
                        display:        'inline-block',
                        background:     catColor + '28',
                        color:          catColor,
                        fontSize:       '8px',
                        fontWeight:     800,
                        letterSpacing:  '0.6px',
                        padding:        '2px 6px',
                        borderRadius:   '4px',
                        marginBottom:   '4px',
                        textTransform:  'uppercase',
                    }}>
                        {post.category}
                    </div>
                )}

                <div style={{
                    fontWeight:         700,
                    fontSize:           isBig ? '12px' : '11px',
                    color:              '#f0f0f0',
                    lineHeight:         1.3,
                    marginBottom:       captionLines > 0 ? '3px' : 0,
                    overflow:           'hidden',
                    display:            '-webkit-box',
                    WebkitLineClamp:    nameLines,
                    WebkitBoxOrient:    'vertical',
                }}>
                    {post.name}
                </div>

                <div style={{
                    fontSize:           isSquare ? '9px' : '10px',
                    color:              post.media_url ? 'rgba(255,255,255,0.55)' : '#555',
                    lineHeight:         1.35,
                    overflow:           'hidden',
                    display:            '-webkit-box',
                    WebkitLineClamp:    captionLines,
                    WebkitBoxOrient:    'vertical',
                }}>
                    {post.caption}
                </div>
            </div>
        </div>
    );
}

//Bentogrid 
function BentoGrid({ posts, visible }) {
    const [cardsVisible, setCardsVisible] = useState(false);

    useEffect(() => {
        if (posts.length > 0) {
            const t = setTimeout(() => setCardsVisible(true), 80);
            return () => clearTimeout(t);
        }
    }, [posts]);

    if (posts.length === 0) {
        return (
            <div style={{
                display:             'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gridAutoRows:        '60px',
                gap:                 '5px',
                marginBottom:        '28px',
            }}>
                {BENTO_PATTERN.map((span, i) => (
                    <div key={i} style={{
                        gridColumn:   `span ${span.col}`,
                        gridRow:      `span ${span.row}`,
                        background:   '#0e0e0e',
                        borderRadius: '10px',
                        animation:    `pulse 1.8s ease-in-out ${i * 60}ms infinite`,
                    }} />
                ))}
                <style>{`@keyframes pulse { 0%,100%{opacity:.25} 50%{opacity:.5} }`}</style>
            </div>
        );
    }

    return (
        <div style={{
            display:             'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gridAutoRows:        '60px',
            gap:                 '5px',
            marginBottom:        '28px',
            opacity:             visible ? 1 : 0,
            transform:           visible ? 'none' : 'translateY(8px)',
            transition:          'opacity 0.5s ease, transform 0.5s ease',
        }}>
            {posts.slice(0, 12).map((post, i) => (
                <BentoCard
                    key={post.post_id}
                    post={post}
                    span={BENTO_PATTERN[i] || { col: 1, row: 1 }}
                    visible={cardsVisible}
                    animDelay={i * 35}
                />
            ))}
        </div>
    );
}

//main appp
export default function App() {
    const [query,   setQuery]   = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error,   setError]   = useState('');
    const [breakdown, setBreakdown] = useState(null);

    const [bentoPosts,   setBentoPosts]   = useState([]);
    const [bentoVisible, setBentoVisible] = useState(true);
    const [bentoLoaded,  setBentoLoaded]  = useState(false);

    const [likedInSession, setLikedInSession] = useState([]);
    const [allLikedSet,    setAllLikedSet]    = useState(new Set());

    const [question,   setQuestion]   = useState('');
    const [ragAnswer,  setRagAnswer]  = useState('');
    const [ragSources, setRagSources] = useState([]);
    const [ragLoading, setRagLoading] = useState(false);

    const searchInputRef = useRef(null);

    useEffect(() => {
        fetch(`${API_BASE}/random?count=12`)
            .then(r => r.json())
            .then(data => {
                if (data.posts?.length) {
                    setBentoPosts(data.posts);
                    setBentoLoaded(true);
                }
            })
            .catch(err => console.warn('Bento load failed:', err.message));

        fetch(`${API_BASE}/likes/${USER_ID}`)
            .then(r => r.json())
            .then(data => {
                if (data.liked_posts?.length) {
                    setAllLikedSet(new Set(data.liked_posts.map(p => p.post_id)));
                    const sorted = [...data.liked_posts]
                        .sort((a, b) => new Date(b.liked_at) - new Date(a.liked_at))
                        .map(p => p.post_id);
                    setLikedInSession(sorted);
                }
            })
            .catch(() => {});
    }, []);

//like
    async function handleLike(postId) {
        if (allLikedSet.has(postId)) return;
        try {
            const res = await fetch(`${API_BASE}/like`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ post_id: postId, user_id: USER_ID })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            setAllLikedSet(prev => new Set([...prev, postId]));
            setLikedInSession(prev => [postId, ...prev.filter(id => id !== postId)]);
            setError('');
        } catch (err) {
            setError(`Failed to like: ${err.message}`);
        }
    }

//search 
    async function handleSearch(overrideQuery) {
        const q = typeof overrideQuery === 'string' ? overrideQuery : query;
        if (!q.trim()) { setError('Please enter a search query'); return; }

        setLoading(true);
        setError('');
        setBentoVisible(false);

        try {
            const res = await fetch(`${API_BASE}/search`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    query: q,
                    user_id: USER_ID,
                    session_liked_ids: likedInSession,
                })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
            const data = await res.json();
            setResults(data.results || []);
            setBreakdown(data.breakdown || null);
            setQuery(q);
        } catch (err) {
            setError(`Search failed: ${err.message}`);
            setResults([]);
            setBreakdown(null);
        } finally {
            setLoading(false);
        }
    }

    function handleKeyPress(e)    { if (e.key === 'Enter') handleSearch(); }
    function handleRagKeyPress(e) { if (e.key === 'Enter') handleRagAsk(); }

    function handleNewSearch() {
        searchInputRef.current?.focus();
        try { searchInputRef.current?.select(); } catch {}
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
//rag
    async function handleRagAsk() {
        if (!question.trim()) { setError('Please enter a question'); return; }
        setRagLoading(true);
        setRagAnswer('');
        setRagSources([]);
        setError('');
        try {
            const res = await fetch(`${API_BASE}/rag`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ question, limit: 5, min_score: 0.1 })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setRagAnswer(data.answer || '');
            setRagSources(data.sources || []);
        } catch (err) {
            setError(`RAG failed: ${err.message}`);
        } finally {
            setRagLoading(false);
        }
    }

    let modeLabel = '✦ Search to begin';
    let modeColor = '#444';
    if (breakdown) {
        if (breakdown.mode === 'personalized') {
            modeLabel = `✦ Personalized — ${breakdown.personalized} interest-based · ${breakdown.query_based} query`;
            modeColor = '#60a5fa';
        } else {
            modeLabel = `✦ Discovery — ${breakdown.random} random · ${breakdown.query_based} query`;
            modeColor = '#a78bfa';
        }
    }
    const showBento = results.length === 0;

    return (
        <div style={{ background: '#000', color: '#fff', minHeight: '100vh', padding: '36px 20px 60px', fontFamily: 'system-ui, sans-serif' }}>
            <div style={{ maxWidth: '860px', margin: '0 auto' }}>
                <h1 style={{
                    fontSize: '38px', marginBottom: '8px', textAlign: 'center', fontWeight: 400,
                    background: 'linear-gradient(to bottom, #064e40, #0b6b58, #10775f, #139c77, #33b89b)',
                    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>
                    the-algorithm
                </h1>

                {DEV_MODE && (
                    <div style={{ textAlign: 'center', fontSize: '11px', color: '#6b6868', marginBottom: '6px' }}>
                        web3 · travel · food · coding · ai · art · nature · music · movies · sports · finance · socialmedia · education · healthcare · tech
                    </div>
                )}

                <div style={{ textAlign: 'center', fontSize: '11px', color: modeColor, marginBottom: '20px', minHeight: '16px' }}>
                    {modeLabel}
                </div>

                {error && (
                    <div style={{ background: '#7f1d1d', border: '1px solid #dc2626', color: '#fca5a5', padding: '10px 14px', borderRadius: '8px', marginBottom: '16px', fontSize: '13px' }}>
                        {error}
                    </div>
                )}

              {/* searchBar  */}
                <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                    <input
                        ref={searchInputRef}
                        type="text"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Search posts…"
                        disabled={loading}
                        style={{ flex: 1, padding: '11px 14px', background: '#111', border: '1px solid #222', color: '#fff', fontSize: '15px', outline: 'none', borderRadius: '8px' }}
                    />
                    <button
                        onClick={() => handleSearch()}
                        disabled={loading}
                        style={{ padding: '11px 28px', background: loading ? '#333' : '#fff', color: '#000', border: 'none', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '15px', fontWeight: 600, borderRadius: '8px' }}
                    >
                        {loading ? '…' : 'Search'}
                    </button>
                </div>

                {showBento && (
                    <div style={{
                        opacity:    bentoVisible ? 1 : 0,
                        transform:  bentoVisible ? 'none' : 'translateY(-6px)',
                        transition: 'opacity 0.35s ease, transform 0.35s ease',
                        pointerEvents: bentoVisible ? 'auto' : 'none',
                    }}>
                        <div style={{ fontSize: '10px', color: '#333', letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: '8px' }}>
                            Trending now
                        </div>

                        <BentoGrid posts={bentoPosts} visible={bentoLoaded} />
                    </div>
                )}
                   {/* search results  */}
                {results.length === 0 && !loading && query && (
                    <div style={{ textAlign: 'center', color: '#333', padding: '40px', fontSize: '14px' }}>
                        No results found
                    </div>
                )}

                {/* Session seeds debug*/}
                {DEV_MODE && likedInSession.length > 0 && results.length > 0 && (
                    <div style={{ marginBottom: '14px', padding: '8px 12px', background: '#0a1628', border: '1px solid #1e3a8a', borderRadius: '7px', fontSize: '10px', color: '#60a5fa' }}>
                        <span style={{ opacity: 0.6 }}>seeds → </span>
                        {likedInSession.join(' · ')}
                    </div>
                )}

                {results.map((post, idx) => {
                    const badge    = getBadge(post.source);
                    const catColor = getCatColor(post.category);
                    const liked    = allLikedSet.has(post.post_id);

                    return (
                        <React.Fragment key={post.post_id}>
                            <div style={{
                                background: '#111',
                                padding: '18px',
                                marginBottom: '8px',
                                border: `1px solid ${post.source === 'personalized' ? '#1e3a8a33' : '#1a1a1a'}`,
                                borderRadius: '10px',
                                display: 'flex',
                                gap: '14px',
                                position: 'relative',
                            }}>
                                <div style={{ position: 'absolute', top: '11px', right: '11px', background: badge.bg, color: badge.color, padding: '3px 10px', borderRadius: '10px', fontSize: '10px', fontWeight: 700, letterSpacing: '0.3px' }}>
                                    {badge.text}
                                </div>

                                {post.media_url && (
                                    <img src={post.media_url} alt="" style={{ width: '72px', height: '72px', objectFit: 'cover', flexShrink: 0, borderRadius: '7px', background: '#1a1a1a' }}
                                        onError={e => { e.target.style.display = 'none'; }} />
                                )}

                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '7px', alignItems: 'flex-start', paddingRight: '90px' }}>
                                        <div>
                                            <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '3px' }}>{post.name}</div>
                                            {post.based_on && (
                                                <div style={{ color: '#60a5fa', fontSize: '10px', marginBottom: '4px', opacity: 0.8 }}>
                                                    ↳ because you liked {post.based_on}
                                                </div>
                                            )}
                                            <div style={{ display: 'flex', gap: '7px', alignItems: 'center' }}>
                                                <span style={{ color: '#333', fontSize: '11px' }}>{post.post_id}</span>
                                                {post.category && post.category !== 'unknown' && (
                                                    <span style={{ background: catColor + '1a', color: catColor, padding: '1px 7px', borderRadius: '5px', fontSize: '10px', fontWeight: 700 }}>
                                                        {post.category}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        <span style={{ color: '#444', fontSize: '11px', flexShrink: 0 }}>{post.similarity_percentage}</span>
                                    </div>

                                    <div style={{ color: '#aaa', lineHeight: '1.5', marginBottom: '10px', fontSize: '13px' }}>{post.caption}</div>

                                    <button
                                        onClick={() => handleLike(post.post_id)}
                                        disabled={liked}
                                        style={{ display: 'flex', alignItems: 'center', gap: '5px', padding: '6px 13px', background: liked ? '#dc2626' : '#1a1a1a', color: liked ? '#fff' : '#555', border: `1px solid ${liked ? '#dc2626' : '#222'}`, borderRadius: '18px', cursor: liked ? 'default' : 'pointer', fontSize: '12px', fontWeight: 500 }}
                                    >
                                        <Heart size={12} fill={liked ? '#fff' : 'none'} stroke={liked ? '#fff' : '#555'} />
                                        {liked ? 'Liked' : 'Like'}
                                    </button>
                                </div>
                            </div>

                            {idx === results.length - 1 && results.length >= 8 && (
                                <div style={{ display: 'flex', justifyContent: 'center', margin: '18px 0' }}>
                                    <button onClick={handleNewSearch}
                                        style={{ padding: '10px 26px', background: '#fff', color: '#000', borderRadius: '8px', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '13px' }}>
                                        Perform a new search
                                    </button>
                                </div>
                            )}
                        </React.Fragment>
                    );
                })}

                <hr style={{ margin: '48px 0 32px', borderColor: '#0f0f0f' }} />

                {/* RAG */}
                {/* <h2 style={{ marginBottom: '18px', fontWeight: 500, fontSize: '18px' }}>🧠 Ask RAG</h2>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '18px' }}>
                    <input
                        type="text"
                        value={question}
                        onChange={e => setQuestion(e.target.value)}
                        onKeyPress={handleRagKeyPress}
                        placeholder="Ask about the posts…"
                        disabled={ragLoading}
                        style={{ flex: 1, padding: '11px 14px', background: '#111', border: '1px solid #222', color: '#fff', fontSize: '15px', outline: 'none', borderRadius: '8px' }}
                    />
                    <button onClick={handleRagAsk} disabled={ragLoading}
                        style={{ padding: '11px 28px', background: ragLoading ? '#333' : '#fff', color: '#000', border: 'none', cursor: ragLoading ? 'not-allowed' : 'pointer', fontSize: '15px', fontWeight: 600, borderRadius: '8px' }}>
                        {ragLoading ? 'Thinking…' : 'Ask'}
                    </button>
                </div>

                {ragAnswer && (
                    <div style={{ background: '#111', padding: '18px', border: '1px solid #1a1a1a', borderRadius: '10px', marginBottom: '20px' }}>
                        <h3 style={{ marginBottom: '14px', fontWeight: 500, fontSize: '15px' }}>Answer</h3>
                        <div style={{ display: 'flex', gap: '18px', alignItems: 'flex-start' }}>
                            {ragSources[0]?.media_url && (
                                <img src={ragSources[0].media_url} alt="" style={{ width: '160px', height: '160px', objectFit: 'cover', borderRadius: '9px', flexShrink: 0 }}
                                    onError={e => { e.target.style.display = 'none'; }} />
                            )}
                            <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', flex: 1, margin: 0, fontSize: '13px', color: '#ccc' }}>{ragAnswer}</p>
                        </div>
                    </div>
                )} */}

                {ragSources.length > 0 && (
                    <>
                        <h3 style={{ marginBottom: '10px', fontWeight: 500, fontSize: '14px' }}>Sources ({ragSources.length})</h3>
                        {ragSources.map((s, i) => (
                            <div key={i} style={{ background: '#0a0a0a', padding: '14px', marginBottom: '8px', border: '1px solid #111', borderRadius: '9px', display: 'flex', gap: '12px' }}>
                                {s.media_url && (
                                    <img src={s.media_url} alt="" style={{ width: '80px', height: '80px', objectFit: 'cover', borderRadius: '7px', flexShrink: 0 }}
                                        onError={e => { e.target.style.display = 'none'; }} />
                                )}
                                <div style={{ flex: 1 }}>
                                    <b style={{ fontSize: '13px' }}>{s.name}</b>
                                    <div style={{ color: '#444', fontSize: '11px', marginBottom: '5px' }}>{s.post_id} · {s.similarity_score}</div>
                                    <p style={{ margin: 0, color: '#888', lineHeight: '1.5', fontSize: '12px' }}>{s.caption}</p>
                                </div>
                            </div>
                        ))}
                    </>
                )}

            </div>
        </div>
    );
}