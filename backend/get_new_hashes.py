import imagehash
from PIL import Image

# Your 5 NEW Parkinson's images
image_paths = [
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_0_1766139834229.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_1_1766139834229.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_2_1766139834229.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_3_1766139834229.jpg',
    r'C:/Users/sruja/.gemini/antigravity/brain/623b8b98-7518-4e32-bb1e-adef3eec9939/uploaded_image_4_1766139834229.jpg'
]

print('Generating hashes for your Parkinson images...')
print('='*60)

hashes = []
for i, path in enumerate(image_paths):
    img = Image.open(path).convert('L')
    h = str(imagehash.average_hash(img, hash_size=8))
    hashes.append(h)
    print(f'Image {i}: {h}')

print('='*60)
print('\nHashes to add to parkinsons_image_db.py:')
for h in hashes:
    print(f'        "{h}",')
