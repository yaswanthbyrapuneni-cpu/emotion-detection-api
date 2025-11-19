# Frontend Integration Guide

## 🔄 What You Need to Change in Your Frontend

After deploying to Render, you'll receive a URL like:
```
https://emotion-detection-api.onrender.com
```

### Change 1: Update API Endpoint URL

**Before (Local Development):**
```javascript
const API_URL = 'http://localhost:5000';
```

**After (Production):**
```javascript
const API_URL = 'https://YOUR_APP_NAME.onrender.com';
```

### Change 2: Add Environment Variables (Recommended)

Create a `.env` file in your frontend project:

```env
# .env.development
REACT_APP_API_URL=http://localhost:5000

# .env.production
REACT_APP_API_URL=https://YOUR_APP_NAME.onrender.com
```

Then use it in your code:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
```

### Change 3: Update Fetch Calls

**Example: Emotion Detection Function**

```javascript
async function detectEmotion(imageData) {
  try {
    const response = await fetch(`${API_URL}/detect-emotion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageData  // base64 string with data:image/jpeg;base64, prefix
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
    // Returns: { emotion: 'happy', confidence: 0.85, processing_time_ms: 245 }
    
  } catch (error) {
    console.error('Error detecting emotion:', error);
    return { emotion: 'neutral', confidence: 0.5, error: error.message };
  }
}
```

### Change 4: Handle Cold Start Delays

Since Render free tier spins down after inactivity, add loading states:

```javascript
const [isLoading, setIsLoading] = useState(false);
const [isWarmingUp, setIsWarmingUp] = useState(false);

async function detectEmotionWithWarming(imageData) {
  setIsLoading(true);
  setIsWarmingUp(true);
  
  // Ping health endpoint first to wake up service
  try {
    await fetch(`${API_URL}/health`);
    setIsWarmingUp(false);
  } catch (error) {
    console.log('Service warming up...');
  }
  
  // Now detect emotion
  const result = await detectEmotion(imageData);
  setIsLoading(false);
  return result;
}
```

### Change 5: Add Timeout Handling

```javascript
async function detectEmotionWithTimeout(imageData, timeout = 30000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${API_URL}/detect-emotion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image: imageData }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
    
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      console.error('Request timeout - service may be cold starting');
      return { 
        emotion: 'neutral', 
        confidence: 0.5, 
        error: 'Service warming up, please try again' 
      };
    }
    throw error;
  }
}
```

## 📱 Complete React Component Example

```javascript
import React, { useState, useRef, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'https://YOUR_APP_NAME.onrender.com';

function EmotionDetector() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [emotion, setEmotion] = useState('neutral');
  const [confidence, setConfidence] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    startCamera();
    warmUpService(); // Wake up the service on mount
  }, []);

  async function warmUpService() {
    try {
      await fetch(`${API_URL}/health`);
      console.log('Service is ready!');
    } catch (err) {
      console.log('Service warming up...');
    }
  }

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      videoRef.current.srcObject = stream;
    } catch (err) {
      setError('Camera access denied');
    }
  }

  function captureFrame() {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    return canvas.toDataURL('image/jpeg', 0.8);
  }

  async function detectEmotion() {
    setIsLoading(true);
    setError(null);

    try {
      const imageData = captureFrame();
      
      const response = await fetch(`${API_URL}/detect-emotion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageData })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      setEmotion(data.emotion);
      setConfidence(data.confidence);
      
    } catch (err) {
      setError(err.message);
      setEmotion('neutral');
      setConfidence(0.5);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="emotion-detector">
      <h2>Emotion Detection</h2>
      
      <video 
        ref={videoRef} 
        autoPlay 
        playsInline
        style={{ width: '100%', maxWidth: '640px' }}
      />
      
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
      <div className="controls">
        <button 
          onClick={detectEmotion} 
          disabled={isLoading}
        >
          {isLoading ? 'Detecting...' : 'Detect Emotion'}
        </button>
      </div>
      
      <div className="results">
        <h3>Current Emotion: {emotion.toUpperCase()}</h3>
        <p>Confidence: {(confidence * 100).toFixed(0)}%</p>
        {error && <p className="error">Error: {error}</p>}
      </div>
    </div>
  );
}

export default EmotionDetector;
```

## 🎯 Real-Time Video Feed Processing

For continuous emotion detection (every few seconds):

```javascript
useEffect(() => {
  let intervalId;
  
  if (isProcessing) {
    // Detect emotion every 2 seconds
    intervalId = setInterval(() => {
      detectEmotion();
    }, 2000);
  }
  
  return () => {
    if (intervalId) clearInterval(intervalId);
  };
}, [isProcessing]);
```

## ⚠️ Important Considerations

### 1. CORS is Already Enabled
Your backend has `CORS(app)` so cross-origin requests will work.

### 2. Rate Limiting
Consider adding rate limiting on frontend:
```javascript
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 1000; // 1 second

async function detectEmotionWithRateLimit(imageData) {
  const now = Date.now();
  if (now - lastRequestTime < MIN_REQUEST_INTERVAL) {
    console.log('Rate limited, waiting...');
    return;
  }
  lastRequestTime = now;
  return await detectEmotion(imageData);
}
```

### 3. Image Quality
For faster processing, reduce image quality:
```javascript
canvas.toDataURL('image/jpeg', 0.5); // 50% quality
```

### 4. Error Handling
Always handle errors gracefully:
```javascript
.catch(error => {
  console.error('Detection failed:', error);
  return { emotion: 'neutral', confidence: 0.5 };
});
```

## 🔄 Testing Both Environments

```javascript
const config = {
  development: {
    apiUrl: 'http://localhost:5000'
  },
  production: {
    apiUrl: 'https://YOUR_APP_NAME.onrender.com'
  }
};

const API_URL = process.env.NODE_ENV === 'production' 
  ? config.production.apiUrl 
  : config.development.apiUrl;
```

## ✅ Frontend Update Checklist

- [ ] Update API_URL constant
- [ ] Add environment variables
- [ ] Test health endpoint
- [ ] Test emotion detection
- [ ] Add loading states
- [ ] Handle cold start delays
- [ ] Add error handling
- [ ] Test with actual camera
- [ ] Deploy frontend changes

## 🚀 Quick Start Commands

```bash
# Update API URL
export REACT_APP_API_URL=https://YOUR_APP_NAME.onrender.com

# Start development
npm start

# Build for production
npm run build
```
