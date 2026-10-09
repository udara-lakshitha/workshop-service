# Workshop Registration System

A full-stack application built for community training center workshop management, featuring role-based access control (RBAC), real-time availability filtering, and database pessimistic locking to prevent over-registration.

---

## Tech Stack
* **Backend:** FastAPI (Python) + SQLAlchemy ORM + Pydantic
* **Database:** Managed PostgreSQL (Neon DB)
* **Frontend:** React + Vite + Axios

---

## Seeded Demo Accounts
The database automatically seeds default users and initial sample workshops on startup:

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Manager** | `manager` | `manager123` |
| **Staff** | `staff` | `staff123` |

---

## Local Setup Instructions

### 1. Backend (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database seed (optional: automatic on server start)
python seed.py

# Start backend server
uvicorn app.main:app --reload --port 8000

```

### 2. Frontend
# Open a new terminal and navigate to frontend directory
cd frontend

# Install node packages
npm install

# Start development server
npm run dev

Web App URL: http://localhost:5173

### 3. Database

This is neon database
Add below lined to .env file

DATABASE_URL=postgresql://neondb_owner:npg_K8teJfn5GaLQ@ep-sweet-snow-b4cmc8xm-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
JWT_SECRET=hardcoded_secret_here
