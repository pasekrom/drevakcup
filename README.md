# Drevak Cup - IIHF Tournament Prediction Platform

Django REST Framework backend and Vue.js frontend for tournament predictions and leaderboard.

## Architecture

- **Backend**: Django REST Framework API (`backend/`)
- **Frontend**: Vue.js 3 + Vite + Tailwind CSS (`frontend/`)
- **Database**: PostgreSQL
- **Authentication**: Django session auth (Keycloak-ready)

## Project structure

```
drevakcup/
├── backend/          # Django REST API
│   ├── api/          # Main API app
│   ├── config/      # Django settings
│   └── manage.py
├── frontend/         # Vue.js application
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   └── services/
│   └── package.json
├── media/            # Uploaded files (optional, backend has its own media/)
└── README.md
```

## Quick start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 12+

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # edit with DB credentials
python manage.py migrate
python manage.py runserver
```

API: `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

### Backend .env (in `backend/`)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=drevakcup
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## API docs

- Swagger: `http://localhost:8000/api/docs/`
- Schema: `http://localhost:8000/api/schema/`

## Features

- Match tips and special (tournament) tips
- Leaderboard and team statistics
- User profile (name, avatar, password change)
- Admin: cups, matches, results, point calculation

## License

Same as original project.
