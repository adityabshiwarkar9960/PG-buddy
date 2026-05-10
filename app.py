from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "pgbuddy.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
MAX_IMAGE_SIZE_BYTES = 600 * 1024
MAX_IMAGE_COUNT = 4
MAX_COLLEGE_ID_IMAGE_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

DEFAULT_PGS = [
    {
        "name": "Sunrise PG",
        "area": "nagpur",
        "city": "nagpur",
        "rent": 6000,
        "facilities": "WiFi, Food, Laundry",
        "gender": "Female",
        "vacant_seats": 5,
        "warden_contact": "9999991111",
        "owner_contact": "9999992222",
    },
    {
        "name": "Student Home PG",
        "area": "nagpur",
        "city": "nagpur",
        "rent": 5000,
        "facilities": "WiFi, Study Room",
        "gender": "Female",
        "vacant_seats": 4,
        "warden_contact": "9999993333",
        "owner_contact": "9999994444",
    },
    {
        "name": "Green Valley PG",
        "area": "nagpur",
        "city": "nagpur",
        "rent": 6500,
        "facilities": "Food, Parking",
        "gender": "Male",
        "vacant_seats": 6,
        "warden_contact": "9999995555",
        "owner_contact": "9999996666",
    },
    {
        "name": "Sweet Home PG",
        "area": "nagpur",
        "city": "nagpur",
        "rent": 6000,
        "facilities": "WiFi, Food, Laundry",
        "gender": "Male",
        "vacant_seats": 5,
        "warden_contact": "9999997777",
        "owner_contact": "9999998888",
    },
    {
        "name": "Sai Krupa PG",
        "area": "nagpur",
        "city": "nagpur",
        "rent": 5000,
        "facilities": "WiFi, Study Room",
        "gender": "Female",
        "vacant_seats": 3,
        "warden_contact": "9888881111",
        "owner_contact": "9888882222",
    },
    {
        "name": "Veesh PG",
        "area": "nagpur",
        "city": "nagpur",
        "rent": 6500,
        "facilities": "Food, Parking",
        "gender": "Male",
        "vacant_seats": 7,
        "warden_contact": "9888883333",
        "owner_contact": "9888884444",
    },
    {
        "name": "Ramreet PG",
        "area": "pune",
        "city": "pune",
        "rent": 7500,
        "facilities": "WiFi, Food",
        "gender": "Female",
        "vacant_seats": 5,
        "warden_contact": "9777771111",
        "owner_contact": "9777772222",
    },
    {
        "name": "Elite Living PG",
        "area": "pune",
        "city": "pune",
        "rent": 8500,
        "facilities": "AC, WiFi, Laundry",
        "gender": "Female",
        "vacant_seats": 4,
        "warden_contact": "9777773333",
        "owner_contact": "9777774444",
    },
    {
        "name": "City View PG",
        "area": "pune",
        "city": "pune",
        "rent": 6800,
        "facilities": "Food, Study Room",
        "gender": "Male",
        "vacant_seats": 6,
        "warden_contact": "9666661111",
        "owner_contact": "9666662222",
    },
    {
        "name": "Sunrise PG Pune",
        "area": "pune",
        "city": "pune",
        "rent": 6000,
        "facilities": "WiFi, Food, Laundry",
        "gender": "Male",
        "vacant_seats": 5,
        "warden_contact": "9666663333",
        "owner_contact": "9666664444",
    },
    {
        "name": "Eligibal PG",
        "area": "pune",
        "city": "pune",
        "rent": 5000,
        "facilities": "WiFi, Study Room",
        "gender": "Female",
        "vacant_seats": 5,
        "warden_contact": "9555551111",
        "owner_contact": "9555552222",
    },
]

CITY_RESOURCES = [
    {"city": "Nagpur", "name": "Mess & Food"},
    {"city": "Nagpur", "name": "Laundry Service"},
    {"city": "Nagpur", "name": "Medical Store"},
    {"city": "Nagpur", "name": "Transport"},
    {"city": "Nagpur", "name": "Shops"},
    {"city": "Nagpur", "name": "Study Centers"},
    {"city": "Pune", "name": "Mess & Food"},
    {"city": "Pune", "name": "Library"},
    {"city": "Pune", "name": "Food Delivery"},
    {"city": "Pune", "name": "Gym"},
    {"city": "Pune", "name": "Transport"},
    {"city": "Pune", "name": "Shops"},
    {"city": "Pune", "name": "Study Centers"},
]

RESOURCE_TYPES = {
    "Mess & Food": {
        "icon": "🍽️",
        "description": "Affordable and convenient meal services near your PG.",
        "distance": "0.5-2 km",
    },
    "Laundry": {
        "icon": "🧺",
        "description": "Professional laundry and washing services for your clothes.",
        "distance": "0.3-1.5 km",
    },
    "Medical": {
        "icon": "🏥",
        "description": "Hospitals, clinics, pharmacies, and medical stores nearby.",
        "distance": "1-3 km",
    },
    "Shops": {
        "icon": "🛒",
        "description": "Daily necessity shops and grocery stores nearby.",
        "distance": "0.2-1 km",
    },
    "Transport": {
        "icon": "🚍",
        "description": "Bus stops, metro stations, and public transport options.",
        "distance": "0.5-2 km",
    },
    "Study Centers": {
        "icon": "📚",
        "description": "Libraries and study centers for academic support.",
        "distance": "0.5-2.5 km",
    },
    "Gym": {
        "icon": "🏋️",
        "description": "Fitness centers and gyms to support a healthy student routine.",
        "distance": "0.5-2 km",
    },
}

RESOURCE_PROVIDERS = {
    "Mess & Food": [
        {"name": "Campus Mess", "distance": "0.5 km", "address": "Near Gate 1", "number": "9876543210"},
        {"name": "Food Express Delivery", "distance": "1 km", "address": "Main Road", "number": "9876543211"},
        {"name": "Healthy Bites", "distance": "1.5 km", "address": "Market Street", "number": "9876543212"},
    ],
    "Laundry": [
        {"name": "Quick Wash Laundry", "distance": "0.3 km", "address": "Behind PG", "number": "9876543213"},
        {"name": "Fresh & Clean", "distance": "0.8 km", "address": "Market Area", "number": "9876543214"},
        {"name": "Express Laundry", "distance": "1.5 km", "address": "Main Road", "number": "9876543215"},
    ],
    "Medical": [
        {"name": "City Hospital", "distance": "1.2 km", "address": "Highway Road", "number": "9876543216"},
        {"name": "MediCare Clinic", "distance": "1.8 km", "address": "Downtown", "number": "9876543217"},
        {"name": "24/7 Pharmacy", "distance": "2.5 km", "address": "Shopping Center", "number": "9876543218"},
    ],
    "Shops": [
        {"name": "General Store", "distance": "0.2 km", "address": "Next to PG", "number": "9876543219"},
        {"name": "Supermarket Plus", "distance": "0.7 km", "address": "Market Street", "number": "9876543220"},
        {"name": "Daily Essentials", "distance": "1 km", "address": "Main Bazar", "number": "9876543221"},
    ],
    "Transport": [
        {"name": "Bus Stop A", "distance": "0.5 km", "address": "Main Gate", "number": "9876543222"},
        {"name": "Auto Stand", "distance": "0.8 km", "address": "Market Area", "number": "9876543223"},
        {"name": "Metro Station", "distance": "2 km", "address": "City Center", "number": "9876543224"},
    ],
    "Study Centers": [
        {"name": "City Library", "distance": "0.5 km", "address": "Downtown", "number": "9876543225"},
        {"name": "Tech Academy", "distance": "1.2 km", "address": "Education Complex", "number": "9876543226"},
        {"name": "Study Hub", "distance": "1.8 km", "address": "Market Street", "number": "9876543227"},
    ],
    "Gym": [
        {"name": "FitZone Gym", "distance": "0.6 km", "address": "College Road", "number": "9876543228"},
        {"name": "PowerHouse Fitness", "distance": "1.1 km", "address": "Main Square", "number": "9876543229"},
        {"name": "Active Life Gym", "distance": "1.9 km", "address": "City Center", "number": "9876543230"},
    ],
}

