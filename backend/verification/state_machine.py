import numpy as np
import logging
import time

logger = logging.getLogger(__name__)

class VerificationStateMachine:
    STATES = [
        "WAITING",
        "MEDICINE_VISIBLE",
        "MEDICINE_FOUND",
        "MATCHED",
        "HAND_DETECTED",
        "HAND_PICKED",
        "HAND_APPROACHING_MOUTH",
        "TABLET_NEAR_MOUTH",
        "OBJECT_DISAPPEARED",
        "TABLET_DISAPPEARED",
        "MOUTH_CLOSED",
        "VERIFYING",
        "TAKEN"
    ]

    FRONTEND_TO_INTERNAL_STATE = {
        "WAITING": "WAITING",
        "MEDICINE_FOUND": "MEDICINE_VISIBLE",
        "MATCHED": "MEDICINE_VISIBLE",
        "HAND_PICKED": "HAND_DETECTED",
        "HAND_APPROACHING_MOUTH": "HAND_APPROACHING_MOUTH",
        "TABLET_NEAR_MOUTH": "TABLET_NEAR_MOUTH",
        "TABLET_DISAPPEARED": "OBJECT_DISAPPEARED",
        "OBJECT_DISAPPEARED": "OBJECT_DISAPPEARED",
        "MOUTH_CLOSED": "MOUTH_CLOSED",
        "VERIFYING": "VERIFYING",
        "TAKEN": "TAKEN"
    }

    INTERNAL_TO_FRONTEND_STATE = {
        "WAITING": "WAITING",
        "MEDICINE_VISIBLE": "MEDICINE_FOUND",
        "HAND_DETECTED": "HAND_PICKED",
        "HAND_APPROACHING_MOUTH": "HAND_PICKED",
        "TABLET_NEAR_MOUTH": "TABLET_NEAR_MOUTH",
        "OBJECT_DISAPPEARED": "TABLET_DISAPPEARED",
        "MOUTH_CLOSED": "MOUTH_CLOSED",
        "VERIFYING": "MOUTH_CLOSED",
        "TAKEN": "TAKEN"
    }

    INTERNAL_STATE_SEQUENCE = [
        "WAITING",
        "MEDICINE_VISIBLE",
        "HAND_DETECTED",
        "HAND_APPROACHING_MOUTH",
        "TABLET_NEAR_MOUTH",
        "OBJECT_DISAPPEARED",
        "MOUTH_CLOSED",
        "VERIFYING",
        "TAKEN"
    ]

    @classmethod
    def _get_timestamp(cls, history: list, state: str) -> float:
        for item in history:
            if item.startswith(f"TS:{state}:"):
                try:
                    return float(item.split(":")[-1])
                except ValueError:
                    return 0.0
        return 0.0

    @classmethod
    def _set_timestamp(cls, history: list, state: str, ts: float) -> list:
        history = [item for item in history if not item.startswith(f"TS:{state}:")]
        history.append(f"TS:{state}:{ts}")
        return history

    @classmethod
    def _get_counter(cls, history: list, key: str) -> int:
        for item in history:
            if item.startswith(f"CNT:{key}:"):
                try:
                    return int(item.split(":")[-1])
                except ValueError:
                    return 0
        return 0

    @classmethod
    def _update_counter(cls, history: list, key: str, val: int) -> list:
        history = [item for item in history if not item.startswith(f"CNT:{key}:")]
        if val > 0:
            history.append(f"CNT:{key}:{val}")
        return history

    @classmethod
    def _reset_sequence(cls, current_time: float) -> tuple:
        history = ["WAITING"]
        history = cls._set_timestamp(history, "WAITING", current_time)
        return "WAITING", history, 0

    @classmethod
    def evaluate(cls, detections: dict, current_state: str, history: list) -> tuple:
        """
        Evaluates current tracker detections and determines next state and confidence.
        detections contains:
            "ocr_lines": list[str]
            "yolo_detections": list[dict]
            "hand_detections": dict
            "face_detections": dict
            "match_percentage": float
        
        Returns:
            (new_state: str, updated_history: list, confidence: int)
        """
        try:
            if current_state == "TAKEN":
                return "TAKEN", history, 100

            current_time = time.time()

            # Determine internal state based on timestamp history
            internal_state = "WAITING"
            for s in cls.INTERNAL_STATE_SEQUENCE:
                if cls._get_timestamp(history, s) > 0.0:
                    internal_state = s

            # Initialize WAITING timestamp if not present
            ts_waiting = cls._get_timestamp(history, "WAITING")
            if ts_waiting == 0.0:
                history = [x for x in history if x in cls.STATES or x.startswith("TS:") or x.startswith("CNT:")]
                if "WAITING" not in history:
                    history.append("WAITING")
                history = cls._set_timestamp(history, "WAITING", current_time)
                ts_waiting = current_time

            # Parse timestamps
            ts_med = cls._get_timestamp(history, "MEDICINE_VISIBLE")
            ts_hand = cls._get_timestamp(history, "HAND_DETECTED")
            ts_approach = cls._get_timestamp(history, "HAND_APPROACHING_MOUTH")
            ts_near = cls._get_timestamp(history, "TABLET_NEAR_MOUTH")
            ts_disappeared = cls._get_timestamp(history, "OBJECT_DISAPPEARED")
            ts_mouth_opened = cls._get_timestamp(history, "MOUTH_OPENED")
            ts_mouth_closed = cls._get_timestamp(history, "MOUTH_CLOSED")

            # Check sequence timeout
            timestamps = [
                cls._get_timestamp(history, s)
                for s in cls.INTERNAL_STATE_SEQUENCE + ["MOUTH_OPENED"]
                if cls._get_timestamp(history, s) > 0.0
            ]
            last_transition_time = max(timestamps) if timestamps else current_time
            if current_time - last_transition_time > 60.0:
                logger.info("Verification sequence timed out. Resetting to WAITING.")
                return cls._reset_sequence(current_time)

            # Extract frame detections
            yolo_classes = [d["class"] for d in detections.get("yolo_detections", [])]
            has_strip_or_box = "medicine_strip" in yolo_classes or "medicine_box" in yolo_classes
            has_tablet = "tablet" in yolo_classes
            best_match_score = detections.get("match_percentage", 0.0)

            # Medicine visible frame evidence
            med_frame = has_strip_or_box or has_tablet or (best_match_score >= 70.0)

            # Hand detected frame evidence
            hand_detected = detections.get("hand_detections", {}).get("detected", False)
            hand_pts = detections.get("hand_detections", {}).get("landmarks", [])
            hand_frame = hand_detected

            # Face and mouth status
            face_detected = detections.get("face_detections", {}).get("detected", False)
            mouth_open = detections.get("face_detections", {}).get("mouth_open", False)
            mouth_closed = detections.get("face_detections", {}).get("mouth_closed", True)

            dist = None
            if hand_detected and face_detected and hand_pts and len(hand_pts) > 0 and len(hand_pts[0]) > 0:
                h_pt = hand_pts[0][0]
                mx, my = 0.5, 0.65
                dist = np.sqrt((h_pt["x"] - mx)**2 + (h_pt["y"] - my)**2)

            # Approaching and near mouth frame evidence
            approach_frame = (hand_detected and face_detected and dist is not None and dist < 0.40)
            near_frame = (hand_detected and face_detected and dist is not None and dist < 0.25)
            disappeared_frame = (not med_frame)
            mouth_open_frame = face_detected and mouth_open
            mouth_closed_frame = mouth_closed

            # Update stable detection counters in history
            med_cnt = cls._get_counter(history, "MEDICINE")
            med_cnt = med_cnt + 1 if med_frame else 0
            history = cls._update_counter(history, "MEDICINE", med_cnt)

            hand_cnt = cls._get_counter(history, "HAND")
            hand_cnt = hand_cnt + 1 if hand_frame else 0
            history = cls._update_counter(history, "HAND", hand_cnt)

            approach_cnt = cls._get_counter(history, "APPROACH")
            approach_cnt = approach_cnt + 1 if approach_frame else 0
            history = cls._update_counter(history, "APPROACH", approach_cnt)

            near_cnt = cls._get_counter(history, "NEAR")
            near_cnt = near_cnt + 1 if near_frame else 0
            history = cls._update_counter(history, "NEAR", near_cnt)

            disappeared_cnt = cls._get_counter(history, "DISAPPEARED")
            disappeared_cnt = disappeared_cnt + 1 if disappeared_frame else 0
            history = cls._update_counter(history, "DISAPPEARED", disappeared_cnt)

            mouth_closed_cnt = cls._get_counter(history, "MOUTH_CLOSED")
            mouth_closed_cnt = min(10, mouth_closed_cnt + 1 if mouth_closed_frame else max(0, mouth_closed_cnt - 1))
            history = cls._update_counter(history, "MOUTH_CLOSED", mouth_closed_cnt)

            # Evaluate state transitions
            next_internal_state = internal_state

            if internal_state == "WAITING":
                if med_cnt >= 3:
                    next_internal_state = "MEDICINE_VISIBLE"
                    history = cls._set_timestamp(history, "MEDICINE_VISIBLE", current_time)
                    if "MEDICINE_FOUND" not in history:
                        history.append("MEDICINE_FOUND")
                    if best_match_score >= 70.0 and "MATCHED" not in history:
                        history.append("MATCHED")
                    ts_med = current_time

            elif internal_state == "MEDICINE_VISIBLE":
                if best_match_score >= 70.0 and "MATCHED" not in history:
                    history.append("MATCHED")
                if hand_cnt >= 2:
                    if current_time > ts_med:
                        next_internal_state = "HAND_DETECTED"
                        history = cls._set_timestamp(history, "HAND_DETECTED", current_time)
                        if "HAND_PICKED" not in history:
                            history.append("HAND_PICKED")
                        ts_hand = current_time

            elif internal_state == "HAND_DETECTED":
                if approach_cnt >= 2:
                    if current_time > ts_hand:
                        next_internal_state = "HAND_APPROACHING_MOUTH"
                        history = cls._set_timestamp(history, "HAND_APPROACHING_MOUTH", current_time)
                        ts_approach = current_time

            elif internal_state == "HAND_APPROACHING_MOUTH":
                if near_cnt >= 2:
                    if current_time > ts_approach:
                        next_internal_state = "TABLET_NEAR_MOUTH"
                        history = cls._set_timestamp(history, "TABLET_NEAR_MOUTH", current_time)
                        if "TABLET_NEAR_MOUTH" not in history:
                            history.append("TABLET_NEAR_MOUTH")
                        ts_near = current_time

            elif internal_state == "TABLET_NEAR_MOUTH":
                if mouth_open_frame:
                    if ts_mouth_opened == 0.0 or current_time > ts_mouth_opened:
                        history = cls._set_timestamp(history, "MOUTH_OPENED", current_time)
                        ts_mouth_opened = current_time
                if disappeared_cnt >= 2:
                    if current_time > ts_near:
                        next_internal_state = "OBJECT_DISAPPEARED"
                        history = cls._set_timestamp(history, "OBJECT_DISAPPEARED", current_time)
                        if "TABLET_DISAPPEARED" not in history:
                            history.append("TABLET_DISAPPEARED")
                        ts_disappeared = current_time

            elif internal_state == "OBJECT_DISAPPEARED":
                if mouth_open_frame:
                    if ts_mouth_opened == 0.0 or current_time > ts_mouth_opened:
                        history = cls._set_timestamp(history, "MOUTH_OPENED", current_time)
                        ts_mouth_opened = current_time

                # Allow verification to complete when ALL of the following are true:
                # 1. Hand has moved away from the mouth
                hand_moved_away = (not hand_detected) or (dist is not None and dist >= 0.40)

                # 2. Face remains visible
                face_visible = face_detected

                # 3. No medicine/tablet is detected near the mouth region
                medicine_near_mouth = False
                for d in detections.get("yolo_detections", []):
                    if d.get("class") in ["tablet", "medicine_strip", "medicine_box"]:
                        norm_bbox = d.get("normalized_bbox")
                        if norm_bbox:
                            tx = (norm_bbox[0] + norm_bbox[2]) / 2
                            ty = (norm_bbox[1] + norm_bbox[3]) / 2
                            if np.sqrt((tx - 0.5)**2 + (ty - 0.65)**2) < 0.30:
                                medicine_near_mouth = True
                                break
                        else:
                            if d.get("class") == "tablet":
                                medicine_near_mouth = True
                                break

                conditions_met = hand_moved_away and face_visible and not medicine_near_mouth

                ts_left_mouth = cls._get_timestamp(history, "LEFT_MOUTH")

                if conditions_met:
                    if ts_left_mouth == 0.0:
                        history = cls._set_timestamp(history, "LEFT_MOUTH", current_time)
                        ts_left_mouth = current_time

                    # 4. Configurable confirmation timer (approx 1.5 seconds) has elapsed
                    CONFIRMATION_DELAY = 1.5
                    if current_time - ts_left_mouth >= CONFIRMATION_DELAY:
                        next_internal_state = "MOUTH_CLOSED"
                        history = cls._set_timestamp(history, "MOUTH_CLOSED", current_time)
                        if "MOUTH_CLOSED" not in history:
                            history.append("MOUTH_CLOSED")
                        ts_mouth_closed = current_time
                else:
                    if ts_left_mouth > 0.0:
                        history = [item for item in history if not item.startswith("TS:LEFT_MOUTH:")]
                        ts_left_mouth = 0.0

            elif internal_state == "MOUTH_CLOSED":
                next_internal_state = "VERIFYING"
                history = cls._set_timestamp(history, "VERIFYING", current_time)
                ts_verifying = current_time

            # Calculate multi-evidence confidence score
            confidence = 0.0

            # OCR Match evidence
            ocr_score = best_match_score * 0.25
            confidence += ocr_score

            # Sequential states check
            history_states = []
            for s in ["MEDICINE_VISIBLE", "HAND_DETECTED", "HAND_APPROACHING_MOUTH", "TABLET_NEAR_MOUTH", "OBJECT_DISAPPEARED", "MOUTH_CLOSED"]:
                ts = cls._get_timestamp(history, s)
                if ts > 0.0:
                    history_states.append((s, ts))

            # Order checkpoints
            sorted_history_states = sorted(history_states, key=lambda x: x[1])
            for state, ts in sorted_history_states:
                if state == "MEDICINE_VISIBLE":
                    confidence += 15
                elif state == "HAND_DETECTED":
                    confidence += 10
                elif state == "HAND_APPROACHING_MOUTH":
                    confidence += 10
                elif state == "TABLET_NEAR_MOUTH":
                    confidence += 15
                elif state == "OBJECT_DISAPPEARED":
                    confidence += 15
                elif state == "MOUTH_CLOSED":
                    confidence += 10

            # Mouth opened validation
            if ts_mouth_opened > 0.0 and ts_mouth_opened > ts_med:
                confidence += 15

            # Stability metrics
            if med_cnt >= 4:
                confidence += 5
            if hand_cnt >= 3:
                confidence += 5

            # Mouth closed detection as an additional confidence bonus
            if mouth_closed_cnt >= 2:
                confidence += 10

            final_confidence = min(100, int(round(confidence)))
            if next_internal_state in ["MOUTH_CLOSED", "VERIFYING", "TAKEN"]:
                final_confidence = max(final_confidence, 85)

            # If verification complete and confidence threshold met, transition to TAKEN
            if next_internal_state in ["MOUTH_CLOSED", "VERIFYING"] and final_confidence >= 80:
                next_internal_state = "TAKEN"
                history = cls._set_timestamp(history, "TAKEN", current_time)
                if "TAKEN" not in history:
                    history.append("TAKEN")

            # Finalize new state and history
            new_state = cls.INTERNAL_TO_FRONTEND_STATE.get(next_internal_state, "WAITING")
            history_set = set(history)
            history_set.add("WAITING")
            
            updated_history = sorted(
                list(history_set),
                key=lambda x: cls.STATES.index(x) if x in cls.STATES else 99
            )

            return new_state, updated_history, final_confidence

        except Exception as e:
            logger.exception(f"Exception in state machine evaluation: {e}")
            return current_state, history, confidence
