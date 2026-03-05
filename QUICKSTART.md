#🚀 Quick Start Guide for Deep Fake Detector

##1️⃣  Install Dependencies (One-time Setup)

### macOS/Linux:
```bash
cd "Deep Live Cam Detector"
chmod +x setup.sh
./setup.sh
```

### Windows:
```cmd
cd Deep Live Cam Detector
setup.bat
```

This will:
- Create Python virtual environment
- Install all required packages
- Create necessary directories
- Set up configuration files

---

##2️⃣  Start the Backend Server

### macOS/Linux:
```bash
source venv/bin/activate
python backend/app.py
```

### Windows:
```cmd
venv\Scripts\activate.bat
python backend\app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

✅ Leave this terminal running!

---

##3️⃣  Load Browser Extension

1. **Open Chrome** and go to `chrome://extensions/`
2. **Enable "Developer mode"** (toggle in top right)
3. **Click "Load unpacked"**
4. **Select the `extension` folder** from the project
5. **The extension should appear** in your extensions list

---

##4️⃣  Test Deep Fake Detection

1. **Open a video call**:
   - Zoom: zoom.us
   - Google Meet: meet.google.com
   - Microsoft Teams: teams.microsoft.com
   - Any other video platform

2. **Click the extension icon** (🎭) in your browser

3. **Monitor the extension popup:**
   - Green indicator = Backend connected
   - **Click "▶️ Start Detection"**
   - Extension will start analyzing video frames

4. **Watch the results**:
   - Risk meter shows video authenticity
   - Confidence score (0-1.0)
   - Number of faces detected
   - Verdict (Authentic or Likely Deep Fake)

---

##⚙️  Configuration Options

In the extension popup:

| Setting | Default | Range | Notes |
|---------|---------|-------|-------|
| **Confidence Threshold** | 0.5 | 0.3-0.9 | Lower = more sensitive |
| **Frame Sampling** | Every 5 | 1-10 | Lower = more accurate, slower |
| **Audio Alerts** | On | - | Beep when deep fake detected |
| **Logging** | Off | - | Enable for debugging |

---

## 🔧 Troubleshooting

### Backend won't start?
```bash
# Check if port 5000 is available
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process on port 5000 and try again
```

### Extension can't connect?
1. Verify backend is running (should see green indicator)
2. Check backend URL in extension settings (should be http://127.0.0.1:5000)
3. Try "Test Connection" button
4. Check browser console for errors (F12 → Console)

### No faces detected?
1. Ensure face is clearly visible in camera
2. Check lighting
3. Move closer to camera
4. Ensure minimum 50×50 pixel face size

### Slow performance?
1. Increase frame sampling rate (skip more frames)
2. Close other CPU-intensive applications
3. Use GPU acceleration if available:
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

---

##📊 Understanding Results

### Confidence Score (0-1.0)
- **0.0-0.3**: Likely Authentic (✅)
- **0.3-0.6**: Suspicious, might need review (⚠️)
- **0.6-1.0**: Likely Deep Fake (❌)

### Verdict Meanings
- **✅ Authentic**: Video appears genuine
- **⚠️ Suspicious**: Some artificial features detected
- **❌ Likely Deep Fake**: High probability of manipulation

---

##📚 Advanced Usage

### Use Custom Models

Replace the detection model in `backend/detection_engine.py`:

```python
def load_models(self):
    # Load FaceForensics++ model
    model_path = 'models/faceforensics_xceptionnet.pth'
    self.models['xceptionnet'] = torch.load(model_path)
```

### GPU Acceleration

```bash
# Install CUDA support (NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For AMD GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

### Change Backend Port

Edit `backend/app.py`:
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)  # Change port here
```

Then update extension settings to match.

---

##❓ FAQ

**Q: Is this 100% accurate?**
A: No detection system is perfect. Use with other security measures.

**Q: Can I use this to monitor others?**
A: Only with explicit consent, following all local laws.

**Q: Does it send data to the cloud?**
A: No! Everything runs locally on your machine.

**Q: Can I use this on Firefox?**
A: Not yet, but Firefox support is planned.

**Q: How much GPU memory do I need?**
A: 2GB+ GPU memory recommended (can run on CPU, but slower).

---

##🔗 Useful Links

- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [FaceForensics++ Dataset](https://github.com/ondyari/FaceForensics)
- [PyTorch Installation](https://pytorch.org/get-started/locally/)
- [OpenCV Documentation](https://opencv.org/documentation/)

---

**Made with ❤️ for cybersecurity awareness**

For additional help, check the main README.md file.
