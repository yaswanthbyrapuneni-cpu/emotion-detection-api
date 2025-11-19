# DeepFace Emotion Detection API - Render Deployment Guide

## 📋 Prerequisites
- GitHub account
- Render account (free tier works)
- Git installed on your computer

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Create a new GitHub repository**
   - Go to https://github.com/new
   - Name it: `emotion-detection-api`
   - Keep it public (required for free tier)
   - Don't initialize with README

2. **Initialize Git in your project folder**
   ```bash
   cd /path/to/your/project
   git init
   git add .
   git commit -m "Initial commit: DeepFace emotion detection API"
   ```

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/emotion-detection-api.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Render

#### Method A: Using render.yaml (Recommended)

1. **Connect Repository**
   - Go to https://dashboard.render.com
   - Click "New" → "Blueprint"
   - Connect your GitHub account if not connected
   - Select your `emotion-detection-api` repository
   - Click "Connect"

2. **Render will automatically**
   - Detect the `render.yaml` file
   - Create the service with the specified configuration
   - Start the deployment

#### Method B: Manual Deployment

1. **Create Web Service**
   - Go to https://dashboard.render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select `emotion-detection-api`

2. **Configure Service**
   - **Name**: `emotion-detection-api`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Instance Type**: `Free`

3. **Environment Variables** (Optional but recommended)
   - `PYTHON_VERSION`: `3.11.0`

4. **Click "Create Web Service"**

### Step 3: Wait for Deployment

- First deployment takes 5-10 minutes
- Render will:
  - Install Python dependencies
  - Download DeepFace models (~500MB)
  - Start the server

### Step 4: Test Your API

Once deployed, you'll get a URL like: `https://emotion-detection-api.onrender.com`

**Test the health endpoint:**
```bash
curl https://YOUR_APP_NAME.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "deepface-emotion-detector"
}
```

## 🎯 Important Notes

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds
- 750 hours/month free runtime

### Performance Optimization
- First emotion detection is slow (model loading)
- Subsequent requests are faster
- Consider upgrading to paid tier for production

### Cold Start Solution
To keep service warm, use a cron job:
```bash
# Add to crontab (every 10 minutes)
*/10 * * * * curl https://YOUR_APP_NAME.onrender.com/health
```

Or use services like:
- UptimeRobot (free)
- Cron-job.org (free)

## 🔧 Troubleshooting

### Build Fails
- Check Python version compatibility
- Verify all dependencies in requirements.txt
- Check Render logs for specific errors

### Timeout Errors
- Increase timeout in Procfile (already set to 120s)
- Consider upgrading instance type

### Memory Issues
- Free tier has 512MB RAM
- DeepFace + TensorFlow uses ~400MB
- Upgrade to paid tier if needed

## 📊 Monitoring

**View Logs:**
1. Go to Render dashboard
2. Select your service
3. Click "Logs" tab
4. Monitor real-time activity

**Check Metrics:**
- Request count
- Response times
- Error rates

## 🔄 Updating Your Deployment

**Push changes to GitHub:**
```bash
git add .
git commit -m "Update: description of changes"
git push
```

Render automatically redeploys on push to main branch.

## 🎨 Frontend Integration

Your deployed API URL will be:
```
https://YOUR_APP_NAME.onrender.com
```

Update your frontend to use this URL instead of `http://localhost:5000`

## ✅ Success Checklist

- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Deployment successful
- [ ] Health endpoint responds
- [ ] Emotion detection works
- [ ] Frontend updated with new URL

## 🆘 Need Help?

- Render Docs: https://render.com/docs
- DeepFace Issues: https://github.com/serengil/deepface/issues
- Check deployment logs in Render dashboard
