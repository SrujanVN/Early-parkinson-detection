import os
import sys
import glob

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_dir)

from handwriting_predictor import handwriting_predictor

# Image paths from metadata
image_paths = [
    r"C:/Users/sruja/.gemini/antigravity/brain/e614f23c-f0bc-40af-a587-aad38807c492/uploaded_image_0_1766176108840.jpg",
    r"C:/Users/sruja/.gemini/antigravity/brain/e614f23c-f0bc-40af-a587-aad38807c492/uploaded_image_1_1766176108840.jpg",
    r"C:/Users/sruja/.gemini/antigravity/brain/e614f23c-f0bc-40af-a587-aad38807c492/uploaded_image_2_1766176108840.png",
    r"C:/Users/sruja/.gemini/antigravity/brain/e614f23c-f0bc-40af-a587-aad38807c492/uploaded_image_3_1766176108840.png"
]

print(f"Initializing Handwriting Predictor...")
success = handwriting_predictor.load_models()
if not success:
    print("❌ Failed to load handwriting models")
    sys.exit(1)

print("\n--- Verifying Predictions on Uploaded Images ---")
for img_path in image_paths:
    if not os.path.exists(img_path):
        print(f"Skipping {img_path} (File not found)")
        continue
        
    print(f"\nProcessing: {os.path.basename(img_path)}")
    try:
        with open(img_path, 'rb') as f:
            image_bytes = f.read()
            
        result = handwriting_predictor.predict(image_bytes)
        
        print(f"Diagnosis: {result.get('diagnosis')}")
        print(f"Confidence: {result.get('confidence'):.2%}")
        print("Individual Models:")
        for model_name, res in result.get('individual_predictions', {}).items():
            print(f"  - {model_name}: {res['prediction']} ({res['confidence']:.2f})")
            
        # Check for report generation
        from handwriting_report_generator import handwriting_report_gen
        pdf_base64 = handwriting_report_gen.generate_report(result)
        print(f"Report Generated: {'Yes' if pdf_base64 else 'No'} (Length: {len(pdf_base64)})")
            
    except Exception as e:
        print(f"❌ Error processing {os.path.basename(img_path)}: {e}")
        import traceback
        traceback.print_exc()

print("\n--- Verification Complete ---")
