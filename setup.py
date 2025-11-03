#!/usr/bin/env python3
"""
ChildSafe Setup Script
This script helps set up the ChildSafe application with all necessary dependencies.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_banner():
    """Print the ChildSafe setup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                        ChildSafe Setup                        ║
    ║               Child Registration & Identification             ║
    ║                                                               ║
    ║  This setup will install all dependencies and prepare         ║
    ║  your ChildSafe application for first use.                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("\n💡 Try installing manually with:")
        print("   pip install -r requirements.txt")
        return False

def setup_database():
    """Set up the SQLite database with required tables."""
    print("\n🗄️  Setting up database...")
    
    try:
        # Run the database creation script
        subprocess.check_call([sys.executable, "create_database.py"])
        
        # Verify database was created
        if os.path.exists("child_registry.db"):
            print("✅ Database created successfully!")
            
            # Add face_encoding column if it doesn't exist
            conn = sqlite3.connect("child_registry.db")
            cursor = conn.cursor()
            
            try:
                cursor.execute("PRAGMA table_info(children)")
                columns = cursor.fetchall()
                column_names = [column[1] for column in columns]
                
                if 'face_encoding' not in column_names:
                    cursor.execute('ALTER TABLE children ADD COLUMN face_encoding TEXT')
                    conn.commit()
                    print("✅ Added face_encoding column to database")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not add face_encoding column: {e}")
            
            conn.close()
            return True
        else:
            print("❌ Database creation failed!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = ["uploads", "flask_session"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created/verified directory: {directory}")

def setup_environment():
    """Create environment configuration file."""
    print("\n🔧 Setting up environment...")
    
    env_content = """# ChildSafe Environment Configuration
# Copy this to .env and customize as needed

# Security
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///child_registry.db

# Upload settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Face recognition settings
FACE_RECOGNITION_TOLERANCE=0.6
SIMILARITY_THRESHOLD=70

# Session settings
SESSION_TIMEOUT_MINUTES=30
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env.example file")
    print("💡 Copy .env.example to .env and customize settings")

def print_next_steps():
    """Print next steps for the user."""
    next_steps = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                          Setup Complete!                      ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║                                                               ║
    ║  Next Steps:                                                  ║
    ║                                                               ║
    ║  1. Copy .env.example to .env and customize settings         ║
    ║  2. Run the application:                                      ║
    ║     python app.py                                             ║
    ║                                                               ║
    ║  3. Open your browser and go to:                             ║
    ║     http://localhost:5000                                     ║
    ║                                                               ║
    ║  Default admin credentials:                                   ║
    ║     Username: admin                                           ║
    ║     Password: admin_password                                  ║
    ║                                                               ║
    ║  ⚠️  IMPORTANT: Change the default admin password!            ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(next_steps)

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Setup completed with warnings. You may need to install dependencies manually.")
    
    # Setup database
    if not setup_database():
        print("\n⚠️  Database setup failed. You may need to run create_database.py manually.")
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
