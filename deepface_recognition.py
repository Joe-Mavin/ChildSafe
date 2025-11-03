"""
DeepFace-based face recognition for ChildSafe
This provides state-of-the-art accuracy using deep learning models
"""

import os
import numpy as np
import base64
from deepface import DeepFace
import cv2
from PIL import Image
import tempfile
import warnings

# Suppress TensorFlow warnings for cleaner output
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def extract_face_encoding_deepface(image_path_or_bytes, model_name='VGG-Face'):
    """
    Extract face encoding using DeepFace.
    
    Args:
    - image_path_or_bytes: Path to image file or image bytes
    - model_name: Model to use ('VGG-Face', 'Facenet', 'OpenFace', 'ArcFace')
    
    Returns:
    - Face encoding array or None if no face found
    """
    try:
        temp_file = None
        
        # Handle bytes input by creating temporary file
        if isinstance(image_path_or_bytes, bytes):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(image_path_or_bytes)
            temp_file.close()
            image_path = temp_file.name
        else:
            image_path = image_path_or_bytes
        
        # Extract face embedding using DeepFace
        embedding = DeepFace.represent(
            img_path=image_path,
            model_name=model_name,
            enforce_detection=True,
            detector_backend='opencv'
        )
        
        # Clean up temporary file
        if temp_file:
            os.unlink(temp_file.name)
        
        # DeepFace returns a list of dictionaries, get the first face
        if embedding and len(embedding) > 0:
            return np.array(embedding[0]['embedding'], dtype=np.float32)
        
        return None
        
    except Exception as e:
        # Clean up temporary file on error
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        
        print(f"DeepFace encoding error: {str(e)}")
        return None

