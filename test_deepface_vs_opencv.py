#!/usr/bin/env python3
"""
Comparison test: DeepFace vs OpenCV face recognition accuracy
This demonstrates why DeepFace is superior for face matching
"""

import cv2
import numpy as np
import os
import time

def create_test_faces():
    """Create test face images with variations."""
    
    def create_face(filename, face_color=(200, 180, 160), eye_size=8, mouth_width=20):
        """Create a synthetic face with specified parameters."""
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Face outline (circle)
        cv2.circle(img, (100, 100), 80, face_color, -1)
        
        # Eyes
        cv2.circle(img, (80, 80), eye_size, (50, 50, 50), -1)
        cv2.circle(img, (120, 80), eye_size, (50, 50, 50), -1)
        
        # Nose
        cv2.line(img, (100, 90), (100, 110), (100, 100, 100), 2)
        
        # Mouth
        cv2.ellipse(img, (100, 130), (mouth_width, 10), 0, 0, 180, (100, 100, 100), 2)
        
        cv2.imwrite(filename, img)
        return img
    
    # Create original face
    create_face('face_original.jpg')
    
    # Create same face with slight variations
    create_face('face_same_person.jpg', face_color=(205, 185, 165), eye_size=9)
    
    # Create different face
    create_face('face_different_person.jpg', face_color=(180, 160, 140), eye_size=6, mouth_width=15)
    
    print("✅ Created test face images")

def test_opencv_accuracy():
    """Test OpenCV face recognition accuracy."""
    print("\n🔍 Testing OpenCV Face Recognition...")
    
    try:
        from opencv_face_recognition import extract_face_features_opencv, compare_faces_opencv
        
        # Extract features
        features_original = extract_face_features_opencv('face_original.jpg')
        features_same = extract_face_features_opencv('face_same_person.jpg')
        features_different = extract_face_features_opencv('face_different_person.jpg')
        
        if features_original is None:
            print("❌ OpenCV failed to extract features")
            return None
        
        # Test same person
        similarity_same = compare_faces_opencv(features_original, features_same)
        
        # Test different person
        similarity_different = compare_faces_opencv(features_original, features_different)
        
        # Test identical image
        similarity_identical = compare_faces_opencv(features_original, features_original)
        
        results = {
            'identical': similarity_identical,
            'same_person': similarity_same,
            'different_person': similarity_different,
            'method': 'OpenCV'
        }
        
        print(f"  Identical image: {similarity_identical:.1f}%")
        print(f"  Same person (variation): {similarity_same:.1f}%")
        print(f"  Different person: {similarity_different:.1f}%")
        
        return results
        
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return None

def test_deepface_accuracy():
    """Test DeepFace accuracy."""
    print("\n🤖 Testing DeepFace Recognition...")
    
    try:
        from deepface_recognition import extract_face_encoding_deepface, compare_faces_deepface
        
        start_time = time.time()
        
        # Extract features
        features_original = extract_face_encoding_deepface('face_original.jpg')
        features_same = extract_face_encoding_deepface('face_same_person.jpg')
        features_different = extract_face_encoding_deepface('face_different_person.jpg')
        
        if features_original is None:
            print("❌ DeepFace failed to extract features")
            return None
        
        # Test same person
        similarity_same = compare_faces_deepface(features_original, features_same)
        
        # Test different person
        similarity_different = compare_faces_deepface(features_original, features_different)
        
        # Test identical image
        similarity_identical = compare_faces_deepface(features_original, features_original)
        
        end_time = time.time()
        
        results = {
            'identical': similarity_identical,
            'same_person': similarity_same,
            'different_person': similarity_different,
            'method': 'DeepFace',
            'time': end_time - start_time
        }
        
        print(f"  Identical image: {similarity_identical:.1f}%")
        print(f"  Same person (variation): {similarity_same:.1f}%")
        print(f"  Different person: {similarity_different:.1f}%")
        print(f"  Processing time: {end_time - start_time:.2f} seconds")
        
        return results
        
    except Exception as e:
        print(f"❌ DeepFace test failed: {e}")
        return None

def analyze_results(opencv_results, deepface_results):
    """Analyze and compare the results."""
    print("\n" + "="*50)
    print("📊 ACCURACY COMPARISON RESULTS")
    print("="*50)
    
    if opencv_results and deepface_results:
        print("\n🎯 IDENTICAL IMAGE MATCHING:")
        print(f"  OpenCV:   {opencv_results['identical']:.1f}%")
        print(f"  DeepFace: {deepface_results['identical']:.1f}%")
        
        print("\n👥 SAME PERSON (with variations):")
        print(f"  OpenCV:   {opencv_results['same_person']:.1f}%")
        print(f"  DeepFace: {deepface_results['same_person']:.1f}%")
        
        print("\n🚫 DIFFERENT PERSON (should be low):")
        print(f"  OpenCV:   {opencv_results['different_person']:.1f}%")
        print(f"  DeepFace: {deepface_results['different_person']:.1f}%")
        
        # Determine winner
        print("\n🏆 WINNER ANALYSIS:")
        
        # Check identical image accuracy
        if deepface_results['identical'] > opencv_results['identical']:
            print("  ✅ DeepFace wins on identical image matching")
        else:
            print("  ✅ OpenCV wins on identical image matching")
        
        # Check same person discrimination
        if deepface_results['same_person'] > opencv_results['same_person']:
            print("  ✅ DeepFace better at recognizing same person with variations")
        else:
            print("  ✅ OpenCV better at recognizing same person with variations")
        
        # Check different person discrimination
        deepface_discrimination = 100 - deepface_results['different_person']
        opencv_discrimination = 100 - opencv_results['different_person']
        
        if deepface_discrimination > opencv_discrimination:
            print("  ✅ DeepFace better at distinguishing different people")
        else:
            print("  ✅ OpenCV better at distinguishing different people")
        
        # Overall recommendation
        deepface_score = (
            deepface_results['identical'] + 
            deepface_results['same_person'] + 
            deepface_discrimination
        ) / 3
        
        opencv_score = (
            opencv_results['identical'] + 
            opencv_results['same_person'] + 
            opencv_discrimination
        ) / 3
        
        print(f"\n📈 OVERALL SCORES:")
        print(f"  DeepFace: {deepface_score:.1f}%")
        print(f"  OpenCV:   {opencv_score:.1f}%")
        
        if deepface_score > opencv_score:
            print("\n🎉 RECOMMENDATION: Use DeepFace for better accuracy!")
        else:
            print("\n🎉 RECOMMENDATION: OpenCV is sufficient for your use case!")
            
    elif deepface_results:
        print("✅ DeepFace is working perfectly!")
        print("❌ OpenCV not available for comparison")
        
    elif opencv_results:
        print("✅ OpenCV is working")
        print("❌ DeepFace not available for comparison")
        
    else:
        print("❌ Neither system is working properly")

def cleanup_test_files():
    """Clean up test files."""
    test_files = ['face_original.jpg', 'face_same_person.jpg', 'face_different_person.jpg']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    print("🧹 Cleaned up test files")

def main():
    """Run the comparison test."""
    print("🎯 DeepFace vs OpenCV Accuracy Comparison")
    print("="*50)
    
    # Create test images
    create_test_faces()
    
    # Test both systems
    opencv_results = test_opencv_accuracy()
    deepface_results = test_deepface_accuracy()
    
    # Analyze results
    analyze_results(opencv_results, deepface_results)
    
    # Cleanup
    cleanup_test_files()
    
    print("\n✅ Comparison test completed!")

if __name__ == "__main__":
    main()
