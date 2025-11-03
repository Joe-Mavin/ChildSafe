# Face Recognition Setup Guide

This guide will help you set up the advanced face recognition features for ChildSafe.

## 🚨 Important Note

The face recognition functionality requires additional setup due to system dependencies. We've provided two versions:

1. **`app_simple.py`** - Basic version without face recognition (works immediately)
2. **`app.py`** - Full version with face recognition (requires additional setup)

## 🛠️ Prerequisites for Face Recognition

### Windows Users

1. **Install Visual Studio Build Tools**
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "C++ build tools" workload

2. **Install CMake**
   - Download from: https://cmake.org/download/
   - During installation, select "Add CMake to system PATH"
   - Verify installation: `cmake --version`

3. **Install dlib (Method 1 - Recommended)**
   ```bash
   pip install dlib
   ```

4. **Install dlib (Method 2 - If Method 1 fails)**
   ```bash
   # Download pre-compiled wheel from:
   # https://github.com/sachadee/Dlib
   pip install dlib-19.22.99-cp311-cp311-win_amd64.whl
   ```

5. **Install face_recognition**
   ```bash
   pip install face_recognition
   ```

### macOS Users

1. **Install Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

2. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Install CMake**
   ```bash
   brew install cmake
   ```

4. **Install dlib and face_recognition**
   ```bash
   pip install dlib
   pip install face_recognition
   ```

### Linux Users (Ubuntu/Debian)

1. **Install system dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential cmake
   sudo apt-get install libopenblas-dev liblapack-dev
   sudo apt-get install libx11-dev libgtk-3-dev
   ```

2. **Install Python dependencies**
   ```bash
   pip install dlib
   pip install face_recognition
   ```

### Linux Users (CentOS/RHEL)

1. **Install system dependencies**
   ```bash
   sudo yum groupinstall "Development Tools"
   sudo yum install cmake
   sudo yum install openblas-devel lapack-devel
   ```

2. **Install Python dependencies**
   ```bash
   pip install dlib
   pip install face_recognition
   ```

## 🔄 Switching Between Versions

### To use the simple version (no face recognition):
```bash
python app_simple.py
```

### To use the full version (with face recognition):
1. Complete the setup above
2. Run:
   ```bash
   python app.py
   ```

## 🧪 Testing Face Recognition

After successful installation, test the face recognition:

```python
# test_face_recognition.py
import face_recognition
import numpy as np

# Test if face_recognition is working
print("Testing face_recognition library...")

# Create a simple test
test_image = np.zeros((100, 100, 3), dtype=np.uint8)
try:
    encodings = face_recognition.face_encodings(test_image)
    print("✅ Face recognition library is working!")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 🐳 Docker Alternative

If you're having trouble with local installation, use Docker:

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t childsafe .
docker run -p 5000:5000 childsafe
```

## 🔧 Troubleshooting

### Common Issues

1. **"CMake is not installed"**
   - Install CMake and ensure it's in your PATH
   - Restart your terminal/command prompt

2. **"Microsoft Visual C++ 14.0 is required"** (Windows)
   - Install Visual Studio Build Tools
   - Restart your computer

3. **"No module named 'dlib'"**
   - Try installing pre-compiled wheels
   - Use conda instead: `conda install -c conda-forge dlib`

4. **Memory errors during compilation**
   - Close other applications
   - Try installing with: `pip install --no-cache-dir dlib`

5. **"Failed building wheel for dlib"**
   - Ensure all prerequisites are installed
   - Try using conda: `conda install -c conda-forge dlib face_recognition`

### Alternative Installation Methods

#### Using Conda (Recommended for difficult cases)
```bash
# Install Anaconda or Miniconda first
conda create -n childsafe python=3.9
conda activate childsafe
conda install -c conda-forge dlib face_recognition
pip install flask flask-session flask-bcrypt werkzeug pillow opencv-python numpy
```

#### Using Pre-compiled Wheels
For Windows users, download pre-compiled wheels from:
- https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib

## 📊 Performance Optimization

Once face recognition is working, you can optimize performance:

1. **Reduce image size before processing**
2. **Use face encoding caching** (already implemented)
3. **Adjust similarity threshold** in the code
4. **Use GPU acceleration** (if available)

## 🆘 Getting Help

If you're still having issues:

1. Check the [dlib installation guide](http://dlib.net/compile.html)
2. Visit the [face_recognition GitHub issues](https://github.com/ageitgey/face_recognition/issues)
3. Try the Docker approach
4. Use the simple version for now and add face recognition later

## ✅ Verification

After successful installation, you should be able to:

1. Run `python app.py` without errors
2. Upload photos during child registration
3. Search for lost children using photos
4. See similarity percentages in search results

The application will automatically detect if face recognition is available and enable/disable features accordingly.
