from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask_session import Session
from functools import wraps
from datetime import timedelta
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
from flask import send_from_directory
import sqlite3
import os
# Try to import face recognition libraries (DeepFace preferred, OpenCV fallback)
try:
    from deepface_recognition import (
        extract_face_encoding_deepface,
        compare_faces_deepface,
        save_face_encoding_deepface,
        get_face_encoding_from_db_deepface,
        verify_faces_deepface
    )
    FACE_RECOGNITION_AVAILABLE = True
    FACE_RECOGNITION_METHOD = 'deepface'
    print("🤖 DeepFace (state-of-the-art) face recognition is available!")
except ImportError:
    try:
        import cv2
        import numpy as np
        from opencv_face_recognition import (
            detect_faces_opencv,
            extract_face_features_opencv,
            compare_faces_opencv,
            save_face_features_opencv,
            get_face_features_from_db_opencv
        )
        FACE_RECOGNITION_AVAILABLE = True
        FACE_RECOGNITION_METHOD = 'opencv'
        print("✅ OpenCV-based face recognition is available!")
    except ImportError as e:
        FACE_RECOGNITION_AVAILABLE = False
        FACE_RECOGNITION_METHOD = None
        print(f"Warning: Face recognition libraries not available: {e}")
        print("To enable face recognition, please install: pip install deepface")

import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-' + str(uuid.uuid4()))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Extended session timeout
Session(app)
bcrypt = Bcrypt(app)

#Database configuration and folder
app.config['DATABASE'] = 'missing_persons.db'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_face_encoding(image_path_or_bytes):
    """
    Extract face encoding from an image file or bytes using the best available method.
    
    Args:
    - image_path_or_bytes: Path to image file or image bytes
    
    Returns:
    - Face encoding array or None if no face found
    """
    if not FACE_RECOGNITION_AVAILABLE:
        print("Face recognition not available. Please install required libraries.")
        return None
        
    try:
        if FACE_RECOGNITION_METHOD == 'deepface':
            return extract_face_encoding_deepface(image_path_or_bytes)
        else:
            return extract_face_features_opencv(image_path_or_bytes)
    except Exception as e:
        print(f"Error extracting face encoding: {str(e)}")
        return None

def compare_faces(known_encoding, unknown_image_path_or_bytes, tolerance=0.6):
    """
    Compare a known face encoding with an unknown image using the best available method.
    
    Args:
    - known_encoding: Known face encoding array
    - unknown_image_path_or_bytes: Path to unknown image or image bytes
    - tolerance: Face matching tolerance (lower is more strict)
    
    Returns:
    - Similarity score (0-100, higher is more similar) or None if no face found
    """
    if not FACE_RECOGNITION_AVAILABLE:
        print("Face recognition not available. Please install required libraries.")
        return None
        
    try:
        if FACE_RECOGNITION_METHOD == 'deepface':
            # For DeepFace, we can use direct verification for better accuracy
            result = verify_faces_deepface(known_encoding, unknown_image_path_or_bytes)
            if result:
                return result.get('similarity', 0)
            else:
                # Fallback to encoding comparison
                unknown_encoding = extract_face_encoding(unknown_image_path_or_bytes)
                if unknown_encoding is None:
                    return None
                return compare_faces_deepface(known_encoding, unknown_encoding)
        else:
            unknown_encoding = extract_face_encoding(unknown_image_path_or_bytes)
            if unknown_encoding is None:
                return None
            return compare_faces_opencv(known_encoding, unknown_encoding)
    except Exception as e:
        print(f"Error comparing faces: {str(e)}")
        return None

