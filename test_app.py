#!/usr/bin/env python3
"""
Test script for ChildSafe application
This script tests basic functionality and face recognition availability
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import sqlite3
        print("✅ SQLite3 imported successfully")
    except ImportError as e:
        print(f"❌ SQLite3 import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Pillow import failed: {e}")
        return False
    
    return True

def test_face_recognition():
    """Test if face recognition libraries are available."""
    print("\n🔍 Testing face recognition libraries...")
    
    try:
        import face_recognition
        print("✅ face_recognition imported successfully")
        
        try:
            import cv2
            print("✅ opencv-python imported successfully")
        except ImportError:
            print("⚠️  opencv-python not available (optional)")
        
        try:
            import numpy as np
            print("✅ numpy imported successfully")
        except ImportError as e:
            print(f"❌ numpy import failed: {e}")
            return False
            
        return True
        
    except ImportError as e:
        print(f"⚠️  face_recognition not available: {e}")
        print("💡 To install: pip install face-recognition")
        return False

def test_database():
    """Test database connectivity."""
    print("\n🗄️  Testing database...")
    
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')  # Test with in-memory database
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        conn.close()
        
        if result[0] == 1:
            print("✅ Database connectivity test passed")
            return True
        else:
            print("❌ Database test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_directories():
    """Test if required directories exist or can be created."""
    print("\n📁 Testing directories...")
    
    directories = ['uploads', 'flask_session']
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ Created directory: {directory}")
            else:
                print(f"✅ Directory exists: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_app_import():
    """Test if the app can be imported without errors."""
    print("\n🚀 Testing app import...")
    
    try:
        # Try importing the main app
        sys.path.insert(0, os.getcwd())
        import app
        print("✅ Main app imported successfully")
        
        # Check if face recognition is available in the app
        if hasattr(app, 'FACE_RECOGNITION_AVAILABLE'):
            if app.FACE_RECOGNITION_AVAILABLE:
                print("✅ Face recognition is available in the app")
            else:
                print("⚠️  Face recognition is not available in the app")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import main app: {e}")
        
        # Try importing the simple app
        try:
            import app_simple
            print("✅ Simple app imported successfully")
            return True
        except ImportError as e2:
            print(f"❌ Failed to import simple app: {e2}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error importing app: {e}")
        return False

def main():
    """Run all tests."""
    print("🎯 ChildSafe Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_imports),
        ("Face Recognition", test_face_recognition),
        ("Database", test_database),
        ("Directories", test_directories),
        ("App Import", test_app_import),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your ChildSafe application is ready to use.")
        print("\n🚀 To start the application:")
        print("   python app.py        # Full version (if face recognition is available)")
        print("   python app_simple.py # Simple version (always works)")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        if passed >= 3:  # If basic functionality works
            print("\n💡 You can still use the simple version:")
            print("   python app_simple.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
