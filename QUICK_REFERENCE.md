# 🚀 Quick Reference - Render Deployment

## 📦 Files Needed
```
your-project/
├── app.py                  # Your Flask application
├── requirements.txt        # Python dependencies
├── Procfile               # Tells Render how to start your app
├── render.yaml            # (Optional) Automated deployment config
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## ⚡ Quick Deploy Commands

### 1. Setup Git
```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Create GitHub Repo
```bash
# On GitHub: Create new repository "emotion-detection-api"
git remote add origin https://github.com/YOUR_USERNAME/emotion-detection-api.git
git branch -M main
git push -u origin main
```

### 3. Deploy on Render
- Go to https://dashboard.render.com
- Click "New" → "Web Service"
- Connect your GitHub repo
- Render will auto-detect settings from Procfile

## 🔗 Your API URLs (After Deployment)

```
Base URL: https://YOUR_APP_NAME.onrender.com

Endpoints:
- GET  /               → API info
- GET  /health         → Health check
- POST /detect-emotion → Emotion detection
```

## 💻 Frontend Changes

### Before (Local)
```javascript
const API_URL = 'http://localhost:5000';
```

### After (Production)
```javascript
const API_URL = 'https://YOUR_APP_NAME.onrender.com';
```

## 🧪 Test Your Deployment

```bash
# Test health endpoint
curl https://YOUR_APP_NAME.onrender.com/health

# Expected response:
# {"status":"healthy","service":"deepface-emotion-detector"}
```

## ⏱️ Important Notes

### First Request
- Takes 30-60 seconds (cold start)
- Service wakes up from sleep
- Subsequent requests are fast

### Free Tier
- 750 hours/month free
- Spins down after 15 min inactivity
- 512MB RAM limit

### Keep Alive (Optional)
Use UptimeRobot or cron job:
```bash
*/10 * * * * curl https://YOUR_APP_NAME.onrender.com/health
```

## 🔧 Troubleshooting

### Build Fails
1. Check Python version (3.11 recommended)
2. Verify requirements.txt
3. Check Render build logs

### Timeout Errors
- Increase timeout in Procfile (currently 120s)
- Check image size (large images take longer)

### Memory Issues
- Free tier: 512MB RAM
- Consider upgrading if needed

## 📊 Example Frontend Code

```javascript
async function detectEmotion(imageBase64) {
  const response = await fetch(
    'https://YOUR_APP_NAME.onrender.com/detect-emotion',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: imageBase64 })
    }
  );
  return await response.json();
}
```

## 📝 Environment Variables (Optional)

In Render dashboard:
- `PYTHON_VERSION` = `3.11.0`
- `FLASK_DEBUG` = `False`

## 🆘 Common Issues

### "Service Unavailable"
- Service is cold starting
- Wait 30-60 seconds
- Try again

### "CORS Error"
- Already handled in backend
- Check if URL is correct

### "Invalid Image Data"
- Ensure base64 encoding is correct
- Include data URL prefix: `data:image/jpeg;base64,`

## ✅ Deployment Checklist

- [ ] All files committed to Git
- [ ] Pushed to GitHub
- [ ] Render service created
- [ ] Build successful
- [ ] Health endpoint works
- [ ] Emotion detection works
- [ ] Frontend URL updated
- [ ] Tested end-to-end

## 🔗 Useful Links

- Render Dashboard: https://dashboard.render.com
- Render Docs: https://render.com/docs
- DeepFace GitHub: https://github.com/serengil/deepface

---

**Need help?** Check DEPLOYMENT_GUIDE.md for detailed instructions!
