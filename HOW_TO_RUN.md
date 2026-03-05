# 🚀 How to Run the Deep Fake Detector

## ✅ Current Status

**Backend is RUNNING** at `http://127.0.0.1:5000`

## 🎯 Quick Start (Backend Already Running)

Since the backend is already active, you just need to load the extension:

### 1. Load the Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right corner)
3. Click **"Load unpacked"**
4. Navigate to and select the `extension/` folder from this project
5. The extension icon should appear in your browser toolbar

### 2. Test on a Video Call

1. Go to any video call platform:
   - Google Meet: `meet.google.com`
   - Zoom: `zoom.us`
   - Microsoft Teams: `teams.microsoft.com`
   
2. Click the Deep Fake Detector extension icon (🎭)

3. In the popup:
   - Verify **Backend Status** shows 🟢 Connected
   - Click **"▶️ Start Detection"**

4. Watch the live results:
   - **Risk meter** shows deepfake probability
   - **Confidence score** updates in real-time
   - **Verdict** shows "✅ Authentic" or "⚠️ Likely Deep Fake"
   - **Processing time** shows detection latency

---

## 🔧 If Backend Stopped or You Restart

### Start Backend Manually

```bash
cd "/Users/aashishjindal/Downloads/VFS Dubai/Deep Fake Live Cam Detector"
source venv/bin/activate
python backend/app.py
```

The backend will start on `http://127.0.0.1:5000`

---

## 🛠️ First Time Setup

If you haven't run setup yet:

```bash
cd "/Users/aashishjindal/Downloads/VFS Dubai/Deep Fake Live Cam Detector"
./setup.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Create necessary directories

---

## ⚙️ Configuration

### Extension Settings

Click the extension icon and adjust:

- **Confidence Threshold**: 0.3 to 0.9 (default: 0.62)
  - Lower = more sensitive (more false positives)
  - Higher = less sensitive (may miss some deepfakes)

- **Frame Sampling Rate**: 1 to 10 frames (default: 5)
  - Lower = more accurate but slower
  - Higher = faster but less accurate

- **Audio Alerts**: Enable beep sound when deepfake detected

- **Logging**: Enable to see detailed activity logs

### Backend Configuration

The backend uses these defaults (can be modified in `.env`):

- **Port**: 5000
- **Detection Method**: hybrid_heuristic_temporal_v1
- **Confidence Threshold**: 0.62
- **Minimum Face Size**: 64 pixels
- **Temporal Window**: 20 frames

---

## 📊 Understanding Results

### Confidence Score (0.0 - 1.0)

- **0.0 - 0.3**: Very likely authentic ✅
- **0.3 - 0.6**: Uncertain, needs review ⚠️
- **0.6 - 1.0**: Very likely deepfake ❌

### Rolling Confidence

The system tracks risk across multiple frames for more stable results. A verdict is only shown after analyzing at least 6 frames.

### Detection Features

The system analyzes:
- Edge density patterns
- Image blur/sharpness
- High-frequency noise
- Color saturation consistency
- Temporal stability between frames

---

## 🧪 Testing

Run backend tests:

```bash
python test_backend.py
```

This verifies:
- All imports work
- Detector initializes
- Detection works on test frames
- API endpoints respond correctly

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "Address already in use"**
```bash
# Kill existing process on port 5000
lsof -ti:5000 | xargs kill -9
# Then start backend again
python backend/app.py
```

### Extension shows "Backend Offline"

1. Check backend is running: `curl http://127.0.0.1:5000/health`
2. If not running, start it: `python backend/app.py`
3. Check firewall isn't blocking port 5000
4. In extension settings, verify Backend URL is `http://127.0.0.1:5000`

### No faces detected

1. Ensure camera is on and face is visible
2. Check lighting (face should be well-lit)
3. Move closer to camera
4. Lower "Minimum Face Size" in backend config

### Slow performance

1. Increase "Frame Sampling Rate" in extension settings
2. Close other CPU-intensive applications
3. Check backend terminal for warnings

---

## 📝 Technical Details

### How It Works

1. **Extension** captures video frames from the browser
2. Frames are sent to **backend** via HTTP POST
3. **Backend** analyzes each frame:
   - Detects faces using Haar Cascade
   - Extracts artifact features
   - Compares with previous frames (temporal analysis)
4. **Rolling confidence** is calculated over last 20 frames
5. **Results** sent back to extension and displayed

### Session Tracking

Each browser tab gets a unique `client_id` so the backend can:
- Track frame history per session
- Calculate rolling confidence per video call
- Avoid mixing data from different calls

---

## 🔒 Privacy & Security

- ✅ All processing is **local** (no cloud uploads)
- ✅ Frames are **not stored** (deleted after processing)
- ✅ No data is sent to external servers
- ✅ Session data is temporary (cleared after 400 frames of no face)

---

## 📚 More Information

- See [README.md](README.md) for full documentation
- See [QUICKSTART.md](QUICKSTART.md) for detailed setup guide
- Backend code: `backend/detection_engine.py`
- Extension code: `extension/js/`

---

**Ready to detect deepfakes on live video calls! 🎭**
