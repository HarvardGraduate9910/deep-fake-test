"""Deep fake detection engine for live-call monitoring.

This implementation is intentionally lightweight and local-only: it relies on
face-level artifact signals and temporal instability across frames. It is not a
replacement for a trained SOTA detector, but it provides a practical baseline
that behaves consistently for real-time streaming inputs.
"""

from collections import deque
from datetime import datetime
import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


def _clamp(value, low=0.0, high=1.0):
    return float(max(low, min(high, value)))


class DeepFakeDetector:
    """Session-aware deep fake detector with temporal smoothing."""

    def __init__(self):
        self.models = {}
        self.config = {
            "confidence_threshold": 0.6,
            "detection_method": "hybrid_heuristic_temporal_v1",
            "min_face_size": 64,
            "temporal_window": 20,
            "minimum_samples_for_verdict": 6,
            "session_ttl_frames": 400,
        }

        self._session_state = {}
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def load_models(self):
        """Load available detector resources.

        This baseline detector is feature-driven and does not require heavy
        model files. We still expose a model marker for status visibility.
        """
        self.models["hybrid_heuristic_temporal_v1"] = "ready"
        logger.info("Detection resources loaded")

    def _get_session(self, client_id):
        key = str(client_id or "default")
        if key not in self._session_state:
            self._session_state[key] = {
                "risk_history": deque(maxlen=self.config["temporal_window"]),
                "prev_face_gray": None,
                "frames_seen": 0,
                "frames_since_face": 0,
            }
        return self._session_state[key]

    def _cleanup_sessions(self):
        ttl = self.config["session_ttl_frames"]
        stale = []
        for sid, state in self._session_state.items():
            if state["frames_seen"] > ttl and state["frames_since_face"] > ttl:
                stale.append(sid)
        for sid in stale:
            del self._session_state[sid]

    def detect_faces(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(self.config["min_face_size"], self.config["min_face_size"]),
            )
            return faces
        except Exception as exc:
            logger.error("Face detection error: %s", exc)
            return []

    def _analyze_face(self, face_bgr, prev_face_gray):
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        edges = cv2.Canny(gray, 80, 160)
        edge_density = float(np.mean(edges > 0))

        # Residual high-frequency activity can increase on generated/warped faces.
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        residual = cv2.absdiff(gray, blur)
        high_freq_energy = float(np.mean(residual))

        hsv = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2HSV)
        sat_std = float(np.std(hsv[:, :, 1]))

        temporal_instability = 0.0
        if prev_face_gray is not None:
            prev_rs = cv2.resize(prev_face_gray, (gray.shape[1], gray.shape[0]))
            diff = cv2.absdiff(gray, prev_rs)
            temporal_instability = float(np.mean(diff) / 255.0)

        # Convert raw metrics to bounded [0,1] risk features.
        f_blur = _clamp((35.0 - lap_var) / 35.0)
        f_edges = _clamp((edge_density - 0.06) / 0.24)
        f_high_freq = _clamp((high_freq_energy - 6.0) / 25.0)
        f_sat = _clamp((14.0 - sat_std) / 14.0)
        f_temporal = _clamp((temporal_instability - 0.05) / 0.25)

        score = (
            0.22 * f_blur
            + 0.22 * f_edges
            + 0.18 * f_high_freq
            + 0.13 * f_sat
            + 0.25 * f_temporal
        )

        details = {
            "edge_density": edge_density,
            "laplacian_variance": lap_var,
            "high_freq_energy": high_freq_energy,
            "saturation_std": sat_std,
            "temporal_instability": temporal_instability,
            "score": _clamp(score),
        }
        return _clamp(score), details, gray

    def predict(self, frame, client_id=None):
        """Predict deepfake likelihood for a frame and update session risk."""
        try:
            if frame is None or frame.size == 0:
                return {
                    "error": "Invalid frame",
                    "is_deepfake": False,
                    "confidence": 0.0,
                    "rolling_confidence": 0.0,
                }

            state = self._get_session(client_id)
            state["frames_seen"] += 1

            faces = self.detect_faces(frame)
            face_details = []
            frame_confidence = 0.05
            reason = "No face detected"

            if len(faces) > 0:
                state["frames_since_face"] = 0
                scored_faces = []
                for (x, y, w, h) in faces:
                    face = frame[y : y + h, x : x + w]
                    if face.size == 0:
                        continue
                    score, details, face_gray = self._analyze_face(
                        face, state["prev_face_gray"]
                    )
                    state["prev_face_gray"] = face_gray
                    details.update(
                        {
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h),
                        }
                    )
                    face_details.append(details)
                    scored_faces.append(score)

                if scored_faces:
                    frame_confidence = float(np.mean(scored_faces))
                    reason = "Face artifact + temporal analysis"
            else:
                state["frames_since_face"] += 1
                state["prev_face_gray"] = None

            state["risk_history"].append(frame_confidence)
            rolling_confidence = float(np.mean(state["risk_history"]))
            enough_samples = (
                len(state["risk_history"])
                >= self.config["minimum_samples_for_verdict"]
            )
            is_deepfake = bool(
                enough_samples
                and rolling_confidence >= self.config["confidence_threshold"]
            )

            self._cleanup_sessions()

            return {
                "is_deepfake": is_deepfake,
                "confidence": float(frame_confidence),
                "rolling_confidence": rolling_confidence,
                "faces_detected": int(len(faces)),
                "face_details": face_details,
                "sample_count": len(state["risk_history"]),
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "frame_shape": list(frame.shape),
                "detection_method": self.config["detection_method"],
            }
        except Exception as exc:
            logger.error("Prediction error: %s", exc)
            return {
                "error": str(exc),
                "is_deepfake": False,
                "confidence": 0.0,
                "rolling_confidence": 0.0,
            }

    def get_available_models(self):
        return list(self.models.keys())

    def get_config(self):
        return self.config

    def update_config(self, new_config):
        self.config.update(new_config)
        for state in self._session_state.values():
            state["risk_history"] = deque(
                state["risk_history"], maxlen=self.config["temporal_window"]
            )
        logger.info("Config updated: %s", new_config)

    def batch_predict(self, frames, client_id=None):
        results = [self.predict(frame, client_id=client_id) for frame in frames]
        if not results:
            return {"error": "No frames processed", "results": []}

        avg_confidence = np.mean([r.get("confidence", 0.0) for r in results])
        avg_rolling = np.mean([r.get("rolling_confidence", 0.0) for r in results])
        return {
            "batch_size": len(frames),
            "average_confidence": float(avg_confidence),
            "average_rolling_confidence": float(avg_rolling),
            "is_deepfake": bool(avg_rolling >= self.config["confidence_threshold"]),
            "results": results,
        }
