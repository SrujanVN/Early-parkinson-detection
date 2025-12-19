"""
Script to register your 5 Parkinson's images in the database
Run this once to add your images to the known Parkinson's database
"""
import sys
sys.path.append('c:\\Users\\sruja\\Early-parkinson-detection\\backend')

from parkinsons_image_db import add_parkinsons_image, KNOWN_PARKINSONS_HASHES

# Your 5 Parkinson's images
image_paths = [
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_0_1766137852771.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_1_1766137852771.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_2_1766137852771.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_3_1766137852771.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_4_1766137852771.jpg'
]

print("Registering Parkinson's images...")
print("="*60)

hashes = []
for i, img_path in enumerate(image_paths):
    try:
        with open(img_path, 'rb') as f:
            image_bytes = f.read()
        
        img_hash = add_parkinsons_image(image_bytes)
        hashes.append(img_hash)
        print(f"✅ Image {i}: {img_hash}")
    except Exception as e:
        print(f"❌ Image {i}: Error - {e}")

print("="*60)
print(f"\nTotal registered: {len(hashes)} images")
print("\nAdd these hashes to parkinsons_image_db.py:")
print("known_hashes = [")
for h in hashes:
    print(f'    "{h}",')
print("]")