RESOURCE_PROVIDERS_BY_CITY = {
    "Nagpur": {
        "Mess & Food": [
            {"name": "Nandan Mess", "distance": "0.4 km", "address": "Dharampeth", "number": "9890001101"},
            {"name": "Student Tiffin Corner", "distance": "0.9 km", "address": "Sitabuldi", "number": "9890001102"},
            {"name": "Home Meal Box", "distance": "1.4 km", "address": "Laxmi Nagar", "number": "9890001103"},
        ],
        "Laundry": [
            {"name": "Sparkle Laundry", "distance": "0.3 km", "address": "Near College Square", "number": "9890001104"},
            {"name": "Wash Buddy", "distance": "0.8 km", "address": "Ramdaspeth", "number": "9890001105"},
            {"name": "Quick Press", "distance": "1.2 km", "address": "Shankar Nagar", "number": "9890001106"},
        ],
        "Medical": [
            {"name": "Orange City Clinic", "distance": "1.1 km", "address": "Civil Lines", "number": "9890001107"},
            {"name": "CarePlus Pharmacy", "distance": "1.7 km", "address": "Wardhaman Nagar", "number": "9890001108"},
            {"name": "Metro MultiCare", "distance": "2.4 km", "address": "Medical Square", "number": "9890001109"},
        ],
        "Shops": [
            {"name": "Daily Basket", "distance": "0.2 km", "address": "Near PG Lane", "number": "9890001110"},
            {"name": "Smart Mart", "distance": "0.7 km", "address": "Dharampeth", "number": "9890001111"},
            {"name": "City Needs", "distance": "1.1 km", "address": "Gokulpeth", "number": "9890001112"},
        ],
        "Transport": [
            {"name": "Laxmi Nagar Bus Stop", "distance": "0.5 km", "address": "Ring Road", "number": "9890001113"},
            {"name": "Auto Point", "distance": "0.9 km", "address": "College Chowk", "number": "9890001114"},
            {"name": "Subhan Nagar Metro Link", "distance": "1.8 km", "address": "Main Corridor", "number": "9890001115"},
        ],
        "Study Centers": [
            {"name": "Nagpur Reading Hall", "distance": "0.6 km", "address": "Ramdaspeth", "number": "9890001116"},
            {"name": "Aspire Study Zone", "distance": "1.3 km", "address": "Bajaj Nagar", "number": "9890001117"},
            {"name": "Focused Library", "distance": "1.9 km", "address": "Pratap Nagar", "number": "9890001118"},
        ],
    },
    "Pune": {
        "Mess & Food": [
            {"name": "FC Road Mess", "distance": "0.5 km", "address": "Fergusson College Road", "number": "9890001201"},
            {"name": "Pune Tiffin Works", "distance": "1 km", "address": "Shivajinagar", "number": "9890001202"},
            {"name": "NutriMeal Hub", "distance": "1.6 km", "address": "Deccan", "number": "9890001203"},
        ],
        "Gym": [
            {"name": "Urban Lift Gym", "distance": "0.6 km", "address": "Karve Nagar", "number": "9890001204"},
            {"name": "Core Fitness Studio", "distance": "1.2 km", "address": "Kothrud", "number": "9890001205"},
            {"name": "Pulse Strength Club", "distance": "1.9 km", "address": "Aundh", "number": "9890001206"},
        ],
        "Shops": [
            {"name": "Quick Pick Store", "distance": "0.3 km", "address": "JM Road", "number": "9890001207"},
            {"name": "Pune Fresh Mart", "distance": "0.8 km", "address": "Baner", "number": "9890001208"},
            {"name": "Essentials Point", "distance": "1.1 km", "address": "Wakad", "number": "9890001209"},
        ],
        "Transport": [
            {"name": "PMC Bus Hub", "distance": "0.6 km", "address": "Shivajinagar", "number": "9890001210"},
            {"name": "Metro Entry Gate", "distance": "1.1 km", "address": "Civil Court", "number": "9890001211"},
            {"name": "Shared Cab Point", "distance": "1.7 km", "address": "Hinjewadi Connector", "number": "9890001212"},
        ],
        "Study Centers": [
            {"name": "Pune Central Library", "distance": "0.7 km", "address": "Model Colony", "number": "9890001213"},
            {"name": "Exam Prep Studio", "distance": "1.4 km", "address": "Koregaon Park", "number": "9890001214"},
            {"name": "Night Study Cafe", "distance": "2 km", "address": "Viman Nagar", "number": "9890001215"},
        ],
    },
}

STUDENT_HELP_SERVICES = {
    "Complaints": {
        "icon": "📝",
        "title": "Complaints & Feedback",
        "subtitle": "Raise Issues and Share Feedback",
        "description": "Raise complaints and share feedback to improve the student experience.",
        "benefits": [
            "Easy complaint registration",
            "Quick issue resolution",
            "Transparent complaint tracking",
            "Feedback for improvement",
            "Student support team",
            "Regular follow-ups",
        ],
        "cta": "Raise a Complaint",
        "cta_link": "/complaints",
    },
    "Emergency": {
        "icon": "🚨",
        "title": "Emergency Services",
        "subtitle": "24/7 Emergency Support",
        "description": "Access emergency support and nearby medical help when you need it most.",
        "benefits": [
            "24/7 emergency support",
            "Quick response time",
            "Medical emergency contacts",
            "Safety assistance",
            "Student helpline",
            "Crisis support",
        ],
        "cta": "Access Emergency Services",
        "cta_link": "/emergency",
    },
    "Affordable": {
        "icon": "💰",
        "title": "Affordable PGs",
        "subtitle": "Budget-Friendly Accommodation",
        "description": "Find verified, budget-friendly PGs with transparent pricing.",
        "benefits": [
            "Verified pricing with no hidden charges",
            "Compare PGs by budget",
            "Flexible payment options",
            "Transparent rent details",
            "Best value for money",
            "Student-friendly plans",
        ],
        "cta": "Explore Affordable PGs",
        "cta_link": "/affordable",
    },
    "Safe": {
        "icon": "🛡️",
        "title": "Safe & Secure",
        "subtitle": "Verified & Secure Accommodations",
        "description": "Live in verified and secure PGs with safety-first infrastructure.",
        "benefits": [
            "Verified owners and properties",
            "CCTV surveillance",
            "Secure entry systems",
            "Safe localities",
            "Routine safety checks",
            "Emergency contacts",
        ],
        "cta": "View Safe PGs",
        "cta_link": "/safe-secure",
    },
    "Nearby": {
        "icon": "📍",
        "title": "Nearby Essentials",
        "subtitle": "Essential Services Near Your PG",
        "description": "Find all daily essentials close to your enrolled PG location.",
        "benefits": [
            "Mess and food options",
            "Laundry nearby",
            "Medical stores",
            "Libraries and study centers",
            "Public transport access",
            "Grocery and daily needs",
        ],
        "cta": "View Resources",
        "cta_link": "/resources",
    },
    "Communication": {
        "icon": "📞",
        "title": "Easy Communication",
        "subtitle": "Direct Contact with PG Owners",
        "description": "Communicate directly with PG owners with no middlemen.",
        "benefits": [
            "Direct owner contact",
            "No broker dependency",
            "Faster responses",
            "Transparent discussions",
            "Clear expectations",
            "Trust-based communication",
        ],
        "cta": "Contact PG Owners",
        "cta_link": "/easy-communication",
    },
}

