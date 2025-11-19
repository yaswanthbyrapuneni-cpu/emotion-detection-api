"""
Quick Test Script for Emotion Detection API
Run this after starting your Flask server to verify it's working
"""

import requests
import base64
from PIL import Image
import io
import numpy as np

# API URL (change if using different port)
API_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    print("🧪 Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def create_test_image():
    """Create a simple test image"""
    # Create a simple RGB image (224x224 with a gradient)
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    
    # Add some pattern
    for i in range(224):
        for j in range(224):
            img[i, j] = [i % 256, j % 256, (i+j) % 256]
    
    # Convert to PIL Image
    pil_img = Image.fromarray(img)
    
    # Convert to base64
    buffered = io.BytesIO()
    pil_img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_base64}"

def test_emotion_detection():
    """Test the emotion detection endpoint"""
    print("\n🧪 Testing emotion detection endpoint...")
    try:
        # Create test image
        print("   Creating test image...")
        test_img = create_test_image()
        
        # Send request
        print("   Sending request to API...")
        response = requests.post(
            f"{API_URL}/detect-emotion",
            json={"image": test_img},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Emotion detection passed!")
            print(f"   Emotion: {result.get('emotion')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Processing Time: {result.get('processing_time_ms')}ms")
            return True
        else:
            print(f"❌ Emotion detection failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.Timeout:
        print("❌ Request timed out (this is normal for first request)")
        print("   Try again - models are being loaded")
        return False
    except Exception as e:
        print(f"❌ Error testing emotion detection: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Emotion Detection API Test Suite")
    print("=" * 60)
    print(f"\nTesting API at: {API_URL}")
    print("Make sure your Flask server is running!")
    print("\nStarting tests...\n")
    
    # Test health endpoint
    health_ok = test_health()
    
    if not health_ok:
        print("\n⚠️ Health check failed. Is the server running?")
        print("   Start the server with: python app_optimized.py")
        return
    
    # Test emotion detection
    emotion_ok = test_emotion_detection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Emotion Detection: {'✅ PASS' if emotion_ok else '❌ FAIL'}")
    
    if health_ok and emotion_ok:
        print("\n🎉 All tests passed! Your API is ready to deploy!")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
