# 🩺 Jaundice Recovery Tracker

A personal, full-featured web application built with **Flask + SQLite** to track and manage a jaundice (hepatitis) recovery journey. It centralises medical records, lab results, medications, daily journal entries, and uploaded reports into a single private dashboard.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started (Local)](#-getting-started-local)
- [Configuration](#-configuration)
- [Application Modules](#-application-modules)
- [Database Models](#-database-models)
- [Running Tests](#-running-tests)
- [Deploying to Production](#-deploying-to-production)
- [File Uploads](#-file-uploads)

---

## ✨ Features

| Module | What it does |
|--------|-------------|
| **Dashboard** | Overview of the full recovery — days since diagnosis, bilirubin trend chart, LFT chart, active medications, recent journal entries |
| **Timeline** | Chronological log of every treatment event (consultations, hospital visits, lab tests, ayurveda visits, milestones, etc.) with optional file attachments |
| **Lab Results** | Log and track all blood tests (Bilirubin, SGPT, SGOT, etc.) with values, units, normal ranges, status flags, and doctor notes. Includes a live chart API |
| **Medications** | Track active, completed, and discontinued medications with dosage, frequency, and prescribing doctor |
| **Reports** | Upload and manage medical documents (PDFs, images) organised by category — lab reports, prescriptions, consultation notes, ayurveda records |
| **Daily Journal** | Daily recovery log with energy level, appetite, sleep quality, mood (all on a 1–10 scale), symptoms, and recovery notes |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Flask 3.x |
| **Database** | SQLite via Flask-SQLAlchemy |
| **ORM** | SQLAlchemy 2.x |
| **Frontend** | Jinja2 templates, Vanilla CSS, Chart.js |
| **Production server** | Gunicorn |
| **Testing** | pytest, pytest-flask |

---

## 📁 Project Structure

```
illtracker/
│
├── app.py                  # App factory — creates Flask app, registers blueprints
├── config.py               # All configuration settings
├── requirements.txt        # Python dependencies
├── Procfile                # For Render/Heroku deployment
├── .gitignore
│
├── models/
│   ├── db.py               # SQLAlchemy models (TimelineEvent, LabResult, Medication, JournalEntry, Report)
│   └── schemas.py          # Constant lists (activity types, test names, statuses, etc.)
│
├── routes/
│   ├── dashboard.py        # GET /  — main dashboard
│   ├── timeline.py         # /timeline/  — CRUD for timeline events
│   ├── lab_results.py      # /lab-results/  — CRUD + chart API
│   ├── medications.py      # /medications/  — CRUD + status update
│   ├── reports.py          # /reports/  — file upload, download, preview, delete
│   └── journal.py          # /journal/  — daily journal (upsert by date)
│
├── templates/
│   ├── base.html           # Shared layout (navbar, flash messages, footer)
│   ├── dashboard.html
│   ├── timeline.html
│   ├── lab_results.html
│   ├── medications.html
│   ├── reports.html
│   └── journal.html
│
├── static/
│   ├── css/style.css       # Application styles
│   ├── js/charts.js        # Chart.js logic
│   └── uploads/            # Uploaded files land here (gitignored, .gitkeep preserved)
│
└── tests/
    ├── conftest.py         # Shared pytest fixtures (in-memory DB, test client)
    ├── test_dashboard.py
    ├── test_journal.py
    ├── test_lab_results.py
    ├── test_medications.py
    ├── test_timeline.py
    └── test_models.py
```

---

## 🚀 Getting Started (Local)

### Prerequisites
- Python 3.10+
- pip

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/illtracker.git
cd illtracker
```

### 2. Create & activate virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> If PowerShell blocks the activation script, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

The app will be available at **http://127.0.0.1:5000**

The SQLite database (`jaundice_tracker.db`) and the `static/uploads/` folder are created automatically on first run.

---

## ⚙️ Configuration

All settings live in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | fallback string | **Set via `SECRET_KEY` env var in production** |
| `DEBUG` | `False` | Set `FLASK_DEBUG=true` env var to enable |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///jaundice_tracker.db` | SQLite DB in project root |
| `UPLOAD_FOLDER` | `static/uploads/` | Where uploaded files are stored |
| `MAX_CONTENT_LENGTH` | `16 MB` | Max upload file size |
| `ALLOWED_EXTENSIONS` | `pdf, jpg, jpeg, png` | Accepted file types |
| `DIAGNOSIS_DATE` | `'2025-05-01'` | **Update this to your actual diagnosis date** |

### Updating your diagnosis date
Open `config.py` and change:
```python
DIAGNOSIS_DATE = '2025-05-01'   # → change to your actual date (YYYY-MM-DD)
```

---

## 📦 Application Modules

### Dashboard (`/`)
- Shows **days since diagnosis** counter
- Summary cards: total consultations, lab tests, active medications, reports, milestones
- **Bilirubin trend chart** — visualises total bilirubin decline over time
- **LFT trend** — SGPT and SGOT over time
- Recent timeline events (last 5) and journal entries (last 3)

### Timeline (`/timeline/`)
- Add events with a **date, activity type, title, description**, and optional file attachment
- Activity types: `Diagnosis`, `Hospital Visit`, `Lab Test`, `Consultation`, `Ayurveda Visit`, `Medication Purchase`, `Recovery Milestone`
- Filter by activity type
- Edit and delete events

### Lab Results (`/lab-results/`)
- Log test results with **test name, date, value, unit, normal range, status, doctor notes**
- Status options: `Normal`, `High`, `Low`, `Critical`
- Filter results by test name
- **Chart API** at `/lab-results/api/chart-data?test=<TestName>` — returns JSON for Chart.js

### Medications (`/medications/`)
- Track medications with **name, start/end date, dosage, frequency, instructions, prescribing doctor**
- Status: `Active`, `Completed`, `Discontinued`
- Quick status-update endpoint without editing the full record
- Filter by status; counts shown per status

### Reports (`/reports/`)
- Upload PDF or image medical documents
- Categories: `Laboratory Report`, `Prescription`, `Consultation Notes`, `Ayurveda Records`
- View files inline in the browser (PDFs open natively)
- Download files with original title as filename
- File size displayed in human-readable format (KB / MB)

### Journal (`/journal/`)
- One entry per day (enforced by a DB unique constraint on `entry_date`)
- Posting the same date **updates** the existing entry (upsert behaviour)
- Tracks: `symptoms`, `energy_level`, `appetite`, `sleep_quality`, `mood` (1–10), `observations`, `recovery_notes`

---

## 🗄 Database Models

All models live in `models/db.py` and use SQLite via SQLAlchemy.

```
TimelineEvent     → timeline_events
LabResult         → lab_results
Report            → reports
Medication        → medications
JournalEntry      → journal_entries   (unique constraint on entry_date)
```

Each model has a `to_dict()` method for JSON serialisation and `created_at` / `updated_at` timestamps.

---

## 🧪 Running Tests

The test suite uses an **in-memory SQLite database** — it never touches the real `jaundice_tracker.db`.

### Install test dependencies
```bash
pip install pytest pytest-flask
```

### Run all tests
```bash
python -m pytest tests/ -v
```

### Run a specific module
```bash
python -m pytest tests/test_journal.py -v
```

### Test coverage (73 tests total)

| Test file | What's covered |
|-----------|---------------|
| `test_dashboard.py` | Page load, empty-DB resilience |
| `test_journal.py` | CRUD, upsert, validation, 404 |
| `test_lab_results.py` | CRUD, filtering, chart API, validation, 404 |
| `test_medications.py` | CRUD, status updates, filtering, validation, 404 |
| `test_timeline.py` | CRUD, all activity types, file attachment, invalid file guard, filtering, 404 |
| `test_models.py` | Persistence, `to_dict()`, defaults, unique constraint |

---

## 🌐 Deploying to Production

### Recommended: [Render.com](https://render.com) (free tier available)

1. **Push your code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/illtracker.git
git push -u origin main
```

2. **On Render:**
   - New → Web Service → connect GitHub repo
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn "app:create_app()"`

3. **Set environment variables on Render:**
   ```
   SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
   FLASK_DEBUG=False
   ```

4. Your app will be live at `https://your-app-name.onrender.com`

> ⚠️ **Persistence warning:** Render's free tier has an ephemeral filesystem. Uploaded files and the SQLite DB may be wiped on redeploy. For long-term use, add a **Render Disk** (~$7/month) and point `UPLOAD_FOLDER` and `SQLALCHEMY_DATABASE_URI` to the mounted path.

---

## 📂 File Uploads

- Uploaded files are stored in `static/uploads/`
- Filenames are prefixed with a timestamp to avoid collisions: `20260615_185500_report.pdf`
- Only the filename is stored in the database (not the full path)
- Allowed types: **PDF, JPG, JPEG, PNG**
- Max size: **16 MB**
- The `static/uploads/` directory is **gitignored** — only the `.gitkeep` placeholder is tracked so the folder is created on fresh clones

---

## 📝 License

Personal use only. Built to support a private medical recovery journey.
