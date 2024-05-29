ChildSafe: Child Registration and Identification System
Table of Contents
Introduction
Features
Installation
Usage
System Design
Testing
Deployment
Contributing
License
Contact
Introduction
ChildSafe is a web-based application designed to help reunite lost children with their families. The system allows for the registration of children at an early age, storing their photos and essential details. If a child goes missing, a person who finds them can upload a photo to the platform, which will then use facial recognition technology to match the photo with registered profiles and retrieve contact information for the child's guardians.

Features
Child Registration: Register a child by uploading a photo and entering essential details.
Facial Recognition: Match uploaded photos of found children with registered profiles.
User Roles: Different dashboards for regular users and admin users.
Regular Users: Register and update child information, search for lost children.
Admin Users: Manage users, update and delete child records.
Secure Login: Authentication using email and password.
Responsive Design: Accessible on both desktop and mobile devices.
Installation
To install and run the ChildSafe application on your local machine, follow these steps:

Prerequisites
Python 3.x
pip (Python package installer)
virtualenv (for creating virtual environments)
Steps
Clone the repository:

bash
Copy code
git clone https://github.com/Joe-Mavin/childSafe.git
cd childsafe
Create a virtual environment and activate it:

bash
Copy code
virtualenv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the database:

Ensure you have SQLite installed or configure your preferred database in app.py.
Run the database migration scripts if any (not covered here).
Run the application:

bash
Copy code
python app.py
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
System Design
The system design follows a client-server architecture:

Frontend: HTML, CSS, JavaScript
Backend: Flask (Python)
Database: SQLite (can be replaced with any SQL-based DB)
Facial Recognition: amazon rekognition API
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
Contributing
Contributions are welcome! Please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature/YourFeature).
Commit your changes (git commit -am 'Add YourFeature').
Push to the branch (git push origin feature/YourFeature).
Create a new Pull Request.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
Author: Joseph Paul Onyango
Email: mavinodundo@gmail.com
GitHub: https://github.com/Joe-Mavin
