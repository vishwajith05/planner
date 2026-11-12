# PlanWise AI - Production Web Deployment Guide

This guide covers deployment for the complete **PlanWise AI** web application:
- **Frontend**: React + TypeScript + Vite + Tailwind CSS (Deployed on **Vercel**)
- **Backend**: Python 3.11 + FastAPI + SQLite/PostgreSQL (Deployed on **Render**)
- **Database & Auth**: SQLite (hermetic local) or Cloud Firestore / Firebase Auth
- **AI Engine**: Google Gemini API with fallback Mock Provider

---

## 1. Architecture Overview

```
Client (Desktop / Tablet / Mobile Browser / PWA)
      │
      ▼
Vercel Edge Network (React 18 SPA + Service Worker)
      │
      │ HTTPS / JWT Bearer
      ▼
Render Web Service (FastAPI + Pydantic v2 + SQLAlchemy)
      │
      ├────► Database (SQLite / PostgreSQL / Cloud Firestore)
      └────► Google Gemini 1.5 / 2.0 API (Backend Key Isolation)
```

---

## 2. Frontend Deployment (Vercel)

### Step 1: Connect Repository to Vercel
1. Log into [vercel.com](https://vercel.com).
2. Click **Add New Project** and select your `planner` Git repository.
3. In **Root Directory**, click **Edit** and set it to: `frontend`.

### Step 2: Build & Output Settings
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Step 3: Environment Variables on Vercel
Add the following in project settings:
```ini
VITE_API_URL=https://your-backend-app.onrender.com/api/v1
```

### Step 4: SPA Routing Rewrite Configuration
`frontend/vercel.json` is configured as:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## 3. Backend Deployment (Render)

### Step 1: Create a New Web Service
1. Log into [render.com](https://render.com).
2. Click **New +** > **Web Service**.
3. Connect your Git repository.

### Step 2: Service Configuration
- **Name**: `planwise-ai-backend`
- **Region**: Oregon (US West) or Frankfurt (EU)
- **Branch**: `main`
- **Root Directory**: `.` (or empty)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables on Render
Configure the following in the Render dashboard:
```ini
ENVIRONMENT=production
PROJECT_NAME=PlanWise AI
SECRET_KEY=generate-a-strong-random-64-character-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
BACKEND_CORS_ORIGINS=["https://your-planwise-app.vercel.app","http://localhost:5173"]
DATABASE_URL=sqlite:///./planwise.db

# AI Provider Configuration
AI_PROVIDER=mock
# When using real Gemini API:
# AI_PROVIDER=gemini
# GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 4. Firebase Authentication & Firestore Configuration (Optional)

PlanWise AI includes native compatibility with Firebase Web Auth:
1. Go to the [Firebase Console](https://console.firebase.google.com).
2. Create project **PlanWise AI**.
3. Enable **Authentication** (Email/Password).
4. (Optional) Enable **Cloud Firestore** in production mode.
5. In project settings, add a **Web App** to retrieve your config:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "planwise-ai.firebaseapp.com",
  projectId: "planwise-ai",
  storageBucket: "planwise-ai.appspot.com",
  messagingSenderId: "...",
  appId: "..."
};
```

---

## 5. Free Hosting Tier Characteristics & Limitations

| Constraint | Behavior on Free Hosting Tier | Recommended Workaround / Note |
|---|---|---|
| **Backend Cold Starts** | Render free web services spin down after 15 minutes of inactivity. First request takes ~45–50 seconds to wake up. | The frontend displays connection retry badges gracefully. An external uptime monitor (e.g., UptimeRobot) can ping `/api/v1/health` every 14 minutes. |
| **Ephemeral Filesystem** | On free Render instances, local SQLite database resets on restart. | Set `DATABASE_URL` to a free Render PostgreSQL database or external Supabase instance for permanent persistence. |
| **Scheduled Reminders** | Free containers cannot guarantee 24/7 background cron execution during spin-down. | The frontend uses local Service Worker and Browser Notifications API to schedule in-browser alarms independently of backend status. |
| **Memory Limits** | Free tier provides 512 MB RAM. | PlanWise AI is built ultra-lightweight: zero Docker, low-memory Python footprint (~48 MB RSS). |

---

## 6. Local Development Instructions

### Running the Backend
```bash
# From workspace root
py -3.11 -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt

# Run server with live reload
python run_server.py
# Server runs on http://localhost:8000
# OpenAPI Docs: http://localhost:8000/api/v1/docs
```

### Running the React Frontend
```bash
# In frontend directory
cd frontend
npm install
npm run dev
# Vite runs on http://localhost:5173
```

### Running Automated Verification Tests
```bash
# Run all 31 backend integration tests
py -3.11 -m pytest backend/app/tests -v
```
