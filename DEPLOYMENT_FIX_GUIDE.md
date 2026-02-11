# Medical Chatbot - Deployment Fix Guide

## 🚨 Current Issue

The chatbot interface is not working because:
1. **Frontend is deployed** on Vercel: https://medical-chatbot-rosy-psi.vercel.app/
2. **Backend URL is incorrect** or the backend is not deployed

The frontend is trying to connect to: `https://medical-chatbot-1-m6re.onrender.com`

## ✅ Solutions

You have **3 options** to fix this:

---

### Option 1: Deploy Your Backend to Render (Recommended)

This is the best solution for production use.

#### Step 1: Sign up/Login to Render
1. Go to https://render.com
2. Sign up or login with GitHub

#### Step 2: Create a New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `medical-chatbot-backend` (or any name you prefer)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`


#### Step 3: Add Environment Variables
In the Render dashboard, add these environment variables:

```
DATABASE_URL=your_database_url_here
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
```

**Important**: You need a PostgreSQL database. You can create one on:
- Render (free tier available)
- Neon.tech (free tier available - recommended)
- ElephantSQL
- Supabase

#### Step 4: Update Frontend with Your New Backend URL

Once deployed, Render will give you a URL like: `https://medical-chatbot-backend-xxxx.onrender.com`

**Update the frontend:**

1. Open `index.html` file
2. Find line ~1667 where it says:
   ```javascript
   const DEFAULT_BACKEND_URL = 'https://medical-chatbot-1-m6re.onrender.com';
   ```
3. Replace with **YOUR** Render URL:
   ```javascript
   const DEFAULT_BACKEND_URL = 'https://YOUR-SERVICE-NAME.onrender.com';
   ```

4. Commit and push to GitHub - Vercel will auto-deploy the updated frontend

---

### Option 2: Use an Existing Backend (If Already Deployed)

If you already have the backend deployed somewhere:

1. Find your backend URL
2. Open `index.html`
3. Update line ~1667:
   ```javascript
   const DEFAULT_BACKEND_URL = 'YOUR_ACTUAL_BACKEND_URL_HERE';
   ```
4. Commit and push to GitHub

---

### Option 3: Run Backend Locally (For Testing Only)

This is only for local testing, not production.

#### Step 1: Start the Backend Locally

```bash
cd "c:\Users\Fa3el5eerA\Desktop\Medical Chatbot\medical-chatbot-backend"

# Activate virtual environment
venv\Scripts\activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 2: Temporary Frontend Change

Open browser console (F12) on your Vercel site and run:
```javascript
localStorage.setItem('med_api_url', 'http://YOUR_LOCAL_IP:8000');
```

Replace `YOUR_LOCAL_IP` with your computer's IP address (find it by running `ipconfig` in command prompt).

**⚠️ Note**: This won't work for other users, only for testing on your network.

---

## 🔍 How to Check If Backend is Working

### Test 1: Health Check
Open in browser: `YOUR_BACKEND_URL/`

Should show: `{"message": "Medical Chatbot API is running"}`

### Test 2: API Documentation  
Open in browser: `YOUR_BACKEND_URL/docs`

Should show the Swagger API documentation

### Test 3: Chat Endpoint
Use browser console or Postman to test:
```javascript
fetch('YOUR_BACKEND_URL/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: 'What is diabetes?',
        guest_session_id: 'test123'
    })
})
```

---

## 📝 Recommended Deployment Steps

### For Production (Best Practice):

1. **Deploy Backend to Render**
   - Create PostgreSQL database on Neon.tech (free)
   - Deploy backend to Render with environment variables
   - Get backend URL from Render

2. **Update Frontend**
   - Change `DEFAULT_BACKEND_URL` in `index.html`
   - Commit and push to GitHub
   - Vercel will auto-deploy

3. **Test**
   - Visit https://medical-chatbot-rosy-psi.vercel.app/
   - Try sending a message
   - Check browser console for connection errors

---

## 🛠️ Quick Summary of Changes Made

1. ✅ Updated Content Security Policy to allow connections to multiple backend URLs
2. ✅ Added better error messages showing which backend URL is being used
3. ✅ Added console logging to help debug connection issues
4. ✅ Added comments explaining how to change the backend URL

---

## 📞 Need Help?

If you're still having issues:

1. **Check browser console** (F12 → Console tab) for error messages
2. **Verify backend is accessible** by visiting `YOUR_BACKEND_URL` in browser
3. **Check CORS settings** in backend `main.py` - should allow your Vercel URL
4. **Verify environment variables** are set correctly in Render/backend

---

## 🔗 Quick Links

- **Frontend (Vercel)**: https://medical-chatbot-rosy-psi.vercel.app/
- **Backend Code**: `c:\Users\Fa3el5eerA\Desktop\Medical Chatbot\medical-chatbot-backend\`
- **Frontend Code**: `c:\Users\Fa3el5eerA\Desktop\Medical Chatbot\index.html`

---

**Last Updated**: 2026-02-11
