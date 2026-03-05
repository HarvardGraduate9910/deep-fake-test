#!/usr/bin/env python3
"""Quick test to verify the backend can initialize and serve requests."""

import sys
import time
import subprocess
import requests

def main():
    print("🧪 Testing Deep Fake Detector Backend")
    print("=" * 50)
    
    # Test imports
    print("\n1️⃣  Testing imports...")
    try:
        import flask
        import cv2
        import numpy as np
        from backend.detection_engine import DeepFakeDetector
        print("   ✅ All imports successful")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test detector initialization
    print("\n2️⃣  Testing detector initialization...")
    try:
        detector = DeepFakeDetector()
        detector.load_models()
        print("   ✅ Detector initialized successfully")
        print(f"   📊 Detection method: {detector.config['detection_method']}")
        print(f"   🎯 Threshold: {detector.config['confidence_threshold']}")
    except Exception as e:
        print(f"   ❌ Detector initialization failed: {e}")
        return False
    
    # Test detection on dummy frame
    print("\n3️⃣  Testing detection on dummy frame...")
    try:
        # Create a simple test frame (black image with white rectangle)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(frame, (200, 150), (440, 330), (255, 255, 255), -1)
        
        result = detector.predict(frame, client_id="test_client")
        print(f"   ✅ Detection completed")
        print(f"   📊 Confidence: {result['confidence']:.3f}")
        print(f"   📊 Rolling confidence: {result['rolling_confidence']:.3f}")
        print(f"   👤 Faces detected: {result['faces_detected']}")
        print(f"   🎯 Is deepfake: {result['is_deepfake']}")
    except Exception as e:
        print(f"   ❌ Detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Start Flask server
    print("\n4️⃣  Starting Flask server...")
    try:
        proc = subprocess.Popen(
            [sys.executable, "backend/app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give server time to start
        
        # Test health endpoint
        print("\n5️⃣  Testing API endpoints...")
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check: {data}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            proc.terminate()
            return False
        
        # Test status endpoint
        response = requests.get("http://127.0.0.1:5000/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status check: {data}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            proc.terminate()
            return False
        
        proc.terminate()
        proc.wait(timeout=2)
        print("\n   ✅ Server stopped cleanly")
        
    except Exception as e:
        print(f"   ❌ Server test failed: {e}")
        try:
            proc.terminate()
        except:
            pass
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    print("\n🚀 Backend is ready to use:")
    print("   • Start: python backend/app.py")
    print("   • URL: http://127.0.0.1:5000")
    print("   • Health: http://127.0.0.1:5000/health")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
