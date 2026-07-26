# Running Steps - MediVerify AI Setup Guide

This document provides complete, step-by-step setup and running instructions for a developer setting up both the frontend client and the backend server.

---

## 📋 Prerequisites

Ensure you have the following installed:
1. **Python**: Version `3.10` or `3.11` (recommended to avoid dependency issues with compiled vision libraries).
2. **Node.js**: Version `18.x` or `20.x` (LTS versions are recommended).
3. **C++ Build Tools**: Required for compiling custom C-based python packages (like OpenCV and EasyOCR components).
4. **Git**: For version control.
5. **Local LLM Engine**: **Ollama** installed on your system.

---

## 🔥 Firebase Setup

The application uses Google Cloud Firestore for its database. A pre-configured project `mediverify-ai-d4c68` has been initialized:
* **Service Account Key**: Located at `backend/firebase/serviceAccount.json`.
* **Frontend Config**: Already populated in `frontend/.env`.

---

## ⚙️ Environment Variables

### Backend Configuration (`backend/.env`)
Create or verify the file `backend/.env` containing:
```env
SERVICE_ACCOUNT_PATH=firebase/serviceAccount.json
PROJECT_ID=mediverify-ai-d4c68
VERIFICATION_MODE=production
```
* *To test Demo verification, change `VERIFICATION_MODE` to `demo`.*

### Frontend Configuration (`frontend/.env`)
Create or verify the file `frontend/.env` containing:
```env
VITE_BACKEND_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=AIzaSyCcUOsaXs-0xRBk6PX1raIBhjjtVWaEFRo
VITE_AUTH_DOMAIN=mediverify-ai-d4c68.firebaseapp.com
VITE_PROJECT_ID=mediverify-ai-d4c68
VITE_STORAGE_BUCKET=mediverify-ai-d4c68.firebasestorage.app
VITE_APP_ID=1:192546472857:web:5b3af35cb522f877668908
```

---

## 🛠️ Installation & Dependency Setup

### 1. Backend Server Setup
Open a terminal at the project root (`mediverify-ai/`) and run:

```powershell
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows Powershell:
.\venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate

# Install required Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Frontend Client Setup
Open a new terminal at the project root (`mediverify-ai/`) and run:

```powershell
# Navigate to the frontend directory
cd frontend

# Install node dependencies
npm install
```

---

## 🚀 Running the Project

### Step 1: Start Ollama & Download LLM
Make sure Ollama is installed and running, then pull the default model used for prescription parsing and patient summaries:

```powershell
# In a shell command prompt:
ollama pull qwen3:8b
```

### Step 2: Run the Backend API Server
With your Python virtual environment activated inside the `backend` directory, start the server:

```powershell
# In the activated backend virtual environment terminal:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
* The API documentation will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Step 3: Run the Frontend Client
In your frontend terminal:

```powershell
# Run the Vite development server:
npm run dev
```
* Open your browser and navigate to: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing System Modules & Flows

