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
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-' + str(uuid.uuid4()))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Extended session timeout
Session(app)
bcrypt = Bcrypt(app)

#Database configuration and folder
app.config['DATABASE'] = 'child_registry.db'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Initialize upload folder and database
create_upload_folder()
create_face_encodings_column()

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

def is_admin(username):
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data and user_data[0] == 1:
        return True
    return False

def retrieve_child_info(huduma_number):
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM children WHERE huduma_number = ?', (huduma_number,))
    child = cursor.fetchone()
    conn.close()
    return child

def reset_user_password(username, new_password):
    password_hash = generate_password_hash(new_password)
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
    conn.commit()
    conn.close()

# Connect to the database and create users table if not exists
conn = sqlite3.connect('child_registry.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0
    )
''')
conn.commit()

# Check if there's no admin, create one
cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
admin_count = cursor.fetchone()[0]
if admin_count == 0:
    default_admin_username = 'admin'
    default_admin_password = 'admin_password'  # You should set a strong password here
    add_user(default_admin_username, default_admin_password, is_admin=True)

conn.close()

@app.route('/')
def landing_page():
    return render_template('modern_landing.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('register.html', error='Username and password are required.')
        
        # Check if username already exists
        conn = sqlite3.connect('child_registry.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()
        conn.close()
        
        if existing_user:
            return render_template('register.html', error='Username already exists. Please choose a different username.')
        
        try:
            add_user(username, password)
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('register.html', error='An error occurred during registration. Please try again.')
    
    return render_template('register.html')

@app.route('/delete_child', methods=['POST'])
def delete_child():
    if 'username' in session and is_admin(session['username']):
        huduma_number = request.form.get('huduma_number')
        conn = sqlite3.connect('child_registry.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM children WHERE huduma_number = ?', (huduma_number,))
        conn.commit()
        conn.close()
        flash('Child deleted successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('You are not authorized to perform this action.', 'error')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.args.get('role')  # Get the role from the query parameters

        if not (username and password and role):  # Check if username, password, and role are provided
            return render_template('login.html', error='Username, password, and role are required.')

        # Authenticate based on the provided role
        if role == 'admin':
            if not is_admin(username):  # Check if the user is an admin
                return render_template('login.html', error='Invalid credentials for admin role.')
        elif role == 'user':  # Handle the case for the "User" role
            if is_admin(username):  # Check if the user is not an admin
                return render_template('login.html', error='Invalid credentials for user role.')

        # Authentication successful, proceed to dashboard based on the role
        if authenticate(username, password):
            session['username'] = username
            session['role'] = role  # Set the role in the session
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password.')

    # If it's a GET request or invalid POST request, render the login page
    return render_template('login.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form.get('username')
        new_password = request.form.get('new_password')

        if not (username and new_password):
            flash('Username and new password are required.', 'error')
            return redirect(url_for('reset_password'))

        if authenticate(username, new_password):
            flash('New password must be different from the old one.', 'error')
            return redirect(url_for('reset_password'))

        reset_user_password(username, new_password)
        flash('Password reset successfully. Please log in with your new password.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' in session:
        username = session['username']
        if is_admin(username):
            if request.method == 'POST':
                user_id = request.form.get('user_id')
                action = request.form.get('action')
                if user_id:
                    if action == 'promote':
                        promote_user_to_admin(user_id)
                        flash('User promoted to admin successfully.', 'success')
                    elif action == 'demote':
                        demote_admin_to_user(user_id)
                        flash('User demoted to regular user successfully.', 'success')
                    else:
                        flash('Invalid action.', 'error')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('User ID is required.', 'error')
            return render_template('admin_dashboard.html')
        else:
            # Redirect non-admin users to the landing page
            return redirect(url_for('landing_page'))
    else:
        # Redirect unauthenticated users to the login page
        return redirect(url_for('login'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'username' in session:
        username = session['username']
        if not is_admin(username):
            # Fetch user-specific data
            return render_template('user_dashboard.html')
        else:
            # Redirect admin users to the landing page
            return redirect(url_for('landing_page'))
    else:
        # Redirect unauthenticated users to the login page
        return redirect(url_for('login'))

@app.route('/update_child', methods=['GET', 'POST'])
def update_child():
    if request.method == 'POST':
        huduma_number = request.form.get('huduma_number')
        conn = sqlite3.connect('child_registry.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM children WHERE huduma_number = ?", (huduma_number,))
        child = cursor.fetchone()
        conn.close()
        if child:
            return render_template('update_child.html', child=child)
        else:
            flash('Child with the specified Huduma number not found.', 'error')
            return redirect(url_for('user_dashboard'))
    return render_template('update_child_form.html')

@app.route('/update_child_submit', methods=['POST'])
def update_child_submit():
    huduma_number = request.form.get('huduma_number')
    # Fetch updated information from the form
    updated_info = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'dob': request.form.get('dob'),
        'gender': request.form.get('gender'),
        # Include other fields as needed
    }
    conn = sqlite3.connect('child_registry.db')
    cursor = conn.cursor()
    # Update child's information in the database
    cursor.execute("""
        UPDATE children
        SET first_name=?, last_name=?, dob=?, gender=?
        WHERE huduma_number=?
    """, (updated_info['first_name'], updated_info['last_name'], updated_info['dob'], updated_info['gender'], huduma_number))
    conn.commit()
    conn.close()
    flash('Child information updated successfully.', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/retrieve_child_information', methods=['POST', 'GET'])
def retrieve_child_information():
    huduma_number = request.form.get('huduma_number')

    if huduma_number is None:
        flash('Huduma number is required.', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Retrieve child information from the database based on huduma number
    child = retrieve_child_info(huduma_number)

    if child:
        # Construct the file path for the child photo
        picture_filename = child[15]  # Assuming the picture filename is stored in the 16th column
        if picture_filename:
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_filename)
        else:
            # If no photo is available, use a placeholder image or display a message
            picture_path = None  # Set to None or provide a default image path

        # Render the child information page with the retrieved data
        return render_template('child_information.html', child={
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
            'picture_path': picture_path  # Pass the picture_path variable to the template
        })
    else:
        flash('Child not found', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/update_child_form')
def update_child_form():
    return render_template('update_child_form.html')

@app.route('/search_lost_child', methods=['POST'])
def search_lost_child():
    # Ensure the user is logged in and has the appropriate role
    if 'role' in session:
        role = session['role']
    else:
        flash('Unauthorized access', 'error')
        return redirect(url_for('login'))

    if 'lost_child_photo' not in request.files:
        flash("No photo uploaded.", 'danger')
        return redirect(url_for('admin_dashboard' if role == 'admin' else 'user_dashboard'))
    
    lost_child_photo = request.files['lost_child_photo']
    
    if lost_child_photo.filename == '' or not allowed_file(lost_child_photo.filename):
        flash("Please upload a valid image file (PNG, JPG, JPEG, GIF).", 'danger')
        return redirect(url_for('admin_dashboard' if role == 'admin' else 'user_dashboard'))
    
    # For now, without face recognition, we'll just show a message
    flash("Photo uploaded successfully! Face recognition feature requires additional setup. Please check the README for installation instructions.", 'info')
    flash("For now, you can manually search for children using the 'Retrieve Child Information' feature.", 'info')
    
    # Redirect to the appropriate dashboard based on user role
    return redirect(url_for('admin_dashboard' if role == 'admin' else 'user_dashboard'))

@app.route('/register_child', methods=['GET', 'POST'])
def register_child():
    if request.method == 'POST':
        if 'username' not in session:
            flash('You need to log in to register a child.', 'error')
            return redirect(url_for('login'))

        # Extract child registration data from the form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        huduma_number = request.form.get('huduma_number')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        mother_first_name = request.form.get('mother_first_name')
        mother_last_name = request.form.get('mother_last_name')
        father_first_name = request.form.get('father_first_name')
        father_last_name = request.form.get('father_last_name')
        mother_contact = request.form.get('mother_contact')
        father_contact = request.form.get('father_contact')
        county = request.form.get('county')
        sub_county = request.form.get('sub_county')
        ward = request.form.get('ward')

        # Validate required fields
        required_fields = [first_name, last_name, huduma_number, dob, mother_first_name, 
                          mother_last_name, mother_contact]
        if not all(required_fields):
            flash('Please fill in all required fields.', 'error')
            return render_template('child_registration.html')

        photo_name = None
        child_id = None
        
        # Check if a file was uploaded
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '' and allowed_file(photo.filename):
                # Generate unique filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(photo.filename)
                name, ext = os.path.splitext(filename)
                photo_name = f"{name}_{timestamp}{ext}"
                
                # Save the file locally
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_name)
                photo.save(photo_path)
            elif photo.filename != '':
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                return render_template('child_registration.html')

        try:
            # Insert child data into the database
            conn = sqlite3.connect('child_registry.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO children (first_name, last_name, huduma_number, dob, gender,
                                      mother_first_name, mother_last_name, father_first_name,
                                      father_last_name, mother_contact, father_contact,
                                      county, sub_county, ward, picture)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, huduma_number, dob, gender, mother_first_name,
                  mother_last_name, father_first_name, father_last_name, mother_contact,
                  father_contact, county, sub_county, ward, photo_name))
            
            child_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            flash('Child registered successfully!', 'success')
            
        except sqlite3.IntegrityError:
            flash('A child with this Huduma number already exists.', 'error')
            if photo_name:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_name)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            return render_template('child_registration.html')
        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'error')
            if photo_name:
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_name)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            return render_template('child_registration.html')

        if is_admin(session['username']):
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    return render_template('child_registration.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('landing_page'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
