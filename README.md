





























# PG Buddy (Python Version)

This folder contains a full Python conversion of the original PG Buddy web project.

- Framework: Flask
- Database: SQLite (pgbuddy.db)
- Auth: Session-based login with hashed passwords
- Storage: Database-backed users, PGs, enrollments, owner messages, complaints
- Assets: CSS and image assets copied into static/ 

## What Was Converted

The Python app includes all major modules from the original project in backend form:

1. Student and owner registration/login
2. Profile page with enrolled PG and owner messages
3. Owner dashboard with:
   - Add/update/delete PG
   - Upload up to 4 images
   - Geolocation selection on map
   - Enrolled student list
   - Owner-to-student messaging
   - Remove student from enrollment
4. PG search and details pages
5. Enrollment flow with seat count updates
6. Complaints and feedback form
7. Student resources and resource details
8. Student help details pages
9. Emergency + nearby hospitals + hospital details
10. Static support pages (affordable, safe-secure, nearby-essentials, easy-communication)

Legacy route aliases are supported, including:

- /index.html, /login.html, /home.html, /profile.html
- /owner-dashboard.html, /resources.html, /resource-details.html
- /student-friendly.html, /student-help-details.html
- /emergency.html, /hospital-details.html, /hospital-info.html
- /complaints.html, /affordable.html, /safe-secure.html
- /nearby-essentials.html, /easy-communication.html, /reset-local-data.html

## Run Locally

1. Open terminal in pgbuddy_python_app
2. Create virtual environment (recommended):

powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1


3. Install dependencies:

powershell
pip install -r requirements.txt


4. Start app:

powershell
python app.py


5. Open browser:

text
http://127.0.0.1:5000


## Notes

1. Default PG listings are auto-seeded on first run.
2. Uploaded images are saved in static/uploads/.
3. To reset all app data, stop server and delete pgbuddy.db.
#




fix the formate for git readme

🏠 PG Buddy (Python Version)
A full Python + Flask conversion of the original PG Buddy web project designed to help students find and manage PG accommodations easily.

🚀 Tech Stack
Backend: Python + Flask

Database: SQLite (pgbuddy.db)

Authentication: Session-based login with hashed passwords

Frontend Assets: HTML, CSS, JavaScript, Images

Storage: Database-backed system for users, PGs, enrollments, complaints, and messages

✨ Features
👨‍🎓 Student Features
Student Registration & Login

Search PGs

View PG Details

Enroll in PGs

Profile Dashboard

View Owner Messages

Complaints & Feedback System

Student Resources Section

Emergency & Hospital Information

🏠 Owner Features
Owner Registration & Login

Owner Dashboard

Add / Update / Delete PGs

Upload up to 4 PG Images

Map-based Geolocation Selection

View Enrolled Students

Send Messages to Students

Remove Student Enrollments

📂 Project Structure
pgbuddy_python_app/
│
├── static/
│   ├── css/
│   ├── images/
│   └── uploads/
│
├── templates/
│
├── pgbuddy.db
├── app.py
├── requirements.txt
└── README.md
🔄 Converted Modules
The Python version includes backend support for all major modules from the original project:

Student & Owner Authentication

Student Profile Management

Owner Dashboard Management

PG Search & Details

Enrollment System

Complaints & Feedback

Student Resources

Student Help Pages

Emergency & Hospital Information

Static Support Pages

🔗 Legacy Route Support
Legacy HTML routes are also supported for compatibility:

/index.html
/login.html
/home.html
/profile.html
/owner-dashboard.html
/resources.html
/resource-details.html
/student-friendly.html
/student-help-details.html
/emergency.html
/hospital-details.html
/hospital-info.html
/complaints.html
/affordable.html
/safe-secure.html
/nearby-essentials.html
/easy-communication.html
/reset-local-data.html
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone <your-repository-url>
cd pgbuddy_python_app
2️⃣ Create Virtual Environment
Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Run the Application
python app.py
5️⃣ Open in Browser
http://127.0.0.1:5000
📸 Key Functionalities
🔐 Secure Authentication System

🗺️ Location-Based PG Selection

🖼️ Multi-Image Upload Support

📩 Student ↔ Owner Messaging

🛏️ Seat Availability Management

🏥 Emergency & Nearby Hospital Information

