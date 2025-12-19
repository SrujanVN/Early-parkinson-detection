"""
Test script for FastAPI Backend
Run this after starting the server to verify all endpoints work
"""

import requests
import json
import base64
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print("✓ Server is healthy")
        print(f"  Models loaded: {data['models_loaded']}")
        print(f"  Device: {data['device']}")
        print(f"  Gemini available: {data['gemini_available']}")
        return True
    else:
        print("✗ Health check failed")
        return False

def test_csv_prediction():
    """Test CSV prediction endpoint"""
    print("\n" + "="*60)
    print("Testing CSV Prediction")
    print("="*60)
    
    # Sample features from the CSV data you provided
    features = {
        "MDVP:Fo(Hz)": 119.992,
        "MDVP:Fhi(Hz)": 157.302,
        "MDVP:Flo(Hz)": 74.997,
        "MDVP:Jitter(%)": 0.00784,
        "MDVP:Jitter(Abs)": 0.00007,
        "MDVP:RAP": 0.00370,
        "MDVP:PPQ": 0.00554,
        "Jitter:DDP": 0.01109,
        "MDVP:Shimmer": 0.04374,
        "MDVP:Shimmer(dB)": 0.426,
        "Shimmer:APQ3": 0.02182,
        "Shimmer:APQ5": 0.03130,
        "MDVP:APQ": 0.02971,
        "Shimmer:DDA": 0.06545,
        "NHR": 0.02211,
        "HNR": 21.033,
        "RPDE": 0.414783,
        "DFA": 0.815285,
        "spread1": -4.813031,
        "spread2": 0.266482,
        "D2": 2.301442,
        "PPE": 0.284654
    }
    
    payload = {
        "features": features,
        "patient_name": "Test Patient"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict/csv",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ CSV prediction successful")
            print(f"  Diagnosis: {data['diagnosis']}")
            print(f"  Confidence: {data['confidence']:.2%}")
            print(f"  PDF report generated: {'Yes' if data.get('report_pdf_base64') else 'No'}")
            return True
        else:
            print(f"✗ CSV prediction failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_chat():
    """Test chatbot endpoint"""
    print("\n" + "="*60)
    print("Testing Chatbot")
    print("="*60)
    
    payload = {
        "message": "What are the early signs of Parkinson's disease?",
        "history": []
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Chatbot response received")
            print(f"  Response preview: {data['response'][:100]}...")
            return True
        elif response.status_code == 503:
            print("⚠ Chatbot not available (GEMINI_API_KEY not set)")
            return True
        else:
            print(f"✗ Chat failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_mri_prediction():
    """Test MRI prediction (requires image file)"""
    print("\n" + "="*60)
    print("Testing MRI Prediction")
    print("="*60)
    
    # Check if test image exists
    test_image_path = Path("test_mri.jpg")
    if not test_image_path.exists():
        print("⚠ Skipping MRI test (no test_mri.jpg file found)")
        print("  To test: Place a brain MRI image as 'test_mri.jpg' in this directory")
        return True
    
    try:
        with open(test_image_path, "rb") as f:
            files = {"file": f}
            data = {"patient_name": "Test Patient"}
            
            response = requests.post(
                f"{BASE_URL}/predict/mri",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ MRI prediction successful")
            print(f"  Diagnosis: {result['diagnosis']}")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Models used: {result['ensemble_info']['num_models']}")
            print(f"  GradCAM available: {'Yes' if result['xai_images'].get('gradcam_base64') else 'No'}")
            print(f"  PDF report generated: {'Yes' if result.get('report_pdf_base64') else 'No'}")
            return True
        else:
            print(f"✗ MRI prediction failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FastAPI Backend Test Suite")
    print("="*60)
    print(f"Testing server at: {BASE_URL}")
    print("Make sure the server is running: uvicorn app:app --reload")
    
    results = {
        "Health Check": test_health(),
        "CSV Prediction": test_csv_prediction(),
        "Chatbot": test_chat(),
        "MRI Prediction": test_mri_prediction()
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print("\n⚠ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
