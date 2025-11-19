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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'deepface-emotion-detector'
    }), 200

@app.route('/detect-emotion', methods=['POST'])
def detect_emotion():
    """
    Detect emotion from base64 encoded image
    
    Expected: { "image": "data:image/jpeg;base64,..." }
    Returns: { "emotion": "happy|neutral|sad", "confidence": 0.85 }
    """
    start_time = time.time()
    
    try:
        if not request.json or 'image' not in request.json:
            return jsonify({'error': 'Missing image data'}), 400
        
        # Decode base64 image
        img_data_url = request.json['image']
        img_base64 = img_data_url.split(',')[1] if ',' in img_data_url else img_data_url
        
        img_bytes = base64.b64decode(img_base64)
        img = Image.open(io.BytesIO(img_bytes))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        
        # Analyze with DeepFace
        result = DeepFace.analyze(
            img_path=img_array,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend='opencv',
            silent=True
        )
        
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
        confidence = round(emotion_mapping[dominant_emotion], 2)
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        logger.info(f"Emotion: {dominant_emotion} ({confidence}%) - {processing_time}ms")
        
        return jsonify({
            'emotion': dominant_emotion,
            'confidence': confidence,
            'processing_time_ms': processing_time
        }), 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'emotion': 'neutral',
            'confidence': 0.5,
            'error': str(e)
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)