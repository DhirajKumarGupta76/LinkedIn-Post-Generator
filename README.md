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

- Real AI generation is intentionally not implemented in this step.
- Authentication is basic scaffold logic only and will be expanded later.
- PostgreSQL and database integration are planned for future steps.


Terminal 1 — Backend
cd "C:\Users\Asus\OneDrive\Desktop\LinkedIn Post Generator\postgen-ai\backend"

.\.venv\Scripts\Activate.ps1

python run.py

If your project uses Flask directly instead of run.py, use:

flask run

Keep this terminal running.

You should see the Flask server on something like:

http://127.0.0.1:5000

Terminal 2 — Frontend

Open a new PowerShell:

cd "C:\Users\Asus\OneDrive\Desktop\LinkedIn Post Generator\postgen-ai\frontend"
npm install
npm run dev

You should get something like:

Local: http://localhost:5173/

Open that URL in your browser.
