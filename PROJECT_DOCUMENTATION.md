# MediVerify AI - Comprehensive Project Documentation

MediVerify AI is an AI-powered real-time medication adherence and verification platform. It assists patients in taking the correct doses on time, validates compliance using a live camera feed via a YOLOv8-based computer vision system, and alerts caregivers and doctors of missed doses.

---

## 1. Project Overview

### Problem Statement
Medication non-adherence is a major challenge in healthcare, causing health deteriorations, hospital readmissions, and financial waste. Traditional tracking apps rely on manual self-reporting (e.g., clicking a button), which is highly prone to user forgetfulness or intentional spoofing. Elderly patients face cognitive and physical barriers when operating camera-based verification systems that require capturing photos manually.

### Motivation
To create a frictionless, secure, and automatic verification process that does not rely on manual button-pressing, ensuring high compliance fidelity and ease of use for elderly or cognitively impaired patients.

### Target Users
- **Patients**: Particularly elderly patients who need clear daily guides and automatic ingestion verification.
- **Caregivers**: Family members or home aides who need to monitor patients' compliance remotely.
- **Doctors**: Healthcare providers who require structured compliance analytics and active alerts for high-risk patients.

### Solution
MediVerify AI provides a **Google Lens-like** experience. The user simply points their camera at the medicine container or strip:
1. It automatically reads the text via **EasyOCR** and fuzzy-matches it against the expected prescription name.
2. It generates a friendly 3-line medication summary using a local **Ollama** model.
3. It tracks ingestion steps in real time: detects holding a pill, bringing it to the mouth, swallowing, and closing the mouth using a lightweight **YOLOv8** model.
4. It updates Firestore exactly once on successful verification, updating analytics and alert systems.

### Objectives
- Eliminate self-reporting bias.
- Automate compliance auditing.
- Make ingestion verification simple and automatic for patients.
- Limit LLM/inference server memory usage via caching and singleton loaders.

---

## 2. Project Features

### Patient Panel
- **Daily Schedule Dashboard**: Chronological list of today's pending and completed doses.
- **Continuous Camera Verification**: Google Lens-like HUD overlay guide showing current ingestion progress checklists.
- **Reminder Configurations**: Custom settings for morning, afternoon, evening, and bedtime reminders.
- **Analytics Panel**: Access to compliance averages and streaks.

### Caregiver Panel
- **Patient Linking**: Link patients by entering their registered email address.
- **Real-Time Audits**: Monitor compliance checklists, schedules, and analytics for linked patients.

### Doctor Panel
- **Assigned Patients View**: Assign patients to the doctor's roster.
- **High-Risk Alerts Dashboard**: Receives immediate red flags for any assigned patient who has missed $\ge 2$ consecutive doses.
- **Adherence Audits**: Trigger manual adherence scans and view patient compliance history.

### Reminder System
- **Schedule Parser**: Automatically sets up chronological morning, afternoon, evening, and bedtime calendar tasks based on the confirmed prescription.
- **Due Monitor**: Polls due schedules and triggers push/banner notifications when a dose becomes due.

### Verification Engine
- **Motion Detection**: Suppresses idle video frames, only transmitting base64 images to the backend when motion variance threshold is met.
- **Real-Time OCR & Matching**: Identifies medicine label text and maps matches to expectations.
- **Action Verification**: Tracks mouth open/closed states, hand movements, and tablet presence.
- **State Machine Integration**: Translates physical steps into state checkmarks: `WAITING` $\rightarrow$ `MEDICINE_FOUND` $\rightarrow$ `MATCHED` $\rightarrow$ `HAND_PICKED` $\rightarrow$ `TABLET_NEAR_MOUTH` $\rightarrow$ `TABLET_DISAPPEARED` $\rightarrow$ `MOUTH_CLOSED` $\rightarrow$ `TAKEN`.

### Analytics & Streaks
- Calculated dynamically from Firestore records:
  - **Current Streak**: Number of consecutive days the patient has taken all scheduled medications.
  - **Longest Streak**: Maximum streak historically achieved.
  - **Adherence Rate**: Percentage of scheduled doses marked `Taken` over a 7-day, 30-day, or custom interval.

---

## 3. Technology Stack