def compare_faces_deepface(encoding1, encoding2, model_name='VGG-Face'):
    """
    Compare two face encodings using cosine similarity.
    
    Args:
    - encoding1: First face encoding
    - encoding2: Second face encoding
    - model_name: Model used for encoding
    
    Returns:
    - Similarity score (0-100) or None if comparison fails
    """
    try:
        if encoding1 is None or encoding2 is None:
            return None
        
        # Ensure encodings are numpy arrays
        enc1 = np.array(encoding1, dtype=np.float32)
        enc2 = np.array(encoding2, dtype=np.float32)
        
        # Calculate cosine similarity manually
        dot_product = np.dot(enc1, enc2)
        norm1 = np.linalg.norm(enc1)
        norm2 = np.linalg.norm(enc2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        cosine_similarity = dot_product / (norm1 * norm2)
        
        # Convert to percentage (cosine similarity ranges from -1 to 1)
        # We map it to 0-100 where 1 = 100% and 0 = 50%
        similarity = ((cosine_similarity + 1) / 2) * 100
        
        return max(0, min(100, similarity))
        
    except Exception as e:
        print(f"DeepFace comparison error: {str(e)}")
        return None

def verify_faces_deepface(img1_path_or_bytes, img2_path_or_bytes, model_name='VGG-Face'):
    """
    Verify if two images contain the same person using DeepFace.
    This is a direct verification without manual encoding extraction.
    
    Args:
    - img1_path_or_bytes: First image (path or bytes)
    - img2_path_or_bytes: Second image (path or bytes)
    - model_name: Model to use for verification
    
    Returns:
    - Dictionary with verification result and confidence
    """
    try:
        temp_files = []
        
        # Handle bytes inputs
        paths = []
        for img_data in [img1_path_or_bytes, img2_path_or_bytes]:
            if isinstance(img_data, bytes):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_file.write(img_data)
                temp_file.close()
                temp_files.append(temp_file.name)
                paths.append(temp_file.name)
            else:
                paths.append(img_data)
        
        # Use DeepFace.verify for direct comparison
        result = DeepFace.verify(
            img1_path=paths[0],
            img2_path=paths[1],
            model_name=model_name,
            detector_backend='opencv',
            enforce_detection=True
        )
        
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        # Convert distance to similarity percentage
        distance = result.get('distance', 1.0)
        threshold = result.get('threshold', 0.4)
        
        # Calculate similarity based on distance and threshold
        if distance <= threshold:
            # Faces match - calculate high similarity
            similarity = (1 - (distance / threshold)) * 100
            similarity = max(80, min(100, similarity))  # Ensure high similarity for matches
        else:
            # Faces don't match - calculate low similarity
            similarity = max(0, (1 - distance) * 100)
            similarity = min(79, similarity)  # Ensure low similarity for non-matches
        
        return {
            'verified': result.get('verified', False),
            'similarity': similarity,
            'distance': distance,
            'threshold': threshold,
            'model': model_name
        }
        
    except Exception as e:
        # Clean up temporary files on error
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        print(f"DeepFace verification error: {str(e)}")
        return None

def save_face_encoding_deepface(image_path, child_id, database_connection, model_name='VGG-Face'):
    """
    Save DeepFace encoding to database.
    
    Args:
    - image_path: Path to the child's image
    - child_id: Child's database ID
    - database_connection: SQLite connection
    - model_name: DeepFace model to use
    
    Returns:
    - True if successful, False otherwise
    """
    try:
        encoding = extract_face_encoding_deepface(image_path, model_name)
        if encoding is not None:
            # Convert encoding to base64 string for storage
            encoding_str = base64.b64encode(encoding.tobytes()).decode('utf-8')
            
            cursor = database_connection.cursor()
            cursor.execute('''
                UPDATE children SET face_encoding = ? WHERE id = ?
            ''', (encoding_str, child_id))
            database_connection.commit()
            return True
    except Exception as e:
        print(f"Error saving DeepFace encoding: {str(e)}")
    return False

def get_face_encoding_from_db_deepface(child_id, database_connection):
    """
    Retrieve DeepFace encoding from database.
    
    Args:
    - child_id: Child's database ID
    - database_connection: SQLite connection
    
    Returns:
    - Face encoding array or None
    """
    try:
        cursor = database_connection.cursor()
        cursor.execute('SELECT face_encoding FROM children WHERE id = ?', (child_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            # Convert base64 string back to numpy array
            encoding_bytes = base64.b64decode(result[0])
            encoding = np.frombuffer(encoding_bytes, dtype=np.float32)
            return encoding
    except Exception as e:
        print(f"Error retrieving DeepFace encoding: {str(e)}")
    return None

def test_deepface():
    """Test DeepFace functionality."""
    try:
        print("🧪 Testing DeepFace...")
        
        # Create a simple test image
        test_image = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Draw a simple face
        cv2.circle(test_image, (100, 100), 80, (200, 180, 160), -1)  # Face
        cv2.circle(test_image, (80, 80), 8, (50, 50, 50), -1)        # Left eye
        cv2.circle(test_image, (120, 80), 8, (50, 50, 50), -1)       # Right eye
        cv2.line(test_image, (100, 90), (100, 110), (100, 100, 100), 2)  # Nose
        cv2.ellipse(test_image, (100, 130), (20, 10), 0, 0, 180, (100, 100, 100), 2)  # Mouth
        
        # Save test image
        cv2.imwrite('test_deepface.jpg', test_image)
        
        # Test encoding extraction
        encoding = extract_face_encoding_deepface('test_deepface.jpg')
        
        if encoding is not None:
            print("✅ DeepFace encoding extraction works!")
            print(f"Encoding shape: {encoding.shape}")
            
            # Test self-comparison
            similarity = compare_faces_deepface(encoding, encoding)
            if similarity is not None:
                print(f"Self-similarity: {similarity:.1f}%")
                
                if similarity > 95:
                    print("✅ DeepFace is working perfectly!")
                    success = True
                else:
                    print("⚠️ DeepFace comparison needs tuning")
                    success = False
            else:
                print("❌ DeepFace comparison failed")
                success = False
        else:
            print("❌ DeepFace encoding extraction failed")
            success = False
        
        # Clean up
        if os.path.exists('test_deepface.jpg'):
            os.remove('test_deepface.jpg')
        
        return success
        
    except Exception as e:
        print(f"❌ DeepFace test failed: {e}")
        return False

if __name__ == "__main__":
    test_deepface()
