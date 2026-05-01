import React, { useState } from 'react';
import axios from 'axios';
import { Search, MapPin, Loader2 } from 'lucide-react';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    const val = e.target.value;
    setQuery(val);

    if (val.length > 2) {
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:3000/v1/search?q=${val}` || `${import.meta.env.VITE_API_URL}/v1/search?q=${val}`);
        setResults(response.data);
      } catch (err) {
        console.error("Search failed", err);
      } finally {
        setLoading(false);
      }
    } else {
      setResults([]);
    }
  };

  return (
    <div style={{ padding: '40px', fontFamily: 'sans-serif', maxWidth: '600px', margin: '0 auto' }}>
      <h1>All India Village Finder</h1>
      <p>Search for any village in India to see the full hierarchy.</p>
      
      <div style={{ position: 'relative', marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Type village name (e.g. Manibeli)..."
          value={query}
          onChange={handleSearch}
          style={{ width: '100%', padding: '12px 40px', borderRadius: '8px', border: '1px solid #ccc', fontSize: '16px' }}
        />
        <Search style={{ position: 'absolute', left: '10px', top: '12px', color: '#888' }} size={20} />
        {loading && <Loader2 style={{ position: 'absolute', right: '10px', top: '12px', animation: 'spin 1s linear infinite' }} size={20} />}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {results.map((item) => (
          <div key={item.value} style={{ padding: '15px', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#f9f9f9' }}>
            <div style={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <MapPin size={16} color="red" /> {item.label}
            </div>
            <div style={{ fontSize: '14px', color: '#555', marginTop: '5px' }}>{item.fullAddress}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;