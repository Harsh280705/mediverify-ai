# MediVerify AI

Day 1 foundation for the MediVerify AI hackathon project.

## What is included

- React + Vite frontend with Tailwind CSS, React Router, Firebase client setup, auth context, protected routes, and role-based dashboards
- FastAPI backend with modular route/service layout, Firebase Admin singleton initialization, and health endpoints
- Environment-variable driven configuration for all secrets and runtime URLs

## Run the frontend

1. `cd frontend`
2. Create a `.env` file from `.env.example`
3. Install dependencies with `npm install`
4. Start the dev server with `npm run dev`

## Run the backend

1. `cd backend`
2. Create a `.env` file from `.env.example`
3. Create a virtual environment and install dependencies from `requirements.txt`
4. Start the API with `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## Firebase setup required

- Create a Firebase project
- Enable Authentication with Email/Password
- Create Firestore and Storage in the same project
- Download a service account JSON file for the backend and point `SERVICE_ACCOUNT_PATH` to it
- Fill in the frontend Firebase client values in `frontend/.env`

## Day 1 scope

OCR, computer vision, medication verification, AI agents, reminder logic, and timeline intelligence are intentionally not implemented yet.
