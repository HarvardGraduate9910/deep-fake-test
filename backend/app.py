"""
Deep Fake Detection Backend Server
Real-time detection engine for live video calls
"""

import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import cv2
import logging
from detection_engine import DeepFakeDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, allow_private_network=True)

# Initialize detector
detector = None


def decode_frame_from_base64(frame_data):
    """Decode base64 (or data URL) image payload into OpenCV frame."""
    if isinstance(frame_data, str) and frame_data.startswith('data:image'):
        frame_data = frame_data.split(',', 1)[1]

    frame_bytes = base64.b64decode(frame_data)
    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame

def init_detector():
    """Initialize the deep fake detection model"""
    global detector
    try:
        logger.info("Initializing Deep Fake Detector...")
        detector = DeepFakeDetector()
        detector.load_models()
        logger.info("Detector initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize detector: {str(e)}")
        raise

@app.before_request
def before_request():
    """Initialize detector on first request"""
    global detector
    if detector is None:
        init_detector()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'detector_ready': detector is not None}), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API info for browser opens."""
    return jsonify({
        'service': 'Deep Fake Detection Backend',
        'status': 'running',
        'endpoints': ['/health', '/status', '/detect', '/detect/batch', '/config']
    }), 200

@app.route('/detect', methods=['POST'])
def detect_deepfake():
    """
    Process a frame and detect deep fakes
    Expects: base64-encoded image in request body
    Returns: detection results with confidence scores
    """
    try:
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame provided'}), 400
        
        frame = decode_frame_from_base64(data['frame'])
        client_id = data.get('client_id', 'default')
        
        if frame is None:
            return jsonify({'error': 'Failed to decode frame'}), 400
        
        # Run detection
        result = detector.predict(frame, client_id=client_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/detect/batch', methods=['POST'])
def detect_batch():
    """
    Process multiple frames in batch
    More efficient for multiple frames
    """
    try:
        data = request.get_json()
        
        if not data or 'frames' not in data:
            return jsonify({'error': 'No frames provided'}), 400
        
        frames_data = data['frames']
        client_id = data.get('client_id', 'default')
        results = []
        
        for frame_data in frames_data:
            try:
                frame = decode_frame_from_base64(frame_data)
                
                if frame is not None:
                    result = detector.predict(frame, client_id=client_id)
                    results.append(result)
            except Exception as e:
                logger.warning(f"Error processing frame in batch: {str(e)}")
                results.append({'error': str(e)})
        
        # Calculate overall risk
        if results:
            avg_confidence = np.mean([r.get('confidence', 0) for r in results if 'confidence' in r])
            avg_rolling = np.mean([
                r.get('rolling_confidence', r.get('confidence', 0))
                for r in results
                if 'confidence' in r
            ])
            overall_result = {
                'frames_processed': len(results),
                'average_confidence': float(avg_confidence),
                'average_rolling_confidence': float(avg_rolling),
                'is_deepfake': avg_rolling > detector.get_config().get('confidence_threshold', 0.5),
                'details': results
            }
        else:
            overall_result = {'error': 'No frames could be processed'}
        
        return jsonify(overall_result), 200
        
    except Exception as e:
        logger.error(f"Batch detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current detector status"""
    return jsonify({
        'detector_loaded': detector is not None,
        'models_available': detector.get_available_models() if detector else [],
        'api_version': '1.0.0'
    }), 200

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update detector configuration"""
    if request.method == 'GET':
        return jsonify(detector.get_config() if detector else {}), 200
    
    elif request.method == 'POST':
        try:
            config = request.get_json()
            if detector:
                detector.update_config(config)
            return jsonify({'status': 'config updated'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        # Initialize detector
        init_detector()
        
        # Run Flask app
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)
