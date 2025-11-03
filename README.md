ChildSafe: Child Registration and Identification System

![ChildSafe Logo](https://img.shields.io/badge/ChildSafe-v2.0-blue?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.7+-green?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-red?style=for-the-badge&logo=flask&logoColor=white)
![Face Recognition](https://img.shields.io/badge/Face_Recognition-Enabled-orange?style=for-the-badge&logo=face-recognition&logoColor=white)

## 🚀 Overview

ChildSafe is a modern web-based application designed to help reunite lost children with their families using advanced facial recognition technology. The system allows for the registration of children with their photos and essential details. When a child goes missing, anyone who finds them can upload a photo to the platform, which uses **open-source facial recognition** to match the photo with registered profiles and retrieve contact information for the child's guardians.

### ✨ Key Improvements in v2.0
- **🔓 No AWS Dependencies**: Replaced AWS Rekognition with open-source `face_recognition` library
- **💾 Local Storage**: No more S3 dependency - all images stored locally
- **🎨 Modern UI**: Enhanced user interface with responsive design
- **🔒 Improved Security**: Better authentication and data validation
- **⚡ Faster Performance**: Optimized face recognition with database caching
- **📱 Mobile Friendly**: Responsive design works on all devices

## 🌟 Features

### 👶 Child Registration
- **Photo Upload**: Secure photo upload with face validation
- **Detailed Records**: Store comprehensive child information
- **Unique Identification**: Huduma number-based identification system
- **Family Contacts**: Multiple guardian contact information

### 🔍 Advanced Facial Recognition
- **Open Source**: Uses `face_recognition` library (no cloud dependencies)
- **High Accuracy**: Advanced facial matching algorithms
- **Fast Processing**: Optimized for quick search results
- **Multiple Faces**: Handles photos with multiple people

### 👥 User Management
- **Role-Based Access**: Admin and regular user roles
- **Secure Authentication**: Password hashing and session management
- **User Dashboard**: Personalized user interfaces
- **Admin Controls**: User promotion/demotion capabilities

### 🎨 Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Intuitive Navigation**: Easy-to-use interface
- **Real-time Feedback**: Instant search results and notifications
- **Accessibility**: WCAG compliant design
## 🛠️ Installation

### Prerequisites
- **Python 3.7+** (recommended: Python 3.8 or higher)
- **pip** (Python package installer)
- **Git** (for cloning the repository)
- **CMake** (required for dlib compilation)
- **Visual Studio Build Tools** (Windows only)

### 🚀 Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Joe-Mavin/childSafe.git
   cd ChildSafe-main
   ```

2. **Run Automated Setup**
   ```bash
   python setup.py
   ```
   
   The setup script will:
   - Check Python version compatibility
   - Install all required dependencies
   - Set up the database
   - Create necessary directories
   - Generate configuration templates

3. **Manual Installation (Alternative)**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup database
   python create_database.py
   
   # Create upload directory
   mkdir uploads
   ```

### 🔧 Configuration

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

2. **Database Initialization**
   The database will be automatically created with a default admin user:
   - **Username**: `admin`
   - **Password**: `admin_password`
   
   ⚠️ **Important**: Change the default password immediately after first login!

### ▶️ Running the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`
Usage
Access the application:
Open your web browser and navigate to http://127.0.0.1:5000.

Login or Register:

Log in with your email and password.
If you don't have an account, register as a new user.
Navigate the Dashboard:

Regular Users: Register a child, update information, search for lost children.
Admin Users: Manage user roles, update and delete child records.
Upload and Search:

Upload a photo of a found child to search for matches in the system.
## 🏗️ System Architecture

### Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Flask (Python)
- **Database**: SQLite (easily replaceable with PostgreSQL/MySQL)
- **Facial Recognition**: `face_recognition` library (dlib-based)
- **Image Processing**: OpenCV, Pillow
- **Authentication**: Flask-Session, Werkzeug

### Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask App     │◄──►│   SQLite DB     │
│   (Frontend)    │    │   (Backend)     │    │   (Data Store)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Face Recognition│
                       │    Engine       │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Local File      │
                       │ Storage         │
                       └─────────────────┘
```

### Security Features
- **Password Hashing**: Werkzeug PBKDF2 hashing
- **Session Management**: Secure session handling
- **File Validation**: Image type and size validation
- **Face Validation**: Ensures uploaded images contain faces
- **SQL Injection Protection**: Parameterized queries
- **CSRF Protection**: Built-in Flask security
Testing
The application includes unit and integration tests to ensure functionality and reliability. To run the tests:

bash
Copy code
python -m unittest discover -s tests
Deployment
To deploy the ChildSafe application to a production environment, follow these steps:

Set up a production server (e.g., AWS, Heroku, DigitalOcean).
Install necessary dependencies on the server.
Clone the repository to the server.
Set up the environment variables for the database and other configurations.
Run the application in a production server environment (using a WSGI server like Gunicorn).
## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python -m pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions
- Keep functions small and focused

### Reporting Issues
- Use the GitHub issue tracker
- Provide detailed reproduction steps
- Include system information and error logs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact & Support

**Original Author**: Joseph Paul Onyango
- 📧 Email: mavinodundo@gmail.com
- 🐙 GitHub: [@Joe-Mavin](https://github.com/Joe-Mavin)

**Enhanced Version**: AI-Assisted Improvements
- 🆕 AWS-Free Implementation
- 🎨 Modern UI/UX
- 🔒 Enhanced Security

### Getting Help
- 📖 Check the [Wiki](https://github.com/Joe-Mavin/childSafe/wiki) for detailed documentation
- 🐛 Report bugs via [GitHub Issues](https://github.com/Joe-Mavin/childSafe/issues)
- 💬 Join our community discussions

---

**⭐ If this project helps you, please give it a star!**

**🚨 Important**: This application handles sensitive child information. Always ensure proper security measures are in place when deploying to production.
