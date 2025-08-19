import React, { useState } from 'react';

function App() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isUnsubscribe, setIsUnsubscribe] = useState(false);

  console.log('React App is rendering!');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setMessage({ type: 'error', text: 'Please enter a valid email address' });
      return;
    }

    setIsLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const endpoint = isUnsubscribe ? '/unsubscribe' : '/subscribe';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({
          type: 'success',
          text: isUnsubscribe
            ? 'Successfully unsubscribed!'
            : 'Successfully subscribed! Check your email for confirmation.'
        });
        setEmail('');
      } else {
        setMessage({ type: 'error', text: data.detail || 'Something went wrong' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Network error. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      {/* Debug indicator */}
      <div style={{
        position: 'fixed',
        top: '10px',
        left: '10px',
        background: 'red',
        color: 'white',
        padding: '5px 10px',
        fontSize: '12px',
        zIndex: 9999
      }}>
        REACT IS WORKING!
      </div>

      <div style={{
        maxWidth: '400px',
        width: '100%',
        textAlign: 'center'
      }}>
        <h1 style={{
          fontSize: '2.5rem',
          marginBottom: '10px',
          color: 'white',
          textShadow: '0 2px 4px rgba(0,0,0,0.3)'
        }}>
          DataDispatch
        </h1>

        <p style={{
          marginBottom: '30px',
          fontSize: '1.1rem',
          color: 'white',
          opacity: 0.9
        }}>
          Stay updated with the latest in AI & Technology
        </p>

        <div style={{
          background: 'white',
          borderRadius: '16px',
          padding: '30px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
        }}>
          <div style={{ marginBottom: '20px' }}>
            <button
              style={{
                padding: '10px 20px',
                marginRight: '10px',
                border: 'none',
                borderRadius: '6px',
                background: !isUnsubscribe ? '#667eea' : '#f0f0f0',
                color: !isUnsubscribe ? 'white' : '#666',
                cursor: 'pointer',
                fontWeight: '500'
              }}
              onClick={() => setIsUnsubscribe(false)}
            >
              Subscribe
            </button>
            <button
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '6px',
                background: isUnsubscribe ? '#667eea' : '#f0f0f0',
                color: isUnsubscribe ? 'white' : '#666',
                cursor: 'pointer',
                fontWeight: '500'
              }}
              onClick={() => setIsUnsubscribe(true)}
            >
              Unsubscribe
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              style={{
                width: '100%',
                padding: '15px',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '16px',
                marginBottom: '15px',
                boxSizing: 'border-box',
                outline: 'none'
              }}
              disabled={isLoading}
            />

            <button
              type="submit"
              style={{
                width: '100%',
                padding: '15px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.7 : 1
              }}
              disabled={isLoading}
            >
              {isLoading ? '⏳ Loading...' : (isUnsubscribe ? 'Unsubscribe' : 'Subscribe')}
            </button>
          </form>

          {message.text && (
            <div style={{
              padding: '15px',
              borderRadius: '8px',
              fontSize: '14px',
              marginTop: '15px',
              textAlign: 'center',
              background: message.type === 'success' ? '#d4edda' : '#f8d7da',
              color: message.type === 'success' ? '#155724' : '#721c24',
              border: `1px solid ${message.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`
            }}>
              {message.text}
            </div>
          )}
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '20px',
          marginTop: '20px',
          flexWrap: 'wrap'
        }}>
          <div style={{ textAlign: 'center', color: 'white' }}>
            <div style={{ fontSize: '24px' }}>🤖</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>AI-Powered</div>
          </div>
          <div style={{ textAlign: 'center', color: 'white' }}>
            <div style={{ fontSize: '24px' }}>📧</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>Weekly Updates</div>
          </div>
          <div style={{ textAlign: 'center', color: 'white' }}>
            <div style={{ fontSize: '24px' }}>🔒</div>
            <div style={{ fontSize: '12px', opacity: 0.9 }}>Privacy Focused</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