- **Frontend**: React + Vite, Tailwind CSS, Firebase Client SDK (Auth, Firestore)
- **Backend**: FastAPI, Uvicorn, PyTorch, TorchVision
- **Database**: Google Cloud Firestore (NoSQL database)
- **Authentication**: Firebase Authentication (Role mapping, JWT Bearer Token validation)
- **OCR Engine**: EasyOCR (PyTorch-based line extraction)
- **Computer Vision**: Ultralytics YOLOv8 (`yolov8n.pt` COCO model), OpenCV (fallback heuristics, skin segmentation, contour features)
- **Large Language Model (LLM)**: Ollama (`qwen3:8b` or local model)
- **Analytics & Fuzzy Matching**: RapidFuzz (Levenshtein-based fuzzy match score)

---

## 4. Project Folder Structure

```
mediverify-ai/
├── backend/
│   ├── api/
│   │   ├── auth.py             # Auth token verification
│   │   ├── users.py            # User linking & patient panels
│   │   ├── documents.py        # OCR & LLM prescription parser
│   │   ├── medications.py      # Medication list & schedules
│   │   ├── reminders.py        # Settings & due notification trackers
│   │   ├── verification.py     # Real-time process frame verification
│   │   ├── monitoring.py       # Doctor alert audits
│   │   └── analytics.py        # Compliance statistics
│   ├── app/
│   │   └── dependencies.py     # LRU Cached service singletons & HTTPBearer middleware
│   ├── config/
│   │   └── settings.py         # App configuration settings
│   ├── firebase/
│   │   └── firebase_admin.py   # Firebase Admin SDK init
│   ├── ocr/
│   │   ├── easyocr_engine.py   # EasyOCR wrapper
│   │   └── ocr_service.py      # Text preprocessing pipeline
│   ├── services/
│   │   ├── user_service.py     # Link/assign patient actions
│   │   ├── summary_service.py  # Ollama summaries + Firestore cache manager
│   │   ├── doctor_monitoring.py# Daemon scanning missed doses
│   │   └── analytics_service.py# Streak & compliance analytics
│   ├── verification/
│   │   └── state_machine.py    # Multi-state vision state evaluator
│   └── vision/
│       ├── yolo_manager.py     # Singleton YOLOv8 loader & inference cache
│       ├── hand_tracking.py    # YOLOv8 Person box + skin check / OpenCV fallback
│       ├── tablet_tracking.py  # YOLOv8 Object box + shape check / OpenCV fallback
│       └── face_tracking.py    # YOLOv8 Head box + mouth contrast / OpenCV fallback
└── frontend/
    └── src/
        ├── components/
        │   ├── LiveCamera.jsx   # HUD camera capture handler
        │   └── PageShell.jsx    # Sidebar container layout
        ├── contexts/
        │   └── AuthContext.jsx  # Firebase registration and user profiles
        ├── pages/
        │   ├── Login.jsx / Register.jsx
        │   ├── PatientDashboard.jsx
        │   ├── CaregiverDashboard.jsx
        │   ├── DoctorDashboard.jsx
        │   ├── PatientAnalytics.jsx
        │   └── VerifyMedicine.jsx
        ├── routes/
        │   └── AppRouter.jsx    # Role-based route protectors
        ├── services/
        │   ├── api.js           # Axios interceptors with Bearer token injector
        │   └── analyticsService.js
        └── utils/
            └── constants.js     # Global routes and roles dictionary
```

---

## 5. Complete System Architecture

### Frontend Architecture
- The React client uses **Firebase Client SDK** for auth persistence. On login, the user profile is fetched, and user roles (`patient`, `caregiver`, `doctor`) dictate dashboard views.
- **Axios Interceptors** intercept every outgoing request to verify credentials and inject the token as a Bearer authorization header.
- **VerifyMedicine.jsx** uses `LiveCamera.jsx` to process the local stream. It computes frame pixel variance on a hidden canvas. If motion is detected, it triggers a backend frame processing task.

### Backend Architecture
- A **FastAPI** web framework processes requests. The `HTTPBearer` security middleware ensures that tokens are decrypted via Firebase Admin SDK.
- **Service Dependency Singletons**: Large vision loaders (YOLO, EasyOCR) are lazy-loaded on request and cached in memory using Python's `@lru_cache` decorators.

