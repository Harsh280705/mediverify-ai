from abc import ABC, abstractmethod
import time
import logging
import numpy as np

from config.settings import get_settings
from verification.state_machine import VerificationStateMachine

logger = logging.getLogger(__name__)


class VerificationStrategy(ABC):

    @abstractmethod
    def evaluate(self, detections: dict, current_state: str, history: list) -> tuple:
        """
        Evaluates current tracker detections and determines next state and confidence.
        Returns:
            (new_state: str, updated_history: list, confidence: int)
        """
        pass

    @abstractmethod
    def is_demo_mode(self) -> bool:
        """
        Returns True if this is the demo strategy.
        """
        pass


class ProductionVerificationStrategy(VerificationStrategy):

    def evaluate(self, detections: dict, current_state: str, history: list) -> tuple:
        logger.debug("Executing Production Verification Strategy")
        return VerificationStateMachine.evaluate(detections, current_state, history)

    def is_demo_mode(self) -> bool:
        return False


class DemoVerificationStrategy(VerificationStrategy):

    def is_demo_mode(self) -> bool:
        return True

    def evaluate(self, detections: dict, current_state: str, history: list) -> tuple:
        """
        Evaluates current tracker detections using gesture-based demo strategy.
        Sequence:
          Medicine visible/matched -> Hand detected -> Hand approaching mouth -> Tablet near mouth -> Hand leaves mouth -> Mouth closes -> Success (TAKEN)
        """
        logger.debug("Executing Demo Verification Strategy")
        try:
            if current_state == "TAKEN":
                return "TAKEN", history, 100

            current_time = time.time()

            # Determine internal state based on timestamp history
            internal_state = "WAITING"
            for s in VerificationStateMachine.INTERNAL_STATE_SEQUENCE:
                if VerificationStateMachine._get_timestamp(history, s) > 0.0:
                    internal_state = s

            # Initialize WAITING timestamp if not present
            ts_waiting = VerificationStateMachine._get_timestamp(history, "WAITING")
            if ts_waiting == 0.0:
                history = [x for x in history if x in VerificationStateMachine.STATES or x.startswith("TS:") or x.startswith("CNT:")]
                if "WAITING" not in history:
                    history.append("WAITING")
                history = VerificationStateMachine._set_timestamp(history, "WAITING", current_time)
                ts_waiting = current_time

            # Parse timestamps
            ts_med = VerificationStateMachine._get_timestamp(history, "MEDICINE_VISIBLE")
            ts_hand = VerificationStateMachine._get_timestamp(history, "HAND_DETECTED")
            ts_approach = VerificationStateMachine._get_timestamp(history, "HAND_APPROACHING_MOUTH")
            ts_near = VerificationStateMachine._get_timestamp(history, "TABLET_NEAR_MOUTH")
            ts_disappeared = VerificationStateMachine._get_timestamp(history, "OBJECT_DISAPPEARED")
            ts_mouth_opened = VerificationStateMachine._get_timestamp(history, "MOUTH_OPENED")
            ts_mouth_closed = VerificationStateMachine._get_timestamp(history, "MOUTH_CLOSED")
            
            # Custom timestamps for Demo Mode
            ts_near_start = VerificationStateMachine._get_timestamp(history, "NEAR_START")
            ts_left_mouth = VerificationStateMachine._get_timestamp(history, "LEFT_MOUTH")

            # Check sequence timeout
            timestamps = [
                VerificationStateMachine._get_timestamp(history, s)
                for s in VerificationStateMachine.INTERNAL_STATE_SEQUENCE + ["MOUTH_OPENED"]
                if VerificationStateMachine._get_timestamp(history, s) > 0.0
            ]
            last_transition_time = max(timestamps) if timestamps else current_time
            if current_time - last_transition_time > 60.0:
                logger.info("Demo Verification sequence timed out. Resetting to WAITING.")
                return VerificationStateMachine._reset_sequence(current_time)

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
            if hand_detected and hand_pts and len(hand_pts) > 0 and len(hand_pts[0]) > 0:
                h_pt = hand_pts[0][0]
                mx, my = 0.5, 0.65
                dist = np.sqrt((h_pt["x"] - mx)**2 + (h_pt["y"] - my)**2)

            # Approaching and near mouth frame evidence (do not require face_detected to be True to avoid occlusion lockups)
            approach_frame = (hand_detected and dist is not None and dist < 0.40)
            near_frame = (hand_detected and dist is not None and dist < 0.28)
            
            # Hand leaves mouth (either hand disappears or moves far from mouth region)
            hand_left_mouth_frame = (not hand_detected) or (dist is not None and dist >= 0.40)
            
            mouth_open_frame = face_detected and mouth_open
            mouth_closed_frame = mouth_closed

            # Update stable detection counters in history using hysteresis to filter noise
            med_cnt = VerificationStateMachine._get_counter(history, "MEDICINE")
            med_cnt = min(10, med_cnt + 1 if med_frame else max(0, med_cnt - 1))
            history = VerificationStateMachine._update_counter(history, "MEDICINE", med_cnt)

            hand_cnt = VerificationStateMachine._get_counter(history, "HAND")
            hand_cnt = min(10, hand_cnt + 1 if hand_frame else max(0, hand_cnt - 1))
            history = VerificationStateMachine._update_counter(history, "HAND", hand_cnt)

            approach_cnt = VerificationStateMachine._get_counter(history, "APPROACH")
            approach_cnt = min(10, approach_cnt + 1 if approach_frame else max(0, approach_cnt - 1))
            history = VerificationStateMachine._update_counter(history, "APPROACH", approach_cnt)

            near_cnt = VerificationStateMachine._get_counter(history, "NEAR")
            near_cnt = min(10, near_cnt + 1 if near_frame else max(0, near_cnt - 1))
            history = VerificationStateMachine._update_counter(history, "NEAR", near_cnt)

            # Stable hand left mouth counter
            hand_left_cnt = VerificationStateMachine._get_counter(history, "HAND_LEFT")
            hand_left_cnt = min(10, hand_left_cnt + 1 if hand_left_mouth_frame else max(0, hand_left_cnt - 1))
            history = VerificationStateMachine._update_counter(history, "HAND_LEFT", hand_left_cnt)

            # Mouth closed counter
            mouth_closed_cnt = VerificationStateMachine._get_counter(history, "MOUTH_CLOSED")
            mouth_closed_cnt = min(10, mouth_closed_cnt + 1 if mouth_closed_frame else max(0, mouth_closed_cnt - 1))
            history = VerificationStateMachine._update_counter(history, "MOUTH_CLOSED", mouth_closed_cnt)

            # Evaluate state transitions
            next_internal_state = internal_state

            if internal_state == "WAITING":
                if med_cnt >= 4:
                    next_internal_state = "MEDICINE_VISIBLE"
                    history = VerificationStateMachine._set_timestamp(history, "MEDICINE_VISIBLE", current_time)
                    if "MEDICINE_FOUND" not in history:
                        history.append("MEDICINE_FOUND")
                    if best_match_score >= 70.0 and "MATCHED" not in history:
                        history.append("MATCHED")
                    ts_med = current_time

            elif internal_state == "MEDICINE_VISIBLE":
                if best_match_score >= 70.0 and "MATCHED" not in history:
                    history.append("MATCHED")
                if hand_cnt >= 3:
                    if current_time > ts_med:
                        next_internal_state = "HAND_DETECTED"
                        history = VerificationStateMachine._set_timestamp(history, "HAND_DETECTED", current_time)
                        if "HAND_PICKED" not in history:
                            history.append("HAND_PICKED")
                        ts_hand = current_time

            elif internal_state == "HAND_DETECTED":
                if approach_cnt >= 3:
                    if current_time > ts_hand:
                        next_internal_state = "HAND_APPROACHING_MOUTH"
                        history = VerificationStateMachine._set_timestamp(history, "HAND_APPROACHING_MOUTH", current_time)
                        ts_approach = current_time

            elif internal_state == "HAND_APPROACHING_MOUTH":
                if near_cnt >= 3:
                    if current_time > ts_approach:
                        next_internal_state = "TABLET_NEAR_MOUTH"
                        history = VerificationStateMachine._set_timestamp(history, "TABLET_NEAR_MOUTH", current_time)
                        if "TABLET_NEAR_MOUTH" not in history:
                            history.append("TABLET_NEAR_MOUTH")
                        ts_near = current_time
                        # Record starting time of remaining near mouth
                        history = VerificationStateMachine._set_timestamp(history, "NEAR_START", current_time)
                        ts_near_start = current_time

            elif internal_state == "TABLET_NEAR_MOUTH":
                if mouth_open_frame:
                    if ts_mouth_opened == 0.0 or current_time > ts_mouth_opened:
                        history = VerificationStateMachine._set_timestamp(history, "MOUTH_OPENED", current_time)
                        ts_mouth_opened = current_time
                
                # Check that hand has remained briefly in the mouth region (0.7–1.5 seconds, we choose 0.8 seconds)
                if ts_near_start == 0.0:
                    history = VerificationStateMachine._set_timestamp(history, "NEAR_START", current_time)
                    ts_near_start = current_time
                
                hand_remained_briefly = (current_time - ts_near_start >= 0.8)
                
                # Transition to OBJECT_DISAPPEARED on hand leaving mouth
                if hand_remained_briefly and hand_left_cnt >= 3:
                    if current_time > ts_near:
                        next_internal_state = "OBJECT_DISAPPEARED"
                        history = VerificationStateMachine._set_timestamp(history, "OBJECT_DISAPPEARED", current_time)
                        if "TABLET_DISAPPEARED" not in history:
                            history.append("TABLET_DISAPPEARED")
                        ts_disappeared = current_time
                        # Record hand leaving mouth timestamp
                        history = VerificationStateMachine._set_timestamp(history, "LEFT_MOUTH", current_time)
                        ts_left_mouth = current_time

            elif internal_state == "OBJECT_DISAPPEARED":
                if mouth_open_frame:
                    if ts_mouth_opened == 0.0 or current_time > ts_mouth_opened:
                        history = VerificationStateMachine._set_timestamp(history, "MOUTH_OPENED", current_time)
                        ts_mouth_opened = current_time

                if ts_left_mouth == 0.0:
                    history = VerificationStateMachine._set_timestamp(history, "LEFT_MOUTH", current_time)
                    ts_left_mouth = current_time
                
                elapsed_since_leave = current_time - ts_left_mouth
                # Wait a short confirmation delay (approximately 1 second)
                if elapsed_since_leave >= 1.0:
                    next_internal_state = "MOUTH_CLOSED"
                    history = VerificationStateMachine._set_timestamp(history, "MOUTH_CLOSED", current_time)
                    if "MOUTH_CLOSED" not in history:
                        history.append("MOUTH_CLOSED")
                    ts_mouth_closed = current_time

            elif internal_state == "MOUTH_CLOSED":
                next_internal_state = "VERIFYING"
                history = VerificationStateMachine._set_timestamp(history, "VERIFYING", current_time)
                ts_verifying = current_time

            # Calculate multi-evidence confidence score
            confidence = 0.0

            # OCR Match evidence
            ocr_score = best_match_score * 0.25
            confidence += ocr_score

            # Sequential states check
            history_states = []
            for s in ["MEDICINE_VISIBLE", "HAND_DETECTED", "HAND_APPROACHING_MOUTH", "TABLET_NEAR_MOUTH", "OBJECT_DISAPPEARED", "MOUTH_CLOSED"]:
                ts = VerificationStateMachine._get_timestamp(history, s)
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
                    # Transition to OBJECT_DISAPPEARED is triggered by hand leaving mouth, confidence still increases
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

            # Mouth closed detection as an additional confidence bonus only
            if mouth_closed_cnt >= 2:
                confidence += 10

            final_confidence = min(100, int(round(confidence)))
            if next_internal_state in ["MOUTH_CLOSED", "VERIFYING", "TAKEN"]:
                final_confidence = max(final_confidence, 85)

            # If verification complete and confidence threshold met, transition to TAKEN
            if next_internal_state in ["MOUTH_CLOSED", "VERIFYING"] and final_confidence >= 80:
                next_internal_state = "TAKEN"
                history = VerificationStateMachine._set_timestamp(history, "TAKEN", current_time)
                if "TAKEN" not in history:
                    history.append("TAKEN")

            # Finalize new state and history
            new_state = VerificationStateMachine.INTERNAL_TO_FRONTEND_STATE.get(next_internal_state, "WAITING")
            history_set = set(history)
            history_set.add("WAITING")
            
            updated_history = sorted(
                list(history_set),
                key=lambda x: VerificationStateMachine.STATES.index(x) if x in VerificationStateMachine.STATES else 99
            )

            return new_state, updated_history, final_confidence

        except Exception as e:
            logger.exception(f"Exception in demo state machine evaluation: {e}")
            return current_state, history, confidence


def get_verification_strategy() -> VerificationStrategy:
    settings = get_settings()
    if settings.is_demo:
        logger.info("Initializing Demo Verification Strategy")
        return DemoVerificationStrategy()
    else:
        logger.info("Initializing Production Verification Strategy")
        return ProductionVerificationStrategy()
