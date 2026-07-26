# 💊 MediVerify AI

**MediVerify AI** is an experimental AI and Computer Vision-based medication adherence prototype developed for **HackVenture 2026**.

The project explores whether AI can go beyond traditional medication reminders by analysing the medication-taking workflow using **Computer Vision, OCR, local LLMs, and adherence tracking**.

> ⚠️ **Disclaimer:** This is an experimental proof-of-concept built for learning, testing, and demonstration purposes only. It is **not a medical device, clinically validated system, or healthcare product**, and does not provide conclusive proof of medication ingestion.

---

## 🚀 Features

- 📄 Prescription processing using **EasyOCR**
- 🤖 Structured prescription extraction using **Ollama + Qwen3:8b**
- 💊 Medicine matching using **RapidFuzz + `medicines.json`**
- ⏰ Automatic medication schedules and reminders
- 👁️ Computer Vision verification using **YOLOv8 + OpenCV**
- 🔄 Sequential verification using a custom **state machine**
- 🧪 Production and safe **Demo verification modes**
- 📊 Medication adherence analytics and history
- 👤 Patient, Doctor, and Caregiver dashboards
- 🔥 Firebase Authentication and Cloud Firestore

---

## 🛠️ Tech Stack

**Frontend:** React, JavaScript/JSX, Tailwind CSS, Vite  
**Backend:** Python, FastAPI, Uvicorn  
**AI / Computer Vision:** YOLOv8, OpenCV, EasyOCR, RapidFuzz  
**Local LLM:** Ollama + Qwen3:8b  
**Database & Authentication:** Firebase Authentication, Cloud Firestore

---

## ⚙️ How to Run

### Prerequisites

Install **Python 3.10/3.11, Node.js, Git, and Ollama**.

### 1. Clone & Setup Backend

```powershell
git clone https://github.com/Harsh280705/mediverify-ai.git
cd mediverify-ai/backend

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` using `.env.example` and configure your Firebase credentials.

Place your Firebase service account at:

```text
backend/firebase/serviceAccount.json
```

### 2. Setup Ollama

```powershell
ollama pull qwen3:8b
```

Make sure Ollama is running.

### 3. Run Backend

```powershell
uvicorn main:app --reload
```

Backend: `http://127.0.0.1:8000`

### 4. Run Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

---


## ⚠️ Current Limitations

- Computer Vision verification is experimental and cannot conclusively prove medication ingestion.
- Prescription extraction accuracy depends on image quality.
- Printed/digital prescriptions currently provide better results than difficult handwritten prescriptions.
- Local reminders require the application to be running.
- Doctor/Caregiver and Patient linking currently requires manual configuration.

---

## HackVenture 2026

MediVerify AI was developed as a team project for **HackVenture 2026 proof-of-concept** exploring the integration of:

**Computer Vision + OCR + Local LLMs + Web Development + Cloud Data + Real-Time Analytics**

User Flow of the Project:
<img width="1024" height="1536" alt="User Flow" src="https://github.com/user-attachments/assets/3ae92736-5601-425d-abcc-304c90a14773" />
