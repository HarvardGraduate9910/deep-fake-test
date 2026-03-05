# 🎭 Deep Live Cam Detector - Deep Fake Detection System

A real-time deep fake detection system for live video calls with browser extension integration and Python backend.

## 📋 Features

✅ **Real-time Detection** - Process video frames at 10+ FPS
✅ **Multiple Detection Methods** - Uses ensemble analysis with facial feature extraction
✅ **Browser Extension** - Works with Zoom, Google Meet, Microsoft Teams, and more
✅ **Confidence Scoring** - Get detailed confidence metrics for each detection
✅ **Low-latency** - Process frames with minimal delay using optimized pipelines
✅ **Customizable Thresholds** - Adjust sensitivity based on your needs
✅ **Detailed Logging** - Track all detections with activity logs

## 🗂️ Project Structure

```
Deep Live Cam Detector/
├── backend/                 # Python Flask backend
│   ├── app.py              # Main Flask application
│   ├── detection_engine.py  # Core detection logic
│   ├── models/             # Pre-trained models directory
│   └── utils/              # Utility functions
├── extension/              # Chrome/Chromium extension
│   ├── manifest.json       # Extension configuration
│   ├── popup.html          # Extension UI
│   ├── css/
│   │   └── popup.css       # Styling
│   └── js/
│       ├── popup.js        # Popup logic
│       ├── content-script.js # Frame capture
│       └── background.js   # Background worker
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .env.example           # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser
- 2GB+ RAM (4GB+ recommended)
- GPU optional but recommended for real-time performance

### 1. Backend Setup

```bash
# Navigate to project directory
cd "Deep Live Cam Detector"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
python backend/app.py
```

Backend will start on `http://127.0.0.1:5000`

### 2. Browser Extension Setup

#### For Chrome/Chromium:

1. Open `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Navigate to the `extension/` folder
5. Click "Select Folder"

The extension should now appear in your extensions list.

#### For Other Chromium Browsers:
- **Brave**: Settings → Extensions → Load unpacked
- **Edge**: edge://extensions/ → (same steps as Chrome)

### 3. Start Detection

1. **Start the backend**:
   ```bash
   python backend/app.py
   ```

2. **Open a video call** (Zoom, Google Meet, Teams, etc.)

3. **Click extension icon** and press "Start Detection"

4. **Monitor results** in the extension popup

## 🔧 Configuration

### Backend Configuration

Edit settings in `backend/app.py`:

```python
detector = DeepFakeDetector()
detector.config = {
    'confidence_threshold': 0.5,      # Detection threshold (0-1)
    'detection_method': 'ensemble',   # Detection approach
    'min_face_size': 50,              # Minimum face size in pixels
    'use_gpu': True                   # Use GPU if available
}
```

### Extension Configuration

Through the popup UI:
- **Confidence Threshold**: 0.3-0.9 (default: 0.5)
- **Frame Sampling Rate**: 1-10 frames (default: 5)
- **Audio Alerts**: Enable/disable alerts on detection
- **Logging**: Enable/disable activity logs

## 🎯 How It Works

### Detection Pipeline

```
Video Stream
    ↓
Frame Capture (every N frames)
    ↓
Preprocessing (face crop + normalization)
    ↓
Face Detection (Haar Cascade)
    ↓
Per-frame artifact analysis
    ↓
Temporal stability scoring (session window)
    ↓
Rolling confidence scoring
    ↓
