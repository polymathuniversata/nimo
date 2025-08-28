import React from 'react';

// Minimal Index component for debugging
const Index = () => {
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: 'white', 
      color: 'black', 
      padding: '20px' 
    }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Nimo Platform Debug</h1>
      <p>This is the Index component working with inline styles.</p>
      <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid black' }}>
        <h2>Debug Info:</h2>
        <ul>
          <li>React: ✅ Working</li>
          <li>Index Component: ✅ Rendering</li>
          <li>Inline Styles: ✅ Applied</li>
        </ul>
      </div>
      <div style={{ marginTop: '2rem' }}>
        <button 
          style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}
          onClick={() => alert('Button works!')}
        >
          Test Button
        </button>
      </div>
    </div>
  );
};

export default Index;