# MediVerify AI - Project Summary

## Project Overview
**MediVerify AI** is an advanced, AI-powered healthcare assistant designed to tackle the global challenge of medication non-adherence. By leveraging real-time computer vision, edge-based deep learning, and robust automated scheduling, the system provides patients, caregivers, and clinicians with a secure, automated verification system. It ensures that critical medications are taken correctly, on time, and compiles detailed adherence logs to prevent complications and hospitalizations.

## Problem Statement
Medication non-adherence is a critical, multi-billion-dollar issue in modern healthcare:
* **High Hospitalization & Mortality Rates**: Approximately 30-50% of treatment failures and 125,000 deaths annually in the US are attributed to patients forgetting or choosing not to take their prescribed medicines.
* **Lack of Real-Time Auditing**: Traditional tracking systems rely on manual logs or self-reporting, which are prone to user error, forgetfulness, or intentional falsification.
* **Caregiver Burnout & Doctor Blindspots**: Families and physicians remain in the dark about actual adherence until health complications arise, as there is no real-time audit trail of compliance.

## Objectives
* **Automate Verification**: Provide real-time, vision-based verification of pill ingestion using accessible webcams on standard desktop and mobile devices.
* **Bridge the Adherence Gap**: Provide caregiver and doctor portals with real-time analytics, compliance tracking, and immediate missed-dose alerts.
* **Enhance Accessibility**: Utilize edge-compatible lightweight models (YOLOv8, EasyOCR, OpenCV skin heuristics) to support low-resource, consumer devices without requiring specialized hardware.
* **Preserve Safe Testing**: Introduce a dedicated gesture-based **Demo Mode** allowing safe sandbox validation and demonstration without repeated pill ingestion.

## Major Features
* **Dual Adherence Verification Strategies**:
  * **Production Mode**: Employs computer vision (YOLOv8 person/object detection, HSV skin-color contours, and grayscale adaptive mouth contrast) to verify actual tablet ingestion (tablet disappearing from mouth followed by swallowing confirmation).
  * **Demo Mode**: Utilizes an advanced gesture sequence state machine to simulate pill ingestion safely, requiring hand-to-mouth movement, hand-retreat, and optional mouth-closed verification, smoothed with noise-filtering hysteresis counters.
* **AI Medication Guide (LLM Integration)**: Integrates local Ollama models (defaulting to `qwen3:8b`) to instantly generate clear, patient-friendly summaries of newly uploaded prescriptions (strength, timing, dosage, warnings) stored in a Firestore cache.
* **Doctor & Caregiver Dashboards**: Allows clinicians and family members to link patients via email, view real-time adherence charts, run compliance audits, and see automated high-risk compliance alerts (raised if missed doses $\ge 2$).
* **Prescription OCR & Extraction**: Simplifies onboarding by allowing patients to upload prescription images, extracting raw text via EasyOCR, and using Ollama to parse structured JSON medication parameters.

## Technology Stack
* **Frontend**: React, React Router, TailwindCSS, Axios, HTML5 Canvas.
* **Backend**: FastAPI (Python), Uvicorn.
* **Database & Auth**: Google Cloud Firestore, Firebase Admin SDK.
* **AI & Computer Vision**:
  * **Ultralytics YOLOv8**: Real-time object detection (used for person and container/bottle detection).
  * **EasyOCR & RapidFuzz**: OCR text extraction and fuzzy string matching.
  * **OpenCV Skin Segmentations**: Hand tracking and head bounding box cropping inside body regions.
  * **Grayscale Contrast Metrics**: Real-time mouth open/closed status detection.
  * **Ollama (Qwen3:8b)**: Structured prescription JSON extraction and patient medication summary generation.

## Current Project Status
The project is **feature-complete** and fully functional:
* All APIs (Authentication, User Profiles, Documents OCR/Parsing, Reminders, Analytics, Verification, Monitoring, Health check) are integrated and running.
* Interactive dashboards for Patients, Doctors, and Caregivers are deployed.
* The sequential state machine and dual verification strategies (Production and Demo) are fully implemented.
* Local Ollama summaries are cached in Firestore for performance efficiency.
* Client-side motion detection limits backend workload.

## Hackathon Value Proposition
MediVerify AI addresses a high-impact real-world challenge with a functional, production-ready solution. It combines advanced AI verification with accessible web UI/UX, solving patient forgetfulness and providing physicians with reliable data. Features like the safe, interactive **Demo Mode** ensure judges and developers can safely experience and test the adherence tracking loop.