Result Display & Alerts
```

### Detection Methods

1. **Face Artifact Analysis**
   - Detect unusual edge density and blur patterns
   - Measure high-frequency residual noise in facial ROI
   - Track chroma/saturation inconsistency in the face region

2. **Temporal Instability Analysis**
   - Compare consecutive face frames for instability flicker
   - Smooth frame confidence across a rolling session window
   - Delay hard verdict until enough samples are collected

3. **Risk Aggregation**
   - Blend multiple artifact features into a normalized risk score
   - Expose both per-frame and rolling confidence
   - Trigger alerts when rolling confidence crosses threshold

## 📊 API Endpoints

### Health Check
```
GET /health
Response: { "status": "healthy", "detector_ready": true }
```

### Single Frame Detection
```
POST /detect
Body: { "frame": "base64_encoded_image", "client_id": "optional_session_id" }
Response: {
    "is_deepfake": bool,
    "confidence": float (0-1),
    "rolling_confidence": float (0-1),
    "faces_detected": int,
    "face_details": list
}
```

### Batch Detection
```
POST /detect/batch
Body: { "frames": ["base64_frame1", "base64_frame2", ...], "client_id": "optional_session_id" }
Response: {
    "frames_processed": int,
    "average_confidence": float,
    "average_rolling_confidence": float,
    "is_deepfake": bool,
    "details": list
}
```

### Status
```
GET /status
Response: {
    "detector_loaded": bool,
    "models_available": list,
    "api_version": "1.0.0"
}
```

### Configuration
```
GET /config          # Get current config
POST /config         # Update config
Body: { "confidence_threshold": 0.6, ... }
```

## 🔒 Security & Privacy

- ⚠️ **Local Processing**: All frames are processed locally, nothing stored
- ⚠️ **No Cloud Upload**: Video data never leaves your machine
- ⚠️ **No Recording**: Extension captures frames in memory only
- ⚠️ **No Tracking**: All activity logs are local storage

## 🚨 Important Notes

1. **Accuracy Disclaimer**: This tool is for educational purposes. No detection system is 100% accurate.

2. **Legal Considerations**: 
   - Check local laws before using for recording/monitoring
   - Get consent from all participants before monitoring
   - Use responsibly and ethically

3. **Performance**:
   - Better performance on dedicated GPUs
   - CPU mode will be slower
   - Adjust sampling rate for your system capabilities

4. **Browser Support**:
   - Chrome 88+
   - Chromium-based browsers
   - Firefox support coming soon

## 🔄 Advanced Usage

### Custom Model Integration

To use pre-trained models like FaceForensics++:

```python
# In backend/detection_engine.py

def load_faceforensics_model(self):
    """Load FaceForensics++ pretrained model"""
    # Download from: https://github.com/ondyari/FaceForensics
    model_path = 'models/faceforensics_xceptionnet.pth'
    self.models['xceptionnet'] = torch.load(model_path)
```

### GPU Acceleration

```bash
# Install CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU
python -c "import torch; print(torch.cuda.is_available())"
```

## 📈 Performance Optimization

### For Real-time Processing (30+ FPS):

1. **Use GPU**: Install CUDA/ROCm
2. **Reduce Frame Size**: Lower resolution input
3. **Increase Sampling Rate**: Skip frames (every 5-10 instead of every frame)
4. **Model Optimization**: Use quantized/distilled models

### Latency Targets:

| Component | Speed |
|-----------|-------|
| Frame Capture | ~10ms |
| Preprocessing | ~5ms |
| Face Detection | ~15ms |
| Analysis | ~20ms |
| Total | ~50ms (20 FPS) |

## 🛠️ Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check port 5000 isn't in use
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Try different port
python backend/app.py --port 5001
```

### Extension Can't Connect
1. Ensure backend is running
2. Check backend URL in settings (default: http://127.0.0.1:5000)
3. Disable firewall/VPN temporarily
4. Check browser console for errors (F12 → Console)

### No Faces Detected
1. Ensure good lighting
2. Face should be clearly visible in camera
3. Minimum face size is 50px × 50px
4. Adjust camera angle/distance

### False Positives
1. Increase confidence threshold in settings
2. Improve lighting
3. Move closer to camera
4. Check bandwidth isn't causing compression artifacts

## 📚 Learning Resources

### Deep Fake Detection:
- [FaceForensics++ Dataset](https://github.com/ondyari/FaceForensics)
- [MesoNet Paper](https://arxiv.org/abs/1809.00888)
- [XceptionNet for Detection](https://arxiv.org/abs/1610.02357)

### Browser Extensions:
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [WebRTC API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)

##🤝 Contributing

Improvements welcome! Areas for contribution:

- [ ] Better pre-trained models
- [ ] Firefox extension support
- [ ] Mobile browser support
- [ ] Improve detection accuracy
- [ ] Add more video call platform support
- [ ] Optimize for lower-end hardware

## 📄 License

This project is provided as-is for educational purposes.

## ⚠️ Disclaimer

This tool is for educational and authorized security purposes only. Users are responsible for:
- Complying with applicable laws
- Getting proper consent before monitoring
- Using responsibly and ethically
- Understanding accuracy limitations

---

**Made with ❤️ for cybersecurity awareness**

For issues or questions, please check the troubleshooting section or review the code comments.