def save_face_encoding(image_path, child_id):
    """
    Save face encoding to database for faster future comparisons using the best available method.
    
    Args:
    - image_path: Path to the child's image
    - child_id: Child's database ID
    
    Returns:
    - True if successful, False otherwise
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return False
        
    try:
        conn = sqlite3.connect('child_registry.db')
        if FACE_RECOGNITION_METHOD == 'deepface':
            result = save_face_encoding_deepface(image_path, child_id, conn)
        else:
            result = save_face_features_opencv(image_path, child_id, conn)
        conn.close()
        return result
    except Exception as e:
        print(f"Error saving face encoding: {str(e)}")
    return False

def get_face_encoding_from_db(child_id):
    """
    Retrieve face encoding from database using the best available method.
    
    Args:
    - child_id: Child's database ID
    
    Returns:
    - Face encoding array or None
    """
    if not FACE_RECOGNITION_AVAILABLE:
        return None
        
    try:
        conn = sqlite3.connect('child_registry.db')
        if FACE_RECOGNITION_METHOD == 'deepface':
            result = get_face_encoding_from_db_deepface(child_id, conn)
        else:
            result = get_face_features_from_db_opencv(child_id, conn)
        conn.close()
        return result
    except Exception as e:
        print(f"Error retrieving face encoding: {str(e)}")
    return None

def create_upload_folder():
    """Create upload folder if it doesn't exist."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def create_face_encodings_column():
    """Add face_encoding column to children table if it doesn't exist."""
    try:
        conn = sqlite3.connect('child_registry.db')
        cursor = conn.cursor()
        
        # Check if face_encoding column exists
        cursor.execute("PRAGMA table_info(children)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'face_encoding' not in column_names:
            cursor.execute('ALTER TABLE children ADD COLUMN face_encoding TEXT')
            conn.commit()
        
        conn.close()
    except Exception as e:
        print(f"Error creating face_encoding column: {str(e)}")

# Dummy database functions and authentication functions

def add_user(username, password, is_admin=False):
    password_hash = generate_password_hash(password)
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
                   (username, password_hash, is_admin))
    conn.commit()
    conn.close()

def promote_user_to_admin(user_id):
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_admin = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def demote_admin_to_user(user_id):
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_admin = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data and check_password_hash(user_data[0], password):
        return True
    return False

# User Authentication
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            if request.endpoint != 'login':
                flash('You need to log in first.', 'danger')
            return redirect(url_for('login'))

    return wrap

@app.route('/user_dashboard')
def user_dashboard():
    if 'username' in session:
        return render_template('modern_dashboard.html')
    else:
        flash('You need to log in first.', 'error')
        return redirect(url_for('login'))

def is_admin(username):
    conn = sqlite3.connect('child_registry.db')
{{ ... }}
            flash(f'An error occurred during registration: {str(e)}', 'error')
            if photo_name:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_name)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            return render_template('child_registration.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and is_admin(session['username']):
        return render_template('modern_dashboard.html')
    else:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
{{ ... }}
    return redirect(url_for('landing_page'))

@app.route('/match_details')
def match_details():
    """Display detailed information about a matched child."""
    if 'match_details' not in session:
        flash('No match details available.', 'info')
        return redirect(url_for('user_dashboard'))
    
    match = session['match_details']
    
    # Get full child information
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM children WHERE id = ?', (match['id'],))
    child = cursor.fetchone()
    conn.close()
    
    if child:
        child_info = {
            'id': child[0],
            'first_name': child[1],
            'last_name': child[2],
            'huduma_number': child[3],
            'date_of_birth': child[4],
            'gender': child[5],
            'mother_first_name': child[6],
            'mother_last_name': child[7],
            'father_first_name': child[8],
            'father_last_name': child[9],
            'mother_contact': child[10],
            'father_contact': child[11],
            'county': child[12],
            'sub_county': child[13],
            'ward': child[14],
            'picture_filename': child[15],
            'similarity': match['similarity']
        }
        return render_template('match_details.html', child=child_info)
    else:
        flash('Child information not found.', 'error')
        return redirect(url_for('user_dashboard'))

def create_tables():
    """Create the necessary database tables if they don't exist."""
    conn = sqlite3.connect('missing_persons.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create missing_persons table (expanded from children)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS missing_persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_type TEXT NOT NULL DEFAULT 'child',
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            identification_number TEXT UNIQUE NOT NULL,
            dob DATE NOT NULL,
            age INTEGER,
            gender TEXT,
            height TEXT,
            weight TEXT,
            eye_color TEXT,
            hair_color TEXT,
            distinguishing_marks TEXT,
            medical_conditions TEXT,
            medications TEXT,
            last_seen_location TEXT,
            last_seen_date DATE,
            last_seen_time TIME,
            clothing_description TEXT,
            guardian_first_name TEXT,
            guardian_last_name TEXT,
            guardian_relationship TEXT,
            guardian_contact TEXT,
            emergency_contact TEXT,
            county TEXT,
            sub_county TEXT,
            ward TEXT,
            picture TEXT,
            face_encoding TEXT,
            status TEXT DEFAULT 'missing',
            priority_level TEXT DEFAULT 'medium',
            case_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create case_updates table for tracking progress
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            update_type TEXT NOT NULL,
            description TEXT,
            location TEXT,
            updated_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES missing_persons (id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)