### YOLO Vision Pipeline Architecture
- **YOLOModelManager**: Lazy loads `yolov8n.pt` and caches results. Because tablet tracking, hand tracking, and face tracking process the same image during a single frame request, the manager intercepts calls and serves cached predictions, avoiding duplicate forward passes.
- **Trackers**:
  - **Tablet Tracker**: Maps YOLO classes (`bottle`, `cup`, `bowl`) to represent pill containers and utilizes OpenCV shape features (circularity, aspect ratio) to isolate individual pills and medicine strips.
  - **Face Tracker**: Crops the top 35% of the YOLO person detection box as the face region. Finds the mouth ROI (lower 1/3 of face region) and measures pixel intensities to check if the mouth is open/closed.
  - **Hand Tracker**: Restricts skin detection to the body bounding box region. Medium skin contours are evaluated, and palm centroids are returned.
  - **OpenCV Fallbacks**: If YOLO is offline, all trackers fall back to independent skin/shape contour check logic.

### Firestore Database Model
- **NoSQL Documents**:
  - `users`: Tracks custom profile details (role, email, assignedPatients, linkedPatients).
  - `medications`: Stores patients' confirmed prescription details.
  - `schedules`: Stores calendar items for daily doses (status, takenAt, scheduledDateTime).
  - `summaries_cache`: Caches Ollama generated guides.
  - `doctor_alerts`: Tracks patient alert details.

### Authentication Architecture
- Restricts users using Firebase tokens. Role boundaries verify relationships:
  - Patients can only view/verify their own schedules.
  - Caregivers/Doctors can only query linked patient profiles.

### Reminder & Daemon Monitoring Architecture
- **Audit Daemon**: Starts automatically on backend startup. Every 30 minutes, it queries pending schedules. If a schedule is older than 2 hours and pending, `missedCount` is incremented. If `missedCount >= 2`, a document is created in `doctor_alerts` with high-risk status.

---

## 6. Detailed Working & Data Flow