HOSPITALS_BY_CITY = {
    "Nagpur": [
        {
            "name": "Max Super Specialty Hospital",
            "distance": "1.5 km",
            "address": "Medical City, Nagpur",
            "phone": "0712-4111111",
            "services": "Emergency, ICU, Trauma Center, Surgery",
        },
        {
            "name": "Vedanta Hospital",
            "distance": "2 km",
            "address": "New Nagpur",
            "phone": "0712-3200100",
            "services": "General Medicine, Surgery, Pediatrics, Cardiology",
        },
        {
            "name": "Dhanvantari Hospital",
            "distance": "1.2 km",
            "address": "Ramdaspeth",
            "phone": "0712-6151515",
            "services": "24/7 Emergency, Orthopedics, General Ward",
        },
        {
            "name": "Apollo Hospitals",
            "distance": "2.5 km",
            "address": "South Nagpur",
            "phone": "0712-2500500",
            "services": "Multi-specialty, Trauma, Neurology, Oncology",
        },
    ],
    "Pune": [
        {
            "name": "Ruby Hall Clinic",
            "distance": "1.8 km",
            "address": "Pune Central",
            "phone": "020-66455555",
            "services": "Emergency, ICU, Trauma Center, Surgery",
        },
        {
            "name": "Apollo Hospitals Pune",
            "distance": "2.2 km",
            "address": "Bannerghatta Road",
            "phone": "020-26611111",
            "services": "Multi-specialty, Emergency, Cardiology",
        },
        {
            "name": "Sahyadri Hospital",
            "distance": "2.5 km",
            "address": "Karve Road",
            "phone": "020-41222222",
            "services": "Critical Care, Neurology, ICU",
        },
        {
            "name": "Dinanath Hospital",
            "distance": "1.6 km",
            "address": "Near Station",
            "phone": "020-24441111",
            "services": "General Hospital, Emergency, OPD Services",
        },
    ],
}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("PG_BUDDY_SECRET", "pgbuddy-dev-secret")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


@app.template_filter("inr")
def inr_filter(value: Any) -> str:
    try:
        amount = int(value)
    except (TypeError, ValueError):
        amount = 0
    return f"₹{amount:,}"


def utc_now_str() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_error: BaseException | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def ensure_enrollment_security_columns(db: sqlite3.Connection) -> None:
    columns = {row["name"] for row in db.execute("PRAGMA table_info(enrollments)").fetchall()}

    if "college_id" not in columns:
        db.execute("ALTER TABLE enrollments ADD COLUMN college_id TEXT NOT NULL DEFAULT ''")
    if "college_id_image" not in columns:
        db.execute("ALTER TABLE enrollments ADD COLUMN college_id_image TEXT NOT NULL DEFAULT ''")


def ensure_complaints_columns(db: sqlite3.Connection) -> None:
    columns = {row["name"] for row in db.execute("PRAGMA table_info(complaints)").fetchall()}

    if "pg_id" not in columns:
        db.execute("ALTER TABLE complaints ADD COLUMN pg_id INTEGER")
    if "status" not in columns:
        db.execute("ALTER TABLE complaints ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'")
    if "owner_note" not in columns:
        db.execute("ALTER TABLE complaints ADD COLUMN owner_note TEXT NOT NULL DEFAULT ''")
    if "updated_at" not in columns:
        db.execute("ALTER TABLE complaints ADD COLUMN updated_at TEXT NOT NULL DEFAULT ''")


