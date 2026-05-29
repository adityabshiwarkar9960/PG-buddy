

# PG Buddy 

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