### Step 1: User Registration & Login
1. User registers or logs in via [Register.jsx](file:///d:/PROJECTS/HackVenture/mediverify-ai/frontend/src/pages/Register.jsx) or [Login.jsx](file:///d:/PROJECTS/HackVenture/mediverify-ai/frontend/src/pages/Login.jsx).
2. The user profile is written to the `users` collection.
3. Upon login, `AppRouter` redirects the user based on role mapping (e.g. `/patient`, `/caregiver`, `/doctor`).

### Step 2: Prescription Upload & Schedule Generation
1. The patient uploads a prescription PDF or image.
2. **OCR Parsing**: [documents.py](file:///d:/PROJECTS/HackVenture/mediverify-ai/backend/api/documents.py) performs OCR on the document, returning text segments.
3. **LLM Extraction**: Ollama extracts structured medication information (name, dosage, strength, times).
4. **Schedule Generation**: The patient confirms the medications list, which generates schedule items for the next 7 days in the `schedules` collection.

### Step 3: Verification & continuous camera processing
1. Patient enters [VerifyMedicine.jsx](file:///d:/PROJECTS/HackVenture/mediverify-ai/frontend/src/pages/VerifyMedicine.jsx) for a pending daily schedule item.
2. The client-side motion canvas checks pixel differences.
3. If movement occurs, `POST /api/verification/{scheduleId}/process-frame` is called.
4. **Inference Pipeline**:
   - EasyOCR reads medicine box label text.
   - RapidFuzz matches text against schedule medication. If match $\ge 70$, transitions `MATCHED` state.
   - `YOLOModelManager` executes a single inference pass.
   - Hand tracker isolates the person box and locates palm centroids.
   - Face tracker crops face region, estimates head direction, and calculates mouth open/closed state.
   - State machine updates state sequence, adding confidence weight.
   - If `MATCHED` is reached, Ollama checks cache and prints a 3-line description of the pill.
5. **Ingestion Success**:
   - Ingestion sequence complete: state hits `TAKEN` (confidence $\ge 80\%$).
   - Firestore `schedules/{scheduleId}` is updated exactly once to status `Taken`.
   - The UI shows a success card and redirects the patient back to the dashboard.

### Step 4: Compliance Audits
1. Missed schedule audits run. If any patient misses $\ge 2$ consecutive doses, an alert is added to `doctor_alerts`.
2. The physician loads [DoctorDashboard.jsx](file:///d:/PROJECTS/HackVenture/mediverify-ai/frontend/src/pages/DoctorDashboard.jsx), views the red flag alert, and analyses patient analytics.

---

## 7. API Documentation

### Auth Routes
- `POST /api/auth/verify-token`
  - **Payload**: `{"id_token": "firebase_token"}`
  - **Response**: `{"valid": true, "claims": {...}}`
  - **Purpose**: Validates incoming Firebase auth tokens.

### User Routes
- `GET /api/users/{uid}`
  - **Response**: User profile data.
  - **Purpose**: Get user details.
- `POST /api/users/{uid}`
  - **Payload**: User profile updates.
  - **Response**: Updated user profile.
  - **Purpose**: Create/update profile.
- `POST /api/users/link-patient`
  - **Payload**: `{"patientEmail": "email"}`
  - **Response**: Linked patient status.
  - **Authentication**: Caregiver or Doctor role.
- `GET /api/users/linked-patients`
  - **Response**: List of linked patients.
  - **Authentication**: Caregiver or Doctor role.

### Document Routes
- `POST /api/documents/upload`
  - **Payload**: FormFile (PDF/Image)
  - **Response**: `{"text": "extracted raw text"}`
  - **Purpose**: Simple OCR processing.
- `POST /api/documents/extract`
  - **Payload**: `{"text": "raw text"}`
  - **Response**: Structured prescription JSON.
  - **Purpose**: Structured LLM extraction.
- `POST /api/documents/analyze`
  - **Payload**: FormFile (PDF/Image)
  - **Response**: Structured rule-based parsed prescription.
  - **Purpose**: Automatic parsing in one step.

### Medication Routes
- `POST /api/medications/confirm`
  - **Payload**: Confirmed medications array.
  - **Response**: Success status.
  - **Purpose**: Commit daily schedule.
- `GET /api/medications?patientId={id}`
  - **Response**: Medications list.
  - **Purpose**: Get patient meds.
- `GET /api/schedule?patientId={id}`
  - **Response**: Scheduled daily calendar list.
  - **Purpose**: Fetch daily dashboard items.

### Reminder Routes
- `POST /api/reminders/settings`
  - **Payload**: Bedtime/Morning reminder configurations.
  - **Purpose**: Configure notification times.
- `GET /api/reminders/settings?patientId={id}`
  - **Response**: Confirmed configurations.
- `GET /api/reminders/due?patientId={id}`
  - **Response**: Array of current due doses.
- `PATCH /api/reminders/{scheduleId}/notification-sent`
  - **Purpose**: Update notification flag.

### Verification Routes
- `GET /api/verification/{scheduleId}`
  - **Response**: Daily schedule details.
  - **Security**: Verifies caller own boundaries.
- `POST /api/verification/{scheduleId}/process-frame`
  - **Payload**: `{"frame": "base64", "currentState": "state", "history": [], "confidence": int}`
  - **Response**: Updated state, checklist history, current confidence, and summary.
  - **Security**: Verifies patient own boundaries.

### Monitoring Routes
- `GET /api/monitoring/alerts`
  - **Response**: Active alerts array.
  - **Security**: Restricted to doctors and caregivers.
- `POST /api/monitoring/run`
  - **Purpose**: Trigger monitoring daemon execution.

### Analytics Routes
- `GET /api/analytics/{patientId}`
  - **Response**: Compliance stats (longest streak, averages).
  - **Security**: Owner boundaries checks.

---

## 8. Firestore Schema

### Collection: `users`
- **Fields**:
  - `uid`: string (Key)
  - `email`: string
  - `name`: string
  - `role`: `'patient' | 'caregiver' | 'doctor'`
  - `assignedPatients`: array (if doctor)
  - `linkedPatients`: array (if caregiver)

### Collection: `medications`
- **Fields**:
  - `patientId`: string
  - `medicineName`: string
  - `strength`: string
  - `dosage`: string
  - `instructions`: string
  - `timing`: string

### Collection: `schedules`
- **Fields**:
  - `patientId`: string
  - `patientName`: string
  - `medicineName`: string
  - `strength`: string
  - `dosage`: string
  - `instructions`: string
  - `timing`: string
  - `scheduledDateTime`: timestamp
  - `status`: `'Pending' | 'Taken'`
  - `takenAt`: timestamp (optional)
  - `verificationConfidence`: number
  - `verificationMethod`: string
  - `notificationSent`: boolean

### Collection: `summaries_cache`
- **Fields**:
  - `medicineName`: string (Key)
  - `summary`: string
  - `cachedAt`: timestamp

### Collection: `doctor_alerts`
- **Fields**:
  - `patientId`: string
  - `patientName`: string
  - `missedCount`: number
  - `missedMedications`: array
  - `lastTaken`: timestamp
  - `adherencePercentage`: number
  - `status`: `'Active' | 'Resolved'`
  - `updatedAt`: timestamp

---

## 9. Running the Project

### Prerequisites
- **Python**: Version `3.10` or `3.11`
- **Node.js**: Version `18` or `20`
- **Ollama**: Installed and running locally.
- **Firebase**: Account credentials.

### Backend Setup
1. Open a terminal in `backend/` directory.
2. Initialize virtual environment and activate it:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install packages:
   ```powershell
   pip install -r requirements.txt
   ```
4. Create `backend/.env` with your Firestore configuration:
   ```env
   PROJECT_ID=mediverify-ai
   SERVICE_ACCOUNT_PATH=firebase/serviceAccount.json
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen3:8b
   ```
5. Place your Firebase Admin Service Account JSON file in `backend/firebase/serviceAccount.json`.
6. Start the API server:
   ```powershell
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup
1. Open a terminal in `frontend/` directory.
2. Install npm packages:
   ```bash
   npm install
   ```
3. Create `frontend/.env` with Firebase configurations:
   ```env
   VITE_BACKEND_URL=http://127.0.0.1:8000
   VITE_FIREBASE_API_KEY=your_key
   VITE_FIREBASE_AUTH_DOMAIN=your_auth
   VITE_FIREBASE_PROJECT_ID=mediverify-ai
   VITE_FIREBASE_STORAGE_BUCKET=your_bucket
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender
   VITE_FIREBASE_APP_ID=your_app
   ```
4. Start the server:
   ```bash
   npm run dev
   ```

### Running Ollama Locally
1. Download Ollama from [ollama.com](https://ollama.com).
2. Pull the model weights:
   ```bash
   ollama pull qwen3:8b
   ```

### Troubleshooting
- **YOLOv8 downloads model**: YOLO downloads `yolov8n.pt` on its first invocation. Make sure internet access is active.
- **MediaPipe removed**: Rest assured, no MediaPipe packages are needed or will compile. If YOLOv8 is not functional or loaded, the system automatically triggers the secondary OpenCV-based segmentation fallback to handle detections.

---

## 10. Deployment Notes

- **Environment variables**: Use production Firebase configurations on the client. Keep the service account JSON key secure on the backend.
- **Production Server**: Replace the uvicorn reload command with a production WSGI/ASGI wrapper (e.g. gunicorn with uvicorn workers).
- **CORS Configuration**: Allow only verified production domains instead of wildcards in backend middleware.
- **Performance Optimizations**: Frame caching on the backend and client-side canvas throttlers keep CPU load and bandwidth requirements to a minimum.

---

## 11. Known Limitations

- **Lighting & Distance**: Poor illumination or excessive camera distance can reduce HSV skin segmenter accuracy and YOLO bounding box confidence.
- **CPU Inference Speed**: Large EasyOCR models on CPUs can take 1.5–2 seconds. Running on GPU architectures is recommended for fluid 15 FPS tracking.

---

## 12. Future Improvements

- **Pose Landmark Hand Shape Analysis**: Implementing advanced hand pose models (such as YOLOv8 Pose model fine-tuned for hands) to track individual finger gestures.
- **Edge Deployment**: Compiling YOLO to ONNX and running inference directly on the client side using WebGL or WebAssembly to eliminate server frame bandwidth requirements.

---

## 13. Hackathon Demo Guide

### Demo Scenario
Ingestion verification walkthrough of Diclofenac.

### Step-by-Step Script
1. **User Sign Up**:
   - Register a Patient account (`patient@test.com`, role: Patient).
2. **Prescription Upload**:
   - Upload prescription page. Confirm the daily schedule generation.
3. **Verification Page**:
   - Go back to the dashboard, click **Verify** next to the daily schedule dose.
   - Point the camera at a medicine bottle.
   - **Explain**: EasyOCR scans text, RapidFuzz fuzzy-matches "Diclofenac", and Ollama prints the 3-line pill description.
   - **Verification sequence**: Hold the bottle (state: `HAND_PICKED`), bring it close to the mouth (state: `TABLET_NEAR_MOUTH`), simulate ingestion and close mouth (state: `MOUTH_CLOSED`).
   - Glowing green checkmark overlay appears; user is redirected to dashboard.
   - Verify status is now `Taken`.
4. **Physician Monitoring**:
   - Register Doctor account (`doctor@test.com`, role: Doctor).
   - Link the patient using `patient@test.com`.
   - View weekly compliance averages.
   - Run audit trigger manually; missed doses create active flags instantly.
