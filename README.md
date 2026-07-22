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

## YOLO-Based Vision System (Migration from MediaPipe)

The real-time computer vision verification pipeline has been migrated from MediaPipe to a YOLOv8-based model (`yolov8n.pt`).

### Key Details
- **MediaPipe Removal**: MediaPipe Hands and Face Mesh have been completely removed due to the deprecation of the legacy Solutions API in modern runtimes, causing import and build failures.
- **YOLOv8 Selection**: YOLOv8 provides extremely fast and lightweight object detection and person bounding boxes. 
- **Singleton Model Manager & Caching**: A unified `YOLOModelManager` lazy-loads the model and caches predictions for each unique image frame. This prevents redundant model executions and allows Tablet, Hand, and Face trackers to share a single inference pass.
- **OpenCV Fallback**: Retained OpenCV color/shape heuristics as a secondary backup. If YOLOv8 is unavailable or doesn't detect a person/object, the trackers gracefully fall back to the OpenCV implementation to prevent crashes.

