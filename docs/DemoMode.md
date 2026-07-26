# Safe Demo Verification Mode

This guide explains how to configure, run, and evaluate the safe Demo Verification Mode in MediVerify AI.

## Why Demo Mode Exists

For hackathon demonstrations, sandbox testing, and judging, it is not practical or safe to repeatedly ingest pills or medications. Ingestion-based tracking requires the medicine object to permanently disappear inside an open mouth, which is difficult to replicate repeatedly without actually taking medicine.

The **Demo Verification Mode** resolves this by verifying the complete gesture sequence of taking medicine without requiring actual ingestion or swallowing.

## How it Differs from Production

Both strategies run the same computer vision engines (YOLO object detection, EasyOCR text extraction, MediPipe Hand tracker, and Face Mesh trackers) to compute confidence levels, but they handle the final ingestion step differently:

| Feature / Step | Production Verification | Demo Verification |
|---|---|---|
| **OCR & Matching** | Required (prescriptions must fuzzy-match) | Required (prescriptions must fuzzy-match) |
| **Medicine Detection** | Required (YOLO checks strip/box/tablet) | Required (YOLO checks strip/box/tablet) |
| **Hand Tracking** | Required | Required |
| **Face Tracking** | Required | Required |
| **Motion Detection** | Required | Required |
| **Ingestion Event** | **Actual Ingestion Required:** The tablet must disappear from view (`not med_frame`) for stable frames. | **Simulated Ingestion:** The hand must leave the mouth area (distance $\ge 0.40$ or hand leaves frame) after approaching. |
| **Final State** | Ingestion verified → DB status update | Gestures verified → DB status update |

---

## How to Enable / Disable Demo Mode

You can configure the active verification mode via backend environment variables or configuration files. **No code changes are required.**

### Enable Demo Mode
1. Open the backend configuration file at `backend/.env`.
2. Set the `VERIFICATION_MODE` setting to `demo`:
   ```env
   VERIFICATION_MODE=demo
   ```
   *(Alternatively, you can configure `DEMO_MODE=true`)*
3. Save the file.
4. Restart the FastAPI backend server.

### Disable Demo Mode (Use Production)
1. Open the backend configuration file at `backend/.env`.
2. Set the `VERIFICATION_MODE` setting back to `production`:
   ```env
   VERIFICATION_MODE=production
   ```
   *(Ensure `DEMO_MODE=false` or remove it)*
3. Save the file.
4. Restart the FastAPI backend server.

---

## How Judges Can Evaluate It

When Demo Mode is active:
1. Navigating to the verification screen will display a prominent amber badge: **"Demo Mode - Gesture-Based Verification is active. Actual ingestion is not required."**
2. Hold up any medicine (or matching text/label).
3. The AI matches the medicine and prompts you to pick a tablet.
4. Move your hand to your mouth.
5. Bring the object/hand to your mouth region (mouth opens, and mouth opened is registered).
6. **Move your hand away from your mouth or out of the camera's sight.**
7. Close your mouth.
8. The system will detect the hand leaving, the mouth closing, and automatically verify adherence as **Taken**, updating Firestore and redirecting you to the dashboard.
