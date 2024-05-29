from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import boto3
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

app = Flask(__name__)
#app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['AWS_REGION'] = 'us-west-1'
app.config['AWS_ACCESS_KEY_ID'] = 'AKIAXYKJSCVLE33V6WMD'
app.config['AWS_SECRET_ACCESS_KEY'] = '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'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=3)  # Set the session timeout to 3 minutes
Session(app)
bcrypt = Bcrypt(app)

#bucket name configuration
AWS_BUCKET_NAME = 'child-face-match'

#Database configuration and folder
app.config['DATABASE'] = 'child_registry.db'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def crop_image(image_bytes, bbox):
    """
    Crop the image using the bounding box coordinates.

    Args:
    - image_bytes: Bytes of the image file.
    - bbox: Bounding box coordinates (dictionary containing 'Width', 'Height', 'Left', 'Top' keys).

    Returns:
    - Bytes of the cropped image.
    """
    # Open the image from bytes
    image = Image.open(BytesIO(image_bytes))

    # Get the image size
    image_width, image_height = image.size

    # Calculate the cropping box
    left = bbox['Left'] * image_width
    top = bbox['Top'] * image_height
    right = left + bbox['Width'] * image_width
    bottom = top + bbox['Height'] * image_height

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))

    # Convert the cropped image to bytes
    cropped_image_bytes = BytesIO()
    cropped_image.save(cropped_image_bytes, format='JPEG')
    cropped_image_bytes = cropped_image_bytes.getvalue()

    return cropped_image_bytes

def create_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

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

# Function to upload file to AWS S3 bucket
def upload_to_s3(file, bucket_name, object_name):
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(file, bucket_name, object_name)
        return True
    except Exception as e:
        app.logger.error("Error uploading file to S3: %s", str(e))
        return False

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

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
        add_user(username, password)
        return redirect(url_for('login'))
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

    # Connect to the SQLite database
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()

        # Fetch children data from the database
        cursor.execute("SELECT * FROM children")
        database_children = cursor.fetchall()

    if 'lost_child_photo' in request.files:
        lost_child_photo = request.files['lost_child_photo']

        if lost_child_photo:
            # Perform facial recognition on the uploaded photo
            try:
                rekognition_client = boto3.client(
                    'rekognition',
                    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
                    region_name=app.config['AWS_REGION']
                )

                # Read the contents of the uploaded photo
                image_bytes = lost_child_photo.read()

                # Perform face detection
                response = rekognition_client.detect_faces(
                    Image={'Bytes': image_bytes},
                    Attributes=['ALL']
                )

                # Check if faces are detected
                if response['FaceDetails']:
                    for face in response['FaceDetails']:
                        bbox = face['BoundingBox']
                        cropped_image_bytes = crop_image(image_bytes, bbox)

                        for child in database_children:
                            picture_name = child[15]  # Assuming picture_key is at index 13
                            object_key = f'uploads1/{picture_name}'

                            # Compare the lost child's photo with each registered child's photo
                            similarity = rekognition_client.compare_faces(
                                SourceImage={'Bytes': cropped_image_bytes},
                                TargetImage={'S3Object': {'Bucket': AWS_BUCKET_NAME, 'Name': object_key}}
                            )

                            # Check if the similarity is above a certain threshold (e.g., 90%)
                            if similarity['FaceMatches'] and similarity['FaceMatches'][0]['Similarity'] >= 90:
                                flash(f"Lost child found! Name: {child[1]} {child[2]}", "success")
                                flash(f"Huduma Number:{child[3]}", "success")
                                if role == 'admin':
                                    return redirect(url_for('admin_dashboard'))
                                else:
                                    return redirect(url_for('user_dashboard'))

                    # If no matching child is found
                    flash("No matching child found in the database", "danger")
                else:
                    flash("No faces detected in the uploaded photo.", 'danger')
            except Exception as e:
                flash(f"An error occurred: {str(e)}", 'danger')
        else:
            flash("No lost child photo uploaded.", 'danger')
    else:
        flash("No lost child photo uploaded.", 'danger')

    # Redirect to the appropriate dashboard based on user role
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

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

        # Check if a file was uploaded
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                # Securely generate filename
                photo_name = secure_filename(photo.filename)

                # Upload the file to S3
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
                    region_name=app.config['AWS_REGION']
                )
                object_key = photo_name  # Storing just the picture name
                s3.upload_fileobj(photo, AWS_BUCKET_NAME, f'uploads1/{photo_name}')

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
        conn.commit()
        conn.close()

        flash('Child registered successfully.', 'success')

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
    app.run(debug=True)









