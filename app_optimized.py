from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
import logging
import os
import time
from PIL import Image
import numpy as np
from deepface import DeepFace

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS with specific settings
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Flag to track if models are warmed up
models_warmed_up = False

def warmup_models():
    """Warm up the DeepFace model"""
    global models_warmed_up
    if not models_warmed_up:
        try:
            logger.info("🔥 Warming up DeepFace models...")
            # Create a dummy image to initialize models
            dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
            DeepFace.analyze(
                img_path=dummy_img,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',
                silent=True
            )
            models_warmed_up = True
            logger.info("✅ Models loaded successfully!")
        except Exception as e:
            logger.warning(f"⚠️ Warmup failed: {e}")

@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information"""
    return jsonify({
        'service': 'DeepFace Emotion Detection API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'detect_emotion': '/detect-emotion (POST)'
        },
        'status': 'running'
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'deepface-emotion-detector',
        'timestamp': int(time.time())
    }), 200

@app.route('/detect-emotion', methods=['POST', 'OPTIONS'])
def detect_emotion():
    """
    Detect emotion from base64 encoded image
    
    Expected: { "image": "data:image/jpeg;base64,..." }
    Returns: { "emotion": "happy|neutral|sad", "confidence": 0.85 }
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    # Warm up models on first request
    warmup_models()
    
    start_time = time.time()
    
    try:
        # Validate request
        if not request.json or 'image' not in request.json:
            logger.warning("Missing image data in request")
            return jsonify({'error': 'Missing image data'}), 400
        
        # Decode base64 image
        img_data_url = request.json['image']
        
        # Handle both formats: with and without data URL prefix
        if ',' in img_data_url:
            img_base64 = img_data_url.split(',')[1]
        else:
            img_base64 = img_data_url
        
        try:
            img_bytes = base64.b64decode(img_base64)
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            return jsonify({'error': 'Invalid base64 image data'}), 400
        
        # Open and convert image
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (optional optimization)
        max_size = 1024
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        img_array = np.array(img)
        
        # Analyze with DeepFace
        result = DeepFace.analyze(
            img_path=img_array,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend='opencv',
            silent=True
        )
        
        # Handle list or dict response
        if isinstance(result, list):
            result = result[0]
        
        emotions = result.get('emotion', {})
        
        # Map to 3 categories: happy, neutral, sad
        emotion_mapping = {
            'happy': float(emotions.get('happy', 0)),
            'neutral': float(emotions.get('neutral', 0)),
            'sad': float(
                emotions.get('sad', 0) + 
                emotions.get('angry', 0) * 0.5 + 
                emotions.get('fear', 0) * 0.3
            )
        }
        
        # Get dominant emotion
        dominant_emotion = max(emotion_mapping, key=emotion_mapping.get)
        confidence = round(emotion_mapping[dominant_emotion] / 100, 2)
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        logger.info(
            f"✅ Emotion: {dominant_emotion} "
            f"({confidence*100:.1f}%) - {processing_time}ms"
        )
        
        return jsonify({
            'emotion': dominant_emotion,
            'confidence': confidence,
            'processing_time_ms': processing_time,
            'all_emotions': emotion_mapping
        }), 200
        
    except Exception as e:
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.error(f"❌ Error processing image: {e}")
        
        # Return neutral with error info
        return jsonify({
            'emotion': 'neutral',
            'confidence': 0.5,
            'error': str(e),
            'processing_time_ms': processing_time
        }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/', '/health', '/detect-emotion']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please check server logs'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting DeepFace Emotion Detection API on port {port}")
    logger.info(f"🐛 Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )