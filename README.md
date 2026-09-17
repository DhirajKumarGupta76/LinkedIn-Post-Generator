# PostGen AI — AI LinkedIn Post Generator

PostGen AI is a production-ready project foundation for an AI-powered LinkedIn post generator. This step focuses on clean architecture, reusable UI components, and a working frontend/backend scaffold without implementing the real AI generation flow or database integration yet.

## Tech Stack

### Frontend
- React.js
- JavaScript
- Vite
- Tailwind CSS
- React Router
- Axios
- Lucide React

### Backend
- Python
- Flask
- Flask-CORS

## Project Structure

```text
postgen-ai/
├── frontend/
├── backend/
├── README.md
├── .gitignore
├── docker-compose.yml
└── .env.example
```

## Installation

### 1. Clone the project

```bash
git clone <repository-url>
cd postgen-ai
```

### 2. Frontend setup

```bash
cd frontend
npm install
```

### 3. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Frontend Commands

From the `frontend/` directory:

```bash
npm install
npm run dev
npm run build
npm run preview
```

## Backend Commands

From the `backend/` directory:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Available Routes

The frontend includes the following routes:
- `/`
- `/login`
- `/register`
- `/dashboard`
- `/generate`
- `/history`
- `/saved`
- `/profile`
- `/settings`

The backend exposes:
- `GET /api/health`

## Notes

- Frontend API calls use relative `/api` by default (Vite proxy locally; Vercel rewrite in production).
- Never set `VITE_API_BASE_URL=http://localhost:5000` in Vercel — production would call localhost.
- Google Client Secret and JWT secrets belong only in backend / Vercel server env vars.

## Vercel deployment

This repo uses Vercel Services (`vercel.json`):

- `frontend/` → Vite React app
- `backend/` → Flask (`main:app`)
- `/api/*` → rewritten to the Flask service

### Required Vercel Environment Variables (Production + Preview)

Backend / shared (do **not** prefix with `VITE_`):

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_REFRESH_SECRET_KEY`
- `ENCRYPTION_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI=https://linked-in-post-generator-dhiru.vercel.app/api/auth/google/callback`
- `FRONTEND_BASE_URL=https://linked-in-post-generator-dhiru.vercel.app`
- `CORS_ORIGINS=https://linked-in-post-generator-dhiru.vercel.app,https://linked-in-post-generator-git-main-dhiru.vercel.app`
- `DATABASE_URL` (Postgres recommended; SQLite on Vercel is ephemeral under `/tmp`)
- `COOKIE_SECURE=true`
- `FLASK_ENV=production`
- Optional AI keys as needed

Frontend:

- Leave `VITE_API_BASE_URL` **unset** (uses same-origin `/api`)

### Google Cloud Console

Authorized redirect URI must exactly match:

`https://linked-in-post-generator-dhiru.vercel.app/api/auth/google/callback`

Also keep the local URI for development:

`http://localhost:5000/api/auth/google/callback`

### Local run

Terminal 1 — Backend

```bash
cd backend
.\.venv\Scripts\Activate.ps1   # Windows
python run.py
```

Terminal 2 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173/  
Backend: http://127.0.0.1:5000/api/health
