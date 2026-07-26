# Production Verification Logic

This document describes the complete medication verification logic of MediVerify AI. It details the internal state machine, evidence collection parameters, and confidence engine scoring.

## Complete Production State Machine

MediVerify AI uses a sequential state machine to verify that a patient has taken their medication. The state machine monitors a stream of camera frames, performs vision-based and text-based detections, aggregates evidence, and updates internal state tracking.

### Internal States and Sequence
The state machine transitions sequentially through the following internal states:

1. **`WAITING`**: The initial state. The system is waiting for the medication to be held up.
2. **`MEDICINE_VISIBLE`**: The prescribed medicine is detected in the frame.
3. **`HAND_DETECTED`**: A hand is detected in the frame.
4. **`HAND_APPROACHING_MOUTH`**: The hand moves toward the mouth region (distance threshold < 0.40).
5. **`TABLET_NEAR_MOUTH`**: The tablet is brought extremely close to the mouth (distance threshold < 0.25).
6. **`OBJECT_DISAPPEARED`**: The medicine/tablet disappears from the camera's view (stable non-visibility) and mouth open detection is registered.
7. **`MOUTH_CLOSED`**: The mouth closes after ingestion, confirming the swallowing action.
8. **`VERIFYING`**: Verification completes checks.
9. **`TAKEN`**: Final terminal state. Adherence is confirmed, and Firestore is updated.

### Frontend State Mapping
To simplify the user interface, internal states are mapped to frontend-visible status updates:

| Internal State | Frontend State | Display Label | Description |
|---|---|---|---|
| `WAITING` | `WAITING` | Aligning camera... | Initial scan state. |
| `MEDICINE_VISIBLE` | `MEDICINE_FOUND` | Medication detected... / Checking name... | Medicine is visible. |
| `HAND_DETECTED` | `HAND_PICKED` | Hold the tablet near your mouth. | Hand detected, ready for dosage. |
| `HAND_APPROACHING_MOUTH` | `HAND_PICKED` | Hold the tablet near your mouth. | Hand moving toward mouth. |
| `TABLET_NEAR_MOUTH` | `TABLET_NEAR_MOUTH` | Take the tablet. | Medicine is close to mouth. |
| `OBJECT_DISAPPEARED` | `TABLET_DISAPPEARED` | Tablet swallowed. Close mouth to confirm. | Tablet ingested (disappeared). |
| `MOUTH_CLOSED` | `MOUTH_CLOSED` | Verification verifying... | Mouth closed after ingestion. |
| `VERIFYING` | `MOUTH_CLOSED` | Verification verifying... | Final checks running. |
| `TAKEN` | `TAKEN` | Verification complete! | Adherence recorded in DB. |

---

## Transition Rules & Stability Counter Thresholds

To prevent transient noise or false positives, transitions require a minimum number of consecutive frames meeting specific criteria:

* **To `MEDICINE_VISIBLE`**: Requires 3 consecutive frames with medicine detected (`med_cnt >= 3`). Medicine is detected if:
  * YOLO v8 detects `medicine_strip` or `medicine_box` OR
  * YOLO v8 detects a `tablet` OR
  * OCR text extraction finds a fuzzy match score $\ge 70\%$ against the prescription.
* **To `HAND_DETECTED`**: Requires 2 consecutive frames with a hand detected (`hand_cnt >= 2`) after medicine became visible.
* **To `HAND_APPROACHING_MOUTH`**: Requires 2 consecutive frames where the hand-to-mouth distance is $< 0.40$ (`approach_cnt >= 2`).
* **To `TABLET_NEAR_MOUTH`**: Requires 2 consecutive frames where the hand-to-mouth distance is $< 0.25$ (`near_cnt >= 2`).
* **To `OBJECT_DISAPPEARED`**: Requires 2 consecutive frames where the medicine is NOT visible (`disappeared_cnt >= 2`), AND mouth opening is detected at some point.
* **To `MOUTH_CLOSED`**: Requires 2 consecutive frames where the mouth is closed (`mouth_closed_cnt >= 2`), AND mouth opening was detected after medicine was visible.
* **To `TAKEN`**: Final transition occurs when the state machine reaches `MOUTH_CLOSED` / `VERIFYING` and the overall confidence score is $\ge 80\%$.

---

## Confidence Calculations

The confidence score is computed dynamically out of 100 based on three components:

1. **OCR / Text Match (Max 25%)**:
   * Computed as `best_match_score * 0.25` (where `best_match_score` is the fuzzy text similarity from RapidFuzz `WRatio` comparison between prescription and extracted text).
2. **State Sequence Verification (Max 75%)**:
   * `MEDICINE_VISIBLE` reached: +15%
   * `HAND_DETECTED` reached: +10%
   * `HAND_APPROACHING_MOUTH` reached: +10%
   * `TABLET_NEAR_MOUTH` reached: +15%
   * `OBJECT_DISAPPEARED` reached: +15%
   * `MOUTH_CLOSED` reached: +10%
3. **Mouth Opened Verification**:
   * If mouth opened after medicine visible: +15%
4. **Stability Metrics**:
   * Medicine stable ($\ge 4$ frames): +5%
   * Hand stable ($\ge 3$ frames): +5%

*Note: The combined confidence score is capped at 100%.*

---

## Timing Constraints & Failure Conditions

* **Inactivity Timeout**: If no transition occurs for 60 seconds, the sequence times out and resets to `WAITING` to prevent accidental validations.
* **Mouth Opening Validation**: If mouth closed is detected without a corresponding mouth open event after the medicine was shown, the state machine logs a warning and blocks progress to prevent simple mouth-closed bypasses.