📚 Student Resource Portal

🗄️ Database Information
SQLite database file:

pgbuddy.db
Tables include:

Users

PG Listings

Enrollments

Complaints

Messages

Resources

📝 Important Notes
Default PG listings are automatically seeded on first run.

Uploaded images are stored in:

static/uploads/
To completely reset the application data:

Stop the Flask server

Delete:

pgbuddy.db
🔒 Authentication
Passwords are securely hashed before storage.

Flask sessions are used for login authentication.

🌟 Future Improvements
Payment Integration

Chat System

Email Notifications

Advanced Search Filters

Admin Panel

PG Ratings & Reviews

👨‍💻 Developed With
Python

Flask

SQLite

HTML

CSS

JavaScript

📄 License
This project is for educational and learning purposes.


in single file

# 🏠 PG Buddy (Python Version)

A full Python + Flask conversion of the original **PG Buddy** web project designed to help students find and manage PG accommodations easily.

---

## 🚀 Tech Stack

- **Backend:** Python + Flask
- **Database:** SQLite (`pgbuddy.db`)
- **Authentication:** Session-based login with hashed passwords
- **Frontend Assets:** HTML, CSS, JavaScript, Images
- **Storage:** Database-backed system for users, PGs, enrollments, complaints, and messages

---

# ✨ Features

## 👨‍🎓 Student Features

- Student Registration & Login
- Search PGs
- View PG Details
- Enroll in PGs
- Profile Dashboard
- View Owner Messages
- Complaints & Feedback System
- Student Resources Section
- Emergency & Hospital Information

## 🏠 Owner Features

- Owner Registration & Login
- Owner Dashboard
- Add / Update / Delete PGs
- Upload up to 4 PG Images
- Map-based Geolocation Selection
- View Enrolled Students
- Send Messages to Students
- Remove Student Enrollments

---

# 📂 Project Structure

```text
pgbuddy_python_app/
│
├── static/
│   ├── css/
│   ├── images/
│   └── uploads/
│
├── templates/
│
├── pgbuddy.db
├── app.py
├── requirements.txt
└── README.md
```

---

# 🔄 Converted Modules

The Python version includes backend support for all major modules from the original project:

1. Student & Owner Authentication
2. Student Profile Management
3. Owner Dashboard Management
4. PG Search & Details
5. Enrollment System
6. Complaints & Feedback
7. Student Resources
8. Student Help Pages
9. Emergency & Hospital Information
10. Static Support Pages

---

# 🔗 Legacy Route Support

```text
/index.html
/login.html
/home.html
/profile.html
/owner-dashboard.html
/resources.html
/resource-details.html
/student-friendly.html
/student-help-details.html
/emergency.html
/hospital-details.html
/hospital-info.html
/complaints.html
/affordable.html
/safe-secure.html
/nearby-essentials.html
/easy-communication.html
/reset-local-data.html
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone <your-repository-url>
cd pgbuddy_python_app
```

## 2️⃣ Create Virtual Environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Run the Application

```bash
python app.py
```

## 5️⃣ Open in Browser

```text
http://127.0.0.1:5000
```

---

# 📸 Key Functionalities

- 🔐 Secure Authentication System
- 🗺️ Location-Based PG Selection
- 🖼️ Multi-Image Upload Support
- 📩 Student ↔ Owner Messaging
- 🛏️ Seat Availability Management
- 🏥 Emergency & Nearby Hospital Information
- 📚 Student Resource Portal

---

# 🗄️ Database Information

SQLite database file:

```text
pgbuddy.db
```

Tables include:

- Users
- PG Listings
- Enrollments
- Complaints
- Messages
- Resources

---

# 📝 Important Notes

1. Default PG listings are automatically seeded on first run.
2. Uploaded images are stored in:

```text
static/uploads/
```

3. To completely reset the application data:

- Stop the Flask server
- Delete:

```text
pgbuddy.db
```

---

# 🔒 Authentication

- Passwords are securely hashed before storage.
- Flask sessions are used for login authentication.

---

# 🌟 Future Improvements

- Payment Integration
- Chat System
- Email Notifications
- Advanced Search Filters
- Admin Panel
- PG Ratings & Reviews

---

# 👨‍💻 Developed With

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

---

# 📄 License

This project is for educational and learning purposes.