### 1. User Registration & Authentication
1. Go to [http://localhost:5173](http://localhost:5173).
2. Click **Register** to create a new user. Select a role:
   * **Patient**: To upload prescriptions and verify medications.
   * **Doctor**: To assign/link patient panels and monitor alerts.
   * **Caregiver**: To monitor linked patient schedules.
3. Sign in to access your role-specific dashboard.

### 2. Prescription Upload & OCR Extraction (Patient Flow)
1. Log in as a **Patient**.
2. Click **Upload Prescription** from the dashboard.
3. Drag & drop or select a prescription image.
4. Click **Upload & Process**. The backend:
   * Runs EasyOCR text extraction.
   * Prompts Ollama with the structured JSON extraction schema.
   * Performs fuzzy matches on extracted drug names against the `medicines.json` primary database.
5. The frontend redirects to the **Review Prescription** page. Review the medications list (medicine name, strength, dosage frequency, timings, and duration).
6. Click **Confirm Prescription**. Firestore writes the active medications list and schedules daily slots starting from today.

### 3. Testing Reminder Alerts
1. Log in as a **Patient**.
2. Go to **Reminder Settings**. You can modify default slot times (Morning: 08:00, Afternoon: 14:00, Evening: 19:00, Night: 22:00) and reminder advance time (default 15 minutes).
3. The system checks pending schedules against `current_time + remindBeforeMinutes`. If a dose is due, the frontend triggers a notification banner.

### 4. Running Vision Verification

#### A. Production Mode (Real Ingestion Verification)
Ensure `VERIFICATION_MODE=production` in `backend/.env` and restart the backend server.
1. On the Patient Dashboard, click **Verify** next to a pending medication.
2. Grant camera permissions. The scanning HUD overlay will render.
3. **Scan Sequence**:
   * **Medicine Visible**: Hold the medicine package (strip/bottle/cup) in front of the camera. The OCR engine reads the text and fuzzy matches it against the expected drug name.
   * **Hand Detected**: Bring your hand into the frame.
   * **Hand Approaching Mouth**: Move your hand (holding the pill) toward your mouth.
   * **Tablet Near Mouth & Mouth Open**: Bring the hand close to your mouth and open your mouth.
   * **Tablet Disappeared**: Remove your hand from your mouth. The medicine must no longer be visible.
   * **Mouth Closed & Swallowing Confirmation**: Close your mouth. Wait for the 1.5-second confirmation delay.
   * **Taken**: Adherence success triggers, the Firestore schedule status updates to `Taken` with the final confidence percentage, and the page redirects.

#### B. Demo Mode (Gesture Sandbox Verification)
Change `VERIFICATION_MODE=demo` in `backend/.env` and restart the backend server.
1. On the Patient Dashboard, click **Verify** next to a pending medication.
2. The amber banner "Demo Mode - Gesture-Based Verification" will appear.
3. **Gesture Steps**:
   * **Medicine Visible**: Hold any object in front of the camera to trigger the text match/detection.
   * **Hand Picked**: Bring your hand into view.
   * **Hand Approaching**: Move your hand toward your face (distance $< 0.40$).
   * **Tablet Near Mouth**: Move your hand close to your mouth region (distance $< 0.28$) and hold it there for at least **0.8 seconds** (consecutive frames hysteresis).
   * **Tablet Disappeared**: Move your hand away from your mouth.
   * **Mouth Closed**: Keep your mouth closed. After a **1.0-second** confirmation delay, verification triggers success. The database is updated, and the page redirects.

### 5. Compliance Analytics
* Log in as a **Patient**.
* Click **Analytics** in the navbar to check compliance charts, weekly/monthly adherence rates, and current/longest compliance streaks.

### 6. Doctor Audit Panels & Alerts
1. Register/Log in as a **Doctor**.
2. Click **Link Patient** and input the email of the Patient registered in Step 1.
3. Click **Run Adherence Audit** (triggers `POST /api/monitoring/run` on the backend).
4. The background daemon scans patient compliance. If a linked patient has $\ge 2$ missed doses (Pending doses that are $> 2$ hours past due), an active high-risk warning document is added to the `doctor_alerts` collection.
5. Review the active high-risk alerts table on the Doctor Dashboard.

---

## 🔍 Common Troubleshooting

* **Webcam Access Blocked**: Modern browsers block webcam streams on non-secure origins. Ensure you access the client via `http://localhost:5173` or `http://127.0.0.1:5173`.
* **FastAPI Connection Errors**: Ensure `VITE_BACKEND_URL` in `frontend/.env` matches the backend host (default: `http://localhost:8000`).
* **Firebase Credentials Error**: Check that the `SERVICE_ACCOUNT_PATH` environment variable in `backend/.env` points to the correct location of `serviceAccount.json`.
* **Ollama Connection Refused**: Confirm that the Ollama application is running on your system, and that `ollama list` shows the requested `qwen3:8b` model.
