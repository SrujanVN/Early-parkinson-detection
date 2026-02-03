import sys
sys.path.insert(0, 'backend')

print("Testing imports...")

try:
    from image_processor import (
        preprocess_image_for_tensorflow, 
        preprocess_image_for_pytorch,
        validate_image_file,
        save_image_temporarily,
        cleanup_temp_file
    )
    print("✓ image_processor imported")
except ImportError as e:
    print(f"✗ image_processor failed: {e}")

try:
    from handwriting_handler import register_handwriting_routes
    print("✓ handwriting_handler imported")
except ImportError as e:
    print(f"✗ handwriting_handler failed: {e}")

try:
    from voice_handler import register_voice_routes
    print("✓ voice_handler imported")
except ImportError as e:
    print(f"✗ voice_handler failed: {e}")

try:
    from csv_handler import register_csv_routes
    print("✓ csv_handler imported")
except ImportError as e:
    print(f"✗ csv_handler failed: {e}")

try:
    from gradcam_generator import (
        generate_gradcam_for_model,
        encode_image_to_base64,
        save_gradcam_image
    )
    print("✓ gradcam_generator imported")
except ImportError as e:
    print(f"✗ gradcam_generator failed: {e}")

try:
    from parkinsons_image_db import check_image_match, get_model_scores
    print("✓ parkinsons_image_db imported")
except ImportError as e:
    print(f"✗ parkinsons_image_db failed: {e}")

try:
    from xai_visualizations import generate_gradcam_overlay, generate_lime_explanation
    print("✓ xai_visualizations imported")
except ImportError as e:
    print(f"✗ xai_visualizations failed: {e}")

print("\nTesting model initialization...")
try:
    result = initialize_ensemble_models()
    print(f"Initialization result: {result}")
    print(f"Models loaded: {ensemble_predictor.get_model_info()}")
except Exception as e:
    print(f"Initialization failed: {e}")
    import traceback
    traceback.print_exc()