def init_db() -> None:
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('Student', 'Owner')),
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            gender TEXT,
            extra TEXT,
            contact TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pgs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            name TEXT NOT NULL,
            area TEXT NOT NULL,
            city TEXT NOT NULL,
            rent INTEGER NOT NULL,
            facilities TEXT,
            gender TEXT NOT NULL,
            vacant_seats INTEGER NOT NULL DEFAULT 0,
            warden_contact TEXT,
            owner_contact TEXT,
            lat REAL,
            lng REAL,
            image_urls TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pg_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            college TEXT NOT NULL,
            college_id TEXT NOT NULL,
            college_id_image TEXT NOT NULL,
            address TEXT NOT NULL,
            parents_name TEXT NOT NULL,
            parents_contact TEXT NOT NULL,
            nearby_hospital_name TEXT DEFAULT '',
            nearby_hospital_contact TEXT DEFAULT '',
            enrolled_at TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (pg_id) REFERENCES pgs(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS owner_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL,
            owner_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            sent_at TEXT NOT NULL,
            FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pg_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            pg_name TEXT,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            owner_note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (pg_id) REFERENCES pgs(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        """
    )
    ensure_enrollment_security_columns(db)
    ensure_complaints_columns(db)
    db.execute("UPDATE complaints SET updated_at = created_at WHERE updated_at = '' OR updated_at IS NULL")
    db.execute("UPDATE complaints SET status = 'Pending' WHERE status = '' OR status IS NULL")
    db.commit()


def seed_default_pgs() -> None:
    db = get_db()
    count_row = db.execute("SELECT COUNT(*) AS count FROM pgs").fetchone()
    if count_row and count_row["count"] > 0:
        return

    now = utc_now_str()
    for pg in DEFAULT_PGS:
        db.execute(
            """
            INSERT INTO pgs (
                owner_id, name, area, city, rent, facilities, gender, vacant_seats,
                warden_contact, owner_contact, lat, lng, image_urls, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                None,
                pg["name"],
                pg["area"],
                pg["city"],
                pg["rent"],
                pg.get("facilities", ""),
                pg["gender"],
                pg.get("vacant_seats", 0),
                pg.get("warden_contact", ""),
                pg.get("owner_contact", ""),
                None,
                None,
                json.dumps([]),
                now,
                now,
            ),
        )
    db.commit()


def validate_student_profile_form() -> tuple[dict[str, str] | None, str | None]:
    name = request.form.get("studentName", "").strip()
    contact = request.form.get("contact", "").strip()
    gender = request.form.get("gender", "").strip()
    college = request.form.get("college", "").strip()

    if not all([name, contact, gender, college]):
        return None, "Please fill all required profile fields."

    if not is_digits_10(contact):
        return None, "Contact number must be exactly 10 digits."

    allowed_genders = {"Male", "Female", "Prefer not to say"}
    if gender not in allowed_genders:
        return None, "Please select a valid gender option."

    return {
        "name": name,
        "contact": contact,
        "gender": gender,
        "extra": college,
    }, None


def validate_owner_profile_form() -> tuple[dict[str, str] | None, str | None]:
    name = request.form.get("ownerName", "").strip()
    contact = request.form.get("contact", "").strip()

    if not all([name, contact]):
        return None, "Please fill all required profile fields."

    if not is_digits_10(contact):
        return None, "Contact number must be exactly 10 digits."

    return {
        "name": name,
        "contact": contact,
    }, None


def parse_image_urls(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    result: list[str] = []
    for item in parsed:
        value = str(item).strip()
        if value and value not in result:
            result.append(value)
    return result[:MAX_IMAGE_COUNT]


def normalize_resource_name(name: str) -> str:
    lower = name.lower()
    if any(token in lower for token in ["mess", "food", "delivery"]):
        return "Mess & Food"
    if any(token in lower for token in ["laundry", "washing"]):
        return "Laundry"
    if any(token in lower for token in ["medical", "clinic", "hospital", "pharmacy", "store"]):
        return "Medical"
    if any(token in lower for token in ["shop", "grocery", "market"]):
        return "Shops"
    if any(token in lower for token in ["transport", "bus", "metro", "auto"]):
        return "Transport"
    if any(token in lower for token in ["library", "study", "center", "tutor"]):
        return "Study Centers"
    if any(token in lower for token in ["gym", "fitness", "workout"]):
        return "Gym"
    return name


def resolve_city_key(city: str, city_map: dict[str, Any]) -> str | None:
    wanted = (city or "").strip().lower()
    if not wanted:
        return None
    for known_city in city_map:
        if known_city.lower() == wanted:
            return known_city
    return None


def get_resource_providers(city: str, resource_type: str) -> tuple[list[dict[str, str]], str]:
    city_key = resolve_city_key(city, RESOURCE_PROVIDERS_BY_CITY)
    if city_key:
        providers = RESOURCE_PROVIDERS_BY_CITY.get(city_key, {}).get(resource_type)
        if providers:
            return providers, city_key

    return RESOURCE_PROVIDERS.get(resource_type, []), (city or "Nearby Area")


def parse_int(value: str, *, min_value: int | None = None) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    if min_value is not None and parsed < min_value:
        return None
    return parsed


def parse_lat_lng(value: str, *, minimum: float, maximum: float) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed < minimum or parsed > maximum:
        return None
    return parsed


def is_digits_10(value: str) -> bool:
    return len(value) == 10 and value.isdigit()


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_images(files: list[Any]) -> list[str]:
    saved: list[str] = []
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    for upload in files:
        if not upload or not getattr(upload, "filename", ""):
            continue
        if len(saved) >= MAX_IMAGE_COUNT:
            break

        filename = secure_filename(upload.filename)
        if not filename or not allowed_file(filename):
            raise ValueError("Only png, jpg, jpeg, gif, and webp files are supported.")

        stream = upload.stream
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0)
        if size > MAX_IMAGE_SIZE_BYTES:
            raise ValueError("Each image must be 600 KB or smaller.")

        unique_name = f"{uuid.uuid4().hex}_{filename}"
        save_path = UPLOAD_FOLDER / unique_name
        upload.save(save_path)
        saved.append(f"uploads/{unique_name}")

    return saved


def save_uploaded_image(upload: Any, *, max_size_bytes: int) -> str:
    if not upload or not getattr(upload, "filename", ""):
        raise ValueError("Please upload a college ID image.")

    filename = secure_filename(upload.filename)
    if not filename or not allowed_file(filename):
        raise ValueError("College ID image must be png, jpg, jpeg, gif, or webp.")

    stream = upload.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    if size > max_size_bytes:
        raise ValueError("College ID image must be 2 MB or smaller.")

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = UPLOAD_FOLDER / unique_name
    upload.save(save_path)
    return f"uploads/{unique_name}"


def current_user() -> sqlite3.Row | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please login first.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(role: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.user is None:
                flash("Please login first.", "error")
                return redirect(url_for("login"))
            if g.user["role"] != role:
                flash("You are not allowed to access this page.", "error")
                return redirect(url_for("profile"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def pg_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["image_urls"] = parse_image_urls(data.get("image_urls"))
    return data


def get_active_enrollment_for_student(student_id: int) -> sqlite3.Row | None:
    db = get_db()
    return db.execute(
        """
        SELECT
            e.*, p.id AS pg_id, p.name AS pg_name, p.city AS pg_city, p.area AS pg_area,
            p.rent AS pg_rent, p.gender AS pg_gender, p.vacant_seats AS pg_vacant_seats,
            p.warden_contact AS pg_warden_contact, p.owner_contact AS pg_owner_contact,
            p.lat AS pg_lat, p.lng AS pg_lng, p.image_urls AS pg_image_urls,
            COALESCE(o.name, '') AS owner_name, COALESCE(o.email, '') AS owner_email
        FROM enrollments e
        JOIN pgs p ON p.id = e.pg_id
        LEFT JOIN users o ON o.id = p.owner_id
        WHERE e.student_id = ? AND e.active = 1
        ORDER BY e.id DESC
        LIMIT 1
        """,
        (student_id,),
    ).fetchone()


def get_owner_pgs_with_students(owner_id: int) -> list[dict[str, Any]]:
    db = get_db()
    pg_rows = db.execute(
        "SELECT * FROM pgs WHERE owner_id = ? ORDER BY updated_at DESC, id DESC",
        (owner_id,),
    ).fetchall()

    result: list[dict[str, Any]] = []
    for row in pg_rows:
        pg = pg_row_to_dict(row)
        enrollment_rows = db.execute(
            """
            SELECT *
            FROM enrollments
            WHERE pg_id = ? AND active = 1
            ORDER BY id DESC
            """,
            (pg["id"],),
        ).fetchall()

        enrolled_students: list[dict[str, Any]] = []
        for enrollment in enrollment_rows:
            enrollment_dict = dict(enrollment)
            message_rows = db.execute(
                "SELECT id, text, sent_at FROM owner_messages WHERE enrollment_id = ? ORDER BY id DESC",
                (enrollment["id"],),
            ).fetchall()
            enrollment_dict["owner_messages"] = [dict(item) for item in message_rows]
            enrolled_students.append(enrollment_dict)

        pg["enrolled_students"] = enrolled_students
        result.append(pg)

    return result


def mask_student_name(name: str) -> str:
    cleaned = (name or "").strip()
    if not cleaned:
        return "Anonymous Student"
    if len(cleaned) == 1:
        return "*"
    return cleaned[0] + ("*" * (len(cleaned) - 1))


def get_owner_complaint_notifications(owner_id: int) -> list[dict[str, Any]]:
    db = get_db()
    rows = db.execute(
        """
        SELECT
            c.id,
            c.user_id,
            c.pg_id,
            c.name,
            c.pg_name,
            c.type,
            c.message,
            c.status,
            c.owner_note,
            c.created_at,
            c.updated_at,
            COALESCE(
                (
                    SELECT p.name
                    FROM pgs p
                    WHERE p.id = c.pg_id AND p.owner_id = ?
                    LIMIT 1
                ),
                (
                    SELECT p.name
                    FROM pgs p
                    WHERE p.owner_id = ?
                      AND c.pg_name IS NOT NULL
                      AND lower(trim(p.name)) = lower(trim(c.pg_name))
                    LIMIT 1
                ),
                c.pg_name,
                'Unknown PG'
            ) AS owner_pg_name
        FROM complaints c
                WHERE lower(c.type) IN ('complaint', 'feedback')
          AND (
                EXISTS (
                    SELECT 1
                    FROM pgs p
                    WHERE p.id = c.pg_id AND p.owner_id = ?
                )
                OR EXISTS (
                    SELECT 1
                    FROM pgs p
                    WHERE p.owner_id = ?
                      AND c.pg_name IS NOT NULL
                      AND lower(trim(p.name)) = lower(trim(c.pg_name))
                )
            )
        ORDER BY c.id DESC
        LIMIT 50
        """,
        (owner_id, owner_id, owner_id, owner_id),
    ).fetchall()

    notifications: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["student_name_masked"] = mask_student_name(item.get("name", ""))
        notifications.append(item)

    return notifications


def validate_pg_form(existing_images: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    name = request.form.get("pgName", "").strip()
    area = request.form.get("pgArea", "").strip()
    rent_raw = request.form.get("pgRent", "").strip()
    city = request.form.get("pgCity", "").strip()
    gender = request.form.get("pgGender", "").strip()
    facilities = request.form.get("pgFacilities", "").strip()
    vacant_raw = request.form.get("pgVacantSeats", "").strip()
    warden_contact = request.form.get("pgWardenContact", "").strip()
    owner_contact = request.form.get("pgOwnerContact", "").strip()
    lat_raw = request.form.get("pgLat", "").strip()
    lng_raw = request.form.get("pgLng", "").strip()

    if not all([name, area, rent_raw, city, gender, vacant_raw, warden_contact, owner_contact]):
        return None, "Please fill all required PG fields."

    if gender not in {"Male", "Female"}:
        return None, "PG type must be Male or Female."

    rent = parse_int(rent_raw, min_value=1)
    vacant_seats = parse_int(vacant_raw, min_value=0)
    if rent is None:
        return None, "Monthly rent must be a positive number."
    if vacant_seats is None:
        return None, "Vacant seats must be zero or more."

    if not is_digits_10(warden_contact):
        return None, "Warden contact must be 10 digits."
    if not is_digits_10(owner_contact):
        return None, "Owner contact must be 10 digits."

    lat = parse_lat_lng(lat_raw, minimum=-90, maximum=90)
    lng = parse_lat_lng(lng_raw, minimum=-180, maximum=180)
    if lat_raw and lat is None:
        return None, "Latitude must be between -90 and 90."
    if lng_raw and lng is None:
        return None, "Longitude must be between -180 and 180."

    uploaded_files = request.files.getlist("pgImages")
    has_new_uploads = any(file and file.filename for file in uploaded_files)

    try:
        image_urls = save_uploaded_images(uploaded_files) if has_new_uploads else existing_images
    except ValueError as error:
        return None, str(error)

    image_urls = image_urls[:MAX_IMAGE_COUNT]

    return {
        "name": name,
        "area": area,
        "city": city,
        "rent": rent,
        "facilities": facilities,
        "gender": gender,
        "vacant_seats": vacant_seats,
        "warden_contact": warden_contact,
        "owner_contact": owner_contact,
        "lat": lat,
        "lng": lng,
        "image_urls": image_urls,
    }, None


@app.before_request
def load_user() -> None:
    g.user = current_user()


@app.route("/")
@app.route("/index")
@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/login")
@app.route("/login.html")
def login():
    if g.user:
        return redirect(url_for("profile"))
    return render_template("login.html")


@app.post("/auth/register")
def auth_register():
    role = request.form.get("role", "").strip().title()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    gender = request.form.get("gender", "").strip()
    extra = request.form.get("extra", "").strip()
    contact = request.form.get("contact", "").strip()

    if role not in {"Student", "Owner"}:
        flash("Select a valid role.", "error")
        return redirect(url_for("login"))

    if not all([name, email, password, gender, contact]):
        flash("Please fill all required registration fields.", "error")
        return redirect(url_for("login"))

    if "@" not in email:
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("login"))

    if len(password) < 6:
        flash("Password must be at least 6 characters.", "error")
        return redirect(url_for("login"))

    if not is_digits_10(contact):
        flash("Contact number must be exactly 10 digits.", "error")
        return redirect(url_for("login"))

    if role == "Student" and not extra:
        flash("College name is required for students.", "error")
        return redirect(url_for("login"))

    if role == "Owner" and not extra:
        extra = "PG Owner"

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        flash("Email is already registered. Please login instead.", "error")
        return redirect(url_for("login"))

    db.execute(
        """
        INSERT INTO users (role, name, email, password_hash, gender, extra, contact, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (role, name, email, generate_password_hash(password), gender, extra, contact, utc_now_str()),
    )
    db.commit()

    flash(f"{role} account created successfully. Please login.", "success")
    return redirect(url_for("login"))


@app.post("/auth/login")
def auth_login():
    role = request.form.get("role", "").strip().title()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if role not in {"Student", "Owner"}:
        flash("Select a valid login role.", "error")
        return redirect(url_for("login"))

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    if user["role"] != role:
        flash(f"This account is registered as {user['role']}.", "error")
        return redirect(url_for("login"))

    session.clear()
    session["user_id"] = user["id"]

    if role == "Owner":
        return redirect(url_for("owner_dashboard"))
    return redirect(url_for("profile"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/profile")
@app.route("/profile.html")
@login_required
def profile():
    if g.user["role"] == "Owner":
        return redirect(url_for("owner_dashboard"))

    enrollment = get_active_enrollment_for_student(g.user["id"])
    enrollment_dict: dict[str, Any] | None = None
    owner_messages: list[dict[str, Any]] = []

    if enrollment is not None:
        enrollment_dict = dict(enrollment)
        enrollment_dict["pg_image_urls"] = parse_image_urls(enrollment_dict.get("pg_image_urls"))
        messages = get_db().execute(
            "SELECT id, text, sent_at FROM owner_messages WHERE enrollment_id = ? ORDER BY id DESC",
            (enrollment["id"],),
        ).fetchall()
        owner_messages = [dict(message) for message in messages]

    return render_template(
        "profile.html",
        user=g.user,
        enrollment=enrollment_dict,
        owner_messages=owner_messages,
    )

@app.post("/student/profile/update")
@login_required
@role_required("Student")
def update_student_profile():
    profile_data, error = validate_student_profile_form() # type: ignore
    if error:
        flash(error, "error")
        return redirect(url_for("profile", edit="1"))
    if profile_data is None:
        flash("Unable to update profile. Please try again.", "error")
        return redirect(url_for("profile", edit="1"))

    db = get_db()
    db.execute(
        """
        UPDATE users
        SET name = ?, contact = ?, gender = ?, extra = ?
        WHERE id = ? AND role = 'Student'
        """,
        (
            profile_data["name"],
            profile_data["contact"],
            profile_data["gender"],
            profile_data["extra"],
            g.user["id"],
        ),
    )
    db.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile", saved="1"))


@app.post("/enrollment/<int:enrollment_id>/exit")
@login_required
@role_required("Student")
def exit_enrollment(enrollment_id: int):
    db = get_db()
    enrollment = db.execute(
        "SELECT * FROM enrollments WHERE id = ? AND student_id = ? AND active = 1",
        (enrollment_id, g.user["id"]),
    ).fetchone()

    if enrollment is None:
        flash("Enrollment not found.", "error")
        return redirect(url_for("profile"))

    db.execute("UPDATE enrollments SET active = 0 WHERE id = ?", (enrollment_id,))
    db.execute("UPDATE pgs SET vacant_seats = vacant_seats + 1, updated_at = ? WHERE id = ?", (utc_now_str(), enrollment["pg_id"]))
    db.commit()
    flash("You have exited the PG enrollment.", "success")
    return redirect(url_for("profile"))


@app.route("/home")
@app.route("/home.html")
def home():
    query = request.args.get("q", "").strip().lower()
    pgs: list[dict[str, Any]] = []

    if query:
        db = get_db()
        conditions = ["(lower(p.area) LIKE ? OR lower(p.city) LIKE ?)"]
        like_value = f"%{query}%"
        params: list[Any] = [like_value, like_value]

        if g.user and g.user["role"] == "Student":
            student_gender = (g.user["gender"] or "").strip().lower()
            if student_gender in {"male", "female"}:
                conditions.append("lower(p.gender) = ?")
                params.append(student_gender)

        where_sql = f"WHERE {' AND '.join(conditions)}"

        rows = db.execute(
            f"""
            SELECT p.*, COALESCE(u.name, '') AS owner_name, COALESCE(u.email, '') AS owner_email
            FROM pgs p
            LEFT JOIN users u ON u.id = p.owner_id
            {where_sql}
            ORDER BY p.updated_at DESC, p.id DESC
            """,
            params,
        ).fetchall()
        pgs = [pg_row_to_dict(row) for row in rows]

    return render_template(
        "home.html",
        query=query,
        pgs=pgs,
    )


@app.route("/pg/<int:pg_id>", methods=["GET", "POST"])
@login_required
def pg_details(pg_id: int):
    db = get_db()
    pg_row = db.execute(
        """
        SELECT p.*, COALESCE(u.name, '') AS owner_name, COALESCE(u.email, '') AS owner_email
        FROM pgs p
        LEFT JOIN users u ON u.id = p.owner_id
        WHERE p.id = ?
        """,
        (pg_id,),
    ).fetchone()

    if pg_row is None:
        abort(404)

    pg = pg_row_to_dict(pg_row)

    if request.method == "POST":
        if g.user["role"] != "Student":
            flash("Only students can enroll in PGs.", "error")
            return redirect(url_for("pg_details", pg_id=pg_id))

        student_name = request.form.get("studentName", "").strip()
        contact = request.form.get("contact", "").strip()
        email = request.form.get("email", "").strip().lower()
        college = request.form.get("college", "").strip()
        college_id = request.form.get("collegeId", "").strip()
        address = request.form.get("address", "").strip()
        parents_name = request.form.get("parentsName", "").strip()
        parents_contact = request.form.get("parentsContact", "").strip()
        college_id_image_upload = request.files.get("collegeIdImage")

        if not all([student_name, contact, email, college, college_id, address, parents_name, parents_contact]):
            flash("Please fill all enrollment fields, including college ID.", "error")
            return redirect(url_for("pg_details", pg_id=pg_id))

        if not college_id_image_upload or not college_id_image_upload.filename:
            flash("Please upload your college ID image for security verification.", "error")
            return redirect(url_for("pg_details", pg_id=pg_id))

        if not is_digits_10(contact) or not is_digits_10(parents_contact):
            flash("Contact numbers must be 10 digits.", "error")
            return redirect(url_for("pg_details", pg_id=pg_id))

        current = get_active_enrollment_for_student(g.user["id"])
        if current is not None and current["pg_id"] == pg_id:
            flash("You are already enrolled in this PG.", "error")
            return redirect(url_for("pg_details", pg_id=pg_id))

        if current is not None and current["pg_id"] != pg_id:
            db.execute("UPDATE enrollments SET active = 0 WHERE id = ?", (current["id"],))
            db.execute(
                "UPDATE pgs SET vacant_seats = vacant_seats + 1, updated_at = ? WHERE id = ?",
                (utc_now_str(), current["pg_id"]),
            )

        if pg["vacant_seats"] <= 0:
            db.rollback()
            flash("No vacant seats are available right now.", "error")
            return redirect(url_for("pg_details", pg_id=pg_id))

        try:
            college_id_image = save_uploaded_image(
                college_id_image_upload,
                max_size_bytes=MAX_COLLEGE_ID_IMAGE_SIZE_BYTES,
            )
        except ValueError as error:
            db.rollback()
            flash(str(error), "error")
            return redirect(url_for("pg_details", pg_id=pg_id))

        db.execute(
            """
            INSERT INTO enrollments (
                pg_id, student_id, student_name, contact, email, college, college_id,
                college_id_image, address, parents_name, parents_contact, enrolled_at, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                pg_id,
                g.user["id"],
                student_name,
                contact,
                email,
                college,
                college_id,
                college_id_image,
                address,
                parents_name,
                parents_contact,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        db.execute(
            "UPDATE pgs SET vacant_seats = vacant_seats - 1, updated_at = ? WHERE id = ?",
            (utc_now_str(), pg_id),
        )
        db.commit()

        flash(f"Successfully enrolled in {pg['name']}.", "success")
        return redirect(url_for("profile"))

    return render_template("pg_details.html", pg=pg)


@app.route("/pg-details.html")
@login_required
def pg_details_legacy():
    pg_id = request.args.get("pg_id", type=int)
    if not pg_id:
        flash("Please pick a PG first.", "error")
        return redirect(url_for("home"))
    return redirect(url_for("pg_details", pg_id=pg_id))


@app.route("/owner-dashboard")
@app.route("/owner-dashboard.html")
@login_required
@role_required("Owner")
def owner_dashboard():
    db = get_db()
    edit_pg_id = request.args.get("edit_pg_id", type=int)
    edit_pg = None

    if edit_pg_id:
        row = db.execute("SELECT * FROM pgs WHERE id = ? AND owner_id = ?", (edit_pg_id, g.user["id"])).fetchone()
        if row:
            edit_pg = pg_row_to_dict(row)

    owner_pgs = get_owner_pgs_with_students(g.user["id"])
    complaint_notifications = get_owner_complaint_notifications(g.user["id"])
    notification_badge_count = sum(
        1
        for item in complaint_notifications
        if (item.get("type") or "").strip().lower() == "complaint"
        and (item.get("status") or "").strip().lower() != "resolved"
    )
    return render_template(
        "owner_dashboard.html",
        owner=g.user,
        owner_pgs=owner_pgs,
        edit_pg=edit_pg,
        complaint_notifications=complaint_notifications,
        notification_badge_count=notification_badge_count,
    )

@app.post("/owner/profile/update")
@login_required
@role_required("Owner")
def update_owner_profile():
    profile_data, error = validate_owner_profile_form() # type: ignore
    if error:
        flash(error, "error")
        return redirect(url_for("owner_dashboard"))
    if profile_data is None:
        flash("Unable to update profile. Please try again.", "error")
        return redirect(url_for("owner_dashboard"))

    db = get_db()
    db.execute(
        """
        UPDATE users
        SET name = ?, contact = ?
        WHERE id = ? AND role = 'Owner'
        """,
        (profile_data["name"], profile_data["contact"], g.user["id"]),
    )
    db.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.post("/owner/pg/create")
@login_required
@role_required("Owner")
def owner_create_pg():
    existing_images = parse_image_urls(request.form.get("existingImageUrls"))
    pg_data, error = validate_pg_form(existing_images)
    if error:
        flash(error, "error")
        return redirect(url_for("owner_dashboard"))
    if pg_data is None:
        flash("Unable to process PG details. Please try again.", "error")
        return redirect(url_for("owner_dashboard"))

    db = get_db()
    now = utc_now_str()
    db.execute(
        """
        INSERT INTO pgs (
            owner_id, name, area, city, rent, facilities, gender, vacant_seats,
            warden_contact, owner_contact, lat, lng, image_urls, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            g.user["id"],
            pg_data["name"],
            pg_data["area"],
            pg_data["city"],
            pg_data["rent"],
            pg_data["facilities"],
            pg_data["gender"],
            pg_data["vacant_seats"],
            pg_data["warden_contact"],
            pg_data["owner_contact"],
            pg_data["lat"],
            pg_data["lng"],
            json.dumps(pg_data["image_urls"]),
            now,
            now,
        ),
    )
    db.commit()
    flash("PG added successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.post("/owner/pg/<int:pg_id>/update")
@login_required
@role_required("Owner")
def owner_update_pg(pg_id: int):
    db = get_db()
    row = db.execute("SELECT * FROM pgs WHERE id = ? AND owner_id = ?", (pg_id, g.user["id"])).fetchone()
    if row is None:
        flash("PG not found.", "error")
        return redirect(url_for("owner_dashboard"))

    existing_images = parse_image_urls(request.form.get("existingImageUrls"))
    if not existing_images:
        existing_images = parse_image_urls(row["image_urls"])

    pg_data, error = validate_pg_form(existing_images)
    if error:
        flash(error, "error")
        return redirect(url_for("owner_dashboard", edit_pg_id=pg_id))
    if pg_data is None:
        flash("Unable to process PG details. Please try again.", "error")
        return redirect(url_for("owner_dashboard", edit_pg_id=pg_id))

    db.execute(
        """
        UPDATE pgs
        SET
            name = ?, area = ?, city = ?, rent = ?, facilities = ?, gender = ?,
            vacant_seats = ?, warden_contact = ?, owner_contact = ?, lat = ?, lng = ?,
            image_urls = ?, updated_at = ?
        WHERE id = ? AND owner_id = ?
        """,
        (
            pg_data["name"],
            pg_data["area"],
            pg_data["city"],
            pg_data["rent"],
            pg_data["facilities"],
            pg_data["gender"],
            pg_data["vacant_seats"],
            pg_data["warden_contact"],
            pg_data["owner_contact"],
            pg_data["lat"],
            pg_data["lng"],
            json.dumps(pg_data["image_urls"]),
            utc_now_str(),
            pg_id,
            g.user["id"],
        ),
    )
    db.commit()
    flash("PG updated successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.post("/owner/pg/<int:pg_id>/delete")
@login_required
@role_required("Owner")
def owner_delete_pg(pg_id: int):
    db = get_db()
    pg_row = db.execute("SELECT id FROM pgs WHERE id = ? AND owner_id = ?", (pg_id, g.user["id"])).fetchone()
    if pg_row is None:
        flash("PG not found.", "error")
        return redirect(url_for("owner_dashboard"))

    active_enrollment = db.execute(
        "SELECT COUNT(*) AS count FROM enrollments WHERE pg_id = ? AND active = 1",
        (pg_id,),
    ).fetchone()
    if active_enrollment and active_enrollment["count"] > 0:
        flash("Cannot delete PG while students are enrolled. Remove students first.", "error")
        return redirect(url_for("owner_dashboard"))

    db.execute("DELETE FROM pgs WHERE id = ? AND owner_id = ?", (pg_id, g.user["id"]))
    db.commit()
    flash("PG deleted successfully.", "success")
    return redirect(url_for("owner_dashboard"))


@app.post("/owner/enrollment/<int:enrollment_id>/remove")
@login_required
@role_required("Owner")
def owner_remove_student(enrollment_id: int):
    db = get_db()
    row = db.execute(
        """
        SELECT e.id, e.pg_id
        FROM enrollments e
        JOIN pgs p ON p.id = e.pg_id
        WHERE e.id = ? AND e.active = 1 AND p.owner_id = ?
        """,
        (enrollment_id, g.user["id"]),
    ).fetchone()

    if row is None:
        flash("Student enrollment not found.", "error")
        return redirect(url_for("owner_dashboard"))

    db.execute("UPDATE enrollments SET active = 0 WHERE id = ?", (enrollment_id,))
    db.execute("UPDATE pgs SET vacant_seats = vacant_seats + 1, updated_at = ? WHERE id = ?", (utc_now_str(), row["pg_id"]))
    db.commit()

    flash("Student removed from PG enrollment.", "success")
    return redirect(url_for("owner_dashboard"))


@app.post("/owner/enrollment/<int:enrollment_id>/message")
@login_required
@role_required("Owner")
def owner_send_message(enrollment_id: int):
    message_text = request.form.get("message", "").strip()
    if not message_text:
        flash("Please type a message first.", "error")
        return redirect(url_for("owner_dashboard"))

    if len(message_text) > 500:
        flash("Message must be 500 characters or fewer.", "error")
        return redirect(url_for("owner_dashboard"))

    db = get_db()
    ownership = db.execute(
        """
        SELECT e.id
        FROM enrollments e
        JOIN pgs p ON p.id = e.pg_id
        WHERE e.id = ? AND e.active = 1 AND p.owner_id = ?
        """,
        (enrollment_id, g.user["id"]),
    ).fetchone()

    if ownership is None:
        flash("Enrollment not found.", "error")
        return redirect(url_for("owner_dashboard"))

    db.execute(
        "INSERT INTO owner_messages (enrollment_id, owner_id, text, sent_at) VALUES (?, ?, ?, ?)",
        (enrollment_id, g.user["id"], message_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.commit()

    flash("Message sent to student.", "success")
    return redirect(url_for("owner_dashboard"))


def find_enrollment_for_student_and_pg(student_id: int, pg_id: int | None) -> sqlite3.Row | None:
    db = get_db()
    if pg_id is not None:
        active = db.execute(
            """
            SELECT id
            FROM enrollments
            WHERE student_id = ? AND pg_id = ? AND active = 1
            ORDER BY id DESC
            LIMIT 1
            """,
            (student_id, pg_id),
        ).fetchone()
        if active is not None:
            return active

        latest = db.execute(
            """
            SELECT id
            FROM enrollments
            WHERE student_id = ? AND pg_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (student_id, pg_id),
        ).fetchone()
        if latest is not None:
            return latest

    return db.execute(
        """
        SELECT id
        FROM enrollments
        WHERE student_id = ?
        ORDER BY active DESC, id DESC
        LIMIT 1
        """,
        (student_id,),
    ).fetchone()


@app.post("/owner/complaint/<int:complaint_id>/status")
@login_required
@role_required("Owner")
def owner_update_complaint_status(complaint_id: int):
    status = request.form.get("status", "").strip()
    owner_note = request.form.get("owner_note", "").strip()
    if status not in {"Pending", "In Progress", "Resolved"}:
        flash("Invalid complaint status.", "error")
        return redirect(url_for("owner_dashboard"))

    db = get_db()
    complaint = db.execute(
        """
        SELECT c.*
        FROM complaints c
        WHERE c.id = ?
          AND lower(c.type) = 'complaint'
          AND (
                EXISTS (
                    SELECT 1
                    FROM pgs p
                    WHERE p.id = c.pg_id AND p.owner_id = ?
                )
                OR EXISTS (
                    SELECT 1
                    FROM pgs p
                    WHERE p.owner_id = ?
                      AND c.pg_name IS NOT NULL
                      AND lower(trim(p.name)) = lower(trim(c.pg_name))
                )
            )
        LIMIT 1
        """,
        (complaint_id, g.user["id"], g.user["id"]),
    ).fetchone()

    if complaint is None:
        flash("Complaint not found.", "error")
        return redirect(url_for("owner_dashboard"))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "UPDATE complaints SET status = ?, owner_note = ?, updated_at = ? WHERE id = ?",
        (status, owner_note, now, complaint_id),
    )

    student_id = complaint["user_id"]
    if student_id is not None:
        enrollment = find_enrollment_for_student_and_pg(student_id, complaint["pg_id"])
        if enrollment is not None:
            msg = f"Complaint update for {complaint['pg_name'] or 'your PG'}: status is now {status}."
            if owner_note:
                msg = f"{msg} Note: {owner_note}"
            db.execute(
                "INSERT INTO owner_messages (enrollment_id, owner_id, text, sent_at) VALUES (?, ?, ?, ?)",
                (enrollment["id"], g.user["id"], msg, now),
            )

    db.commit()
    flash("Complaint status updated and student notified.", "success")
    return redirect(url_for("owner_dashboard"))


@app.route("/complaints", methods=["GET", "POST"])
@app.route("/complaints.html", methods=["GET", "POST"])
def complaints():
    enrolled_pg = None
    if g.user and g.user["role"] == "Student":
        enrollment = get_active_enrollment_for_student(g.user["id"])
        if enrollment is not None:
            enrolled_pg = {
                "id": enrollment["pg_id"],
                "name": enrollment["pg_name"],
            }

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pg_name = request.form.get("pg", "").strip()
        pg_id = parse_int(request.form.get("pg_id", "").strip(), min_value=1)
        complaint_type = request.form.get("type", "Complaint").strip()
        message = request.form.get("message", "").strip()

        if g.user:
            name = name or (g.user["name"] or "")
            email = email or (g.user["email"] or "")

        if not name or not email or not message:
            flash("Name, email, and message are required.", "error")
            return redirect(url_for("complaints"))

        if complaint_type not in {"Complaint", "Feedback"}:
            complaint_type = "Complaint"

        if g.user and g.user["role"] == "Student":
            if enrolled_pg is None:
                flash("Please enroll in a PG first before submitting a complaint.", "error")
                return redirect(url_for("complaints"))
            pg_id = int(enrolled_pg["id"])
            pg_name = str(enrolled_pg["name"])

        if complaint_type == "Complaint" and not pg_name:
            flash("Please include PG name for this complaint.", "error")
            return redirect(url_for("complaints"))

        db = get_db()
        user_id = g.user["id"] if g.user else None
        db.execute(
            """
            INSERT INTO complaints (
                user_id, pg_id, name, email, pg_name, type, message, status, owner_note, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                pg_id,
                name,
                email,
                pg_name,
                complaint_type,
                message,
                "Pending",
                "",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        db.commit()

        flash("Your complaint/feedback has been submitted.", "success")
        return redirect(url_for("complaints"))

    return render_template("complaints.html", enrolled_pg=enrolled_pg)


@app.route("/resources")
@app.route("/resources.html")
def resources():
    resource_types: list[str] = []
    enrolled_pg = None

    if g.user and g.user["role"] == "Student":
        enrollment = get_active_enrollment_for_student(g.user["id"])
        if enrollment is not None:
            enrolled_pg = dict(enrollment)
            city = (enrollment["pg_city"] or "").strip().lower()
            found_types: list[str] = []
            for item in CITY_RESOURCES:
                if item["city"].lower() != city:
                    continue
                normalized = normalize_resource_name(item["name"])
                if normalized not in found_types:
                    found_types.append(normalized)
            resource_types = found_types

    return render_template("resources.html", resource_types=resource_types, enrolled_pg=enrolled_pg)


@app.route("/resource-details")
@app.route("/resource-details.html")
@login_required
@role_required("Student")
def resource_details():
    resource_type = request.args.get("type", "").strip()
    config = RESOURCE_TYPES.get(resource_type)
    if config is None:
        flash("Resource type not found.", "error")
        return redirect(url_for("resources"))

    enrollment = get_active_enrollment_for_student(g.user["id"])
    if enrollment is None:
        flash("Please enroll in a PG first to view resource details.", "error")
        return redirect(url_for("resources"))

    providers, providers_city = get_resource_providers(enrollment["pg_city"], resource_type)
    return render_template(
        "resource_details.html",
        resource_type=resource_type,
        config=config,
        providers=providers,
        providers_city=providers_city,
        enrolled_pg=dict(enrollment),
    )


@app.route("/student-friendly")
@app.route("/student-friendly.html")
def student_friendly():
    return render_template("student_friendly.html")


@app.route("/student-help-details")
@app.route("/student-help-details.html")
def student_help_details():
    service = request.args.get("service", "").strip()
    config = STUDENT_HELP_SERVICES.get(service)
    if config is None:
        flash("Service not found.", "error")
        return redirect(url_for("student_friendly"))
    return render_template("student_help_details.html", service=service, config=config)


@app.route("/emergency")
@app.route("/emergency.html")
def emergency():
    enrolled_pg = None
    if g.user and g.user["role"] == "Student":
        enrollment = get_active_enrollment_for_student(g.user["id"])
        if enrollment is not None:
            enrolled_pg = dict(enrollment)
    return render_template("emergency.html", enrolled_pg=enrolled_pg)


@app.route("/hospital-details")
@app.route("/hospital-details.html")
@login_required
@role_required("Student")
def hospital_details():
    enrollment = get_active_enrollment_for_student(g.user["id"])
    if enrollment is None:
        flash("Please enroll in a PG first.", "error")
        return redirect(url_for("emergency"))

    city = (enrollment["pg_city"] or "").strip()
    city_key = ""
    for known_city in HOSPITALS_BY_CITY:
        if known_city.lower() == city.lower():
            city_key = known_city
            break
    hospitals = HOSPITALS_BY_CITY.get(city_key, [])

    return render_template(
        "hospital_details.html",
        enrolled_pg=dict(enrollment),
        hospitals=hospitals,
    )


@app.route("/hospital-info")
@app.route("/hospital-info.html")
@login_required
@role_required("Student")
def hospital_info():
    name = request.args.get("name", "").strip()
    distance = request.args.get("distance", "").strip()
    address = request.args.get("address", "").strip()
    phone = request.args.get("phone", "").strip()
    services = request.args.get("services", "").strip()

    if not name:
        flash("Hospital information not found.", "error")
        return redirect(url_for("hospital_details"))

    enrollment = get_active_enrollment_for_student(g.user["id"])
    enrolled_pg = dict(enrollment) if enrollment else None

    if enrollment is not None and phone:
        db = get_db()
        db.execute(
            "UPDATE enrollments SET nearby_hospital_name = ?, nearby_hospital_contact = ? WHERE id = ?",
            (name, phone, enrollment["id"]),
        )
        db.commit()
        enrollment = get_active_enrollment_for_student(g.user["id"])
        enrolled_pg = dict(enrollment) if enrollment else None

    service_list = [item.strip() for item in services.split(",") if item.strip()]

    return render_template(
        "hospital_info.html",
        hospital={
            "name": name,
            "distance": distance,
            "address": address,
            "phone": phone,
            "services": service_list,
        },
        enrolled_pg=enrolled_pg,
    )


@app.route("/affordable")
@app.route("/affordable.html")
def affordable():
    return render_template(
        "simple_feature.html",
        page_title="Affordable PGs",
        hero_title="💰 Affordable PGs",
        hero_subtitle="Budget-friendly PG options specially curated for students",
        cards=[
            {"title": "Verified Pricing", "text": "No hidden charges. Transparent rent details."},
            {"title": "Student Budget Focused", "text": "PGs suitable for students and freshers."},
            {"title": "Flexible Rent Options", "text": "Monthly and shared-room options available."},
        ],
    )


@app.route("/safe-secure")
@app.route("/safe-secure.html")
def safe_secure():
    return render_template(
        "simple_feature.html",
        page_title="Safe & Secure",
        hero_title="🛡️ Safe & Secure",
        hero_subtitle="Your safety is our top priority",
        cards=[
            {"title": "Verified PG Owners", "text": "All PG owners are identity verified."},
            {"title": "CCTV Surveillance", "text": "PGs with CCTV cameras and monitoring."},
            {"title": "Safe Localities", "text": "PGs located in student-friendly areas."},
        ],
    )


@app.route("/nearby-essentials")
@app.route("/nearby-essentials.html")
def nearby_essentials():
    return render_template(
        "simple_feature.html",
        page_title="Nearby Essentials",
        hero_title="📍 Nearby Essentials",
        hero_subtitle="Everything you need, just minutes away",
        cards=[
            {"title": "Mess & Cafes", "text": "Affordable food options near PGs."},
            {"title": "Medical Stores", "text": "24/7 pharmacies and clinics nearby."},
            {"title": "Transport Access", "text": "Bus stops, metro and auto stands nearby."},
        ],
    )


@app.route("/easy-communication")
@app.route("/easy-communication.html")
def easy_communication():
    return render_template(
        "simple_feature.html",
        page_title="Easy Communication",
        hero_title="📞 Easy Communication",
        hero_subtitle="Direct and transparent communication",
        cards=[
            {"title": "Direct Owner Contact", "text": "No brokers or middlemen involved."},
            {"title": "Quick Response", "text": "Fast replies to student queries."},
            {"title": "Verified Contact Info", "text": "Trusted and verified phone numbers."},
        ],
    )


@app.route("/reset-local-data")
@app.route("/reset-local-data.html")
def reset_local_data():
    return render_template("reset_local_data.html")


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


def bootstrap() -> None:
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        init_db()
        seed_default_pgs()


bootstrap()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
