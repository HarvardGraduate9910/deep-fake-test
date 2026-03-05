;;;l# Backend Deepfake Detection Details

## Purpose
This document explains how the Python backend detects likely deepfakes for live video calls in the current implementation.

Relevant source files:
- `backend/app.py`
- `backend/detection_engine.py`

## High-Level Flow
1. The extension captures frames from a live video call and sends each frame as base64 JPEG.
2. The backend receives frames on `POST /detect`.
3. The backend decodes the image into an OpenCV frame.
4. The detector analyzes each detected face using artifact and temporal signals.
5. The detector maintains per-session history using `client_id`.
6. The backend returns both per-frame confidence and rolling confidence.
7. A deepfake verdict is only triggered after enough samples are collected.

## Runtime Architecture
- Web framework: Flask (`backend/app.py`)
- CORS handling: `flask_cors.CORS(app, allow_private_network=True)`
- Computer vision: OpenCV (`cv2`)
- Numeric processing: NumPy
- Detector class: `DeepFakeDetector` in `backend/detection_engine.py`

### Lazy Initialization
The detector is initialized once and reused:
- `@app.before_request` checks if `detector is None`
- If needed, `init_detector()` creates `DeepFakeDetector()` and calls `load_models()`

This avoids per-request model initialization overhead.

## API Endpoints
### `GET /`
Returns backend service info and endpoint list.

### `GET /health`
Returns:
- `status`
- `detector_ready`

Used by the extension popup to show backend connectivity.

### `POST /detect`
Input JSON:
- `frame`: base64 image string (can be full data URL or raw base64)
- `client_id` (optional): session identity from browser tab

Output JSON includes:
- `is_deepfake`: boolean verdict
- `confidence`: frame-level score in `[0, 1]`
- `rolling_confidence`: temporal average in `[0, 1]`
- `faces_detected`
- `face_details` (per-face feature metrics)
- `sample_count`
- `reason`
- `timestamp`
- `frame_shape`
- `detection_method`

### `POST /detect/batch`
Processes multiple frames and returns aggregate confidence.

### `GET /status`
Returns detector/model availability and API version.

### `GET /config`, `POST /config`
Reads/updates detector configuration at runtime.

## Frame Decode Path
`decode_frame_from_base64(frame_data)` does:
1. If input starts with `data:image`, strip metadata prefix.
2. Base64 decode to bytes.
3. Convert bytes to NumPy array.
4. Decode image into BGR frame with `cv2.imdecode`.

If decode fails, endpoint returns HTTP `400`.

## Detection Engine Internals
The backend is a local heuristic + temporal detector, not a heavy neural model.

### Default Configuration
In `DeepFakeDetector.__init__`:
- `confidence_threshold`: `0.6`
- `detection_method`: `hybrid_heuristic_temporal_v1`
- `min_face_size`: `64`
- `temporal_window`: `20`
- `minimum_samples_for_verdict`: `6`
- `session_ttl_frames`: `400`

### Session State by `client_id`
For each session key, backend stores:
- `risk_history`: rolling deque of confidence values
- `prev_face_gray`: previous face crop (grayscale) for temporal diff
- `frames_seen`
- `frames_since_face`

Why this matters:
- Multiple browser tabs can be isolated.
- Rolling confidence remains stable per session.
- Old inactive sessions are cleaned up automatically.

### Face Detection
`detect_faces(frame)`:
- Converts frame to grayscale.
- Uses Haar cascade: `haarcascade_frontalface_default.xml`.
- Parameters:
  - `scaleFactor=1.1`
  - `minNeighbors=5`
  - `minSize=(min_face_size, min_face_size)`

### Per-Face Feature Extraction
For each face ROI, `_analyze_face` computes:
- `laplacian_variance`: blur/sharpness indicator
- `edge_density`: Canny edge ratio
- `high_freq_energy`: residual from Gaussian blur subtraction
- `saturation_std`: color saturation consistency
- `temporal_instability`: mean pixel diff vs previous face frame

Each raw metric is normalized to `[0, 1]` and combined with weights:
- `f_blur`: `0.22`
- `f_edges`: `0.22`
- `f_high_freq`: `0.18`
- `f_sat`: `0.13`
- `f_temporal`: `0.25`

Weighted sum gives per-face risk score.
Frame confidence is the mean score across detected faces.

### Temporal Smoothing and Verdict Logic
In `predict`:
1. Append `frame_confidence` to `risk_history`.
2. Compute `rolling_confidence = mean(risk_history)`.
3. Mark `is_deepfake = True` only when both conditions hold:
   - `sample_count >= minimum_samples_for_verdict`
   - `rolling_confidence >= confidence_threshold`

This prevents unstable early false positives.

### No-Face Behavior
When no face is found:
- Frame confidence defaults to `0.05`.
- `prev_face_gray` is reset.
- Session counter `frames_since_face` increments.

### Session Cleanup
`_cleanup_sessions()` deletes stale sessions when:
- `frames_seen > session_ttl_frames`
- and `frames_since_face > session_ttl_frames`

This limits memory growth in long-running backend processes.

## Response Semantics
### `confidence`
Single-frame estimate. Can fluctuate quickly.

### `rolling_confidence`
Average over recent frames. Used for final verdict and UI risk bar stability.

### `is_deepfake`
Conservative final flag derived from rolling confidence and sample gate.

## Error Handling
`/detect` and `/detect/batch` return:
- `400` for missing or invalid frame payload
- `500` for unexpected runtime errors

Backend logs errors with `logging` module for debugging.

## Live Video Performance Notes
- Flask runs with `threaded=True` to handle concurrent requests.
- Sampling rate is controlled by extension; backend processes what it receives.
- Smaller frame size and moderate sampling improve real-time responsiveness.

## CORS and Browser Compatibility
The backend enables CORS globally and allows private-network preflight:
- `CORS(app, allow_private_network=True)`

This is important for browser extension traffic from pages like Google Meet to localhost backend endpoints.

## Tunable Parameters and Practical Effects
### `confidence_threshold`
- Lower value: more sensitive, more false positives.
- Higher value: more conservative, may miss subtle manipulations.

### `temporal_window`
- Larger window: smoother output, slower reaction.
- Smaller window: faster reaction, noisier output.

### `minimum_samples_for_verdict`
- Larger value: safer initial behavior.
- Smaller value: quicker verdicts.

### `min_face_size`
- Larger value: fewer tiny/uncertain detections.
- Smaller value: more detections, possible noise.

## Current Limitations
- Heuristic approach, not a benchmark-grade deep model.
- Accuracy depends on lighting, compression, camera quality, and face visibility.
- Best used as a risk signal, not a standalone forensic final judgment.

## Suggested Validation Steps
1. Start backend: `python backend/app.py`
2. Verify root: `http://127.0.0.1:5000/`
3. Verify health: `http://127.0.0.1:5000/health`
4. Run test suite: `python test_backend.py`
5. During live call, observe:
   - `sample_count` increasing
   - `rolling_confidence` smoothing behavior
   - verdict only after minimum sample count
