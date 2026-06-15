# AGENT.md — AI Agent Guide for Jaundice Recovery Tracker

This file is written for AI coding agents. It describes the project architecture,
conventions, data flow, and patterns needed to work on this codebase confidently
without reading every file first.

---

## Project Identity

- **Name:** Jaundice Recovery Tracker (`illtracker`)
- **Type:** Personal single-user Flask web application
- **Purpose:** Track and manage a hepatitis/jaundice recovery — lab tests, medications, timeline events, daily journal, uploaded reports
- **Stack:** Python 3.12 · Flask 3.x · SQLite · Flask-SQLAlchemy · Jinja2 · Vanilla CSS · Chart.js
- **Entry point:** `app.py` → `create_app()` factory function
- **Local dev URL:** `http://127.0.0.1:5000`
- **DB file:** `jaundice_tracker.db` (SQLite, auto-created on first run)

---

## Directory Map (what lives where)

```
illtracker/
├── app.py              ← Flask app factory; registers all blueprints
├── config.py           ← All config (SECRET_KEY, DB URI, UPLOAD_FOLDER, DIAGNOSIS_DATE)
├── requirements.txt    ← Flask, Flask-SQLAlchemy, Werkzeug, gunicorn
├── Procfile            ← gunicorn start command for Render/Heroku
├── .gitignore
├── README.md
├── AGENT.md            ← this file
│
├── models/
│   ├── db.py           ← ALL SQLAlchemy models + init_db()
│   └── schemas.py      ← Constant lists used across routes (activity types, test names, statuses)
│
├── routes/             ← One Blueprint file per feature
│   ├── dashboard.py    ← GET /
│   ├── timeline.py     ← /timeline/
│   ├── lab_results.py  ← /lab-results/
│   ├── medications.py  ← /medications/
│   ├── reports.py      ← /reports/
│   └── journal.py      ← /journal/
│
├── templates/          ← Jinja2 HTML; one file per route + base.html
│   ├── base.html       ← Shared layout: navbar, flash messages, footer
│   └── *.html
│
├── static/
│   ├── css/style.css
│   ├── js/charts.js
│   └── uploads/        ← User-uploaded files land here (gitignored)
│
└── tests/
    ├── conftest.py     ← In-memory SQLite fixtures; never touches real DB
    ├── test_models.py
    ├── test_dashboard.py
    ├── test_journal.py
    ├── test_lab_results.py
    ├── test_medications.py
    └── test_timeline.py
```

---

## App Factory Pattern

```python
# app.py
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db(app)                        # db.init_app(app) + db.create_all()
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(lab_results_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(medications_bp)
    app.register_blueprint(journal_bp)
    return app
```

**To add a new blueprint:** create `routes/myfeature.py`, define `myfeature_bp`, import it in `app.py`, call `app.register_blueprint(myfeature_bp)`.

---

## Database Models (models/db.py)

All models share these patterns:
- `id` — Integer primary key (auto-increment)
- `created_at` / `updated_at` — auto-set `DateTime` columns
- `to_dict()` — returns a plain Python dict for JSON serialisation

### Model Reference

| Class | Table | Key Fields | Notes |
|-------|-------|-----------|-------|
| `TimelineEvent` | `timeline_events` | `event_date`, `activity_type`, `title`, `description`, `attachment_path` | `activity_type` is a free string validated against `ACTIVITY_TYPES` in schemas |
| `LabResult` | `lab_results` | `test_name`, `test_date`, `result_value`, `result_unit`, `normal_range`, `status` | `status` ∈ {normal, high, low, critical} |
| `Report` | `reports` | `title`, `category`, `report_date`, `file_path`, `file_type`, `file_size` | `file_path` stores only filename, not full path |
| `Medication` | `medications` | `medicine_name`, `start_date`, `end_date`, `dosage`, `frequency`, `status` | `status` default=`'active'`; ∈ {active, completed, discontinued} |
| `JournalEntry` | `journal_entries` | `entry_date` (unique), `energy_level`, `appetite`, `sleep_quality`, `mood` (all 1–10 int), `symptoms`, `observations`, `recovery_notes` | **`entry_date` has a UNIQUE constraint** — upsert logic is in the route |

### Adding a new model
1. Define the class in `models/db.py` inheriting from `db.Model`
2. Add a `to_dict()` method
3. `db.create_all()` is called on startup, so the table will be created automatically on next run

---

## Route Blueprints — URL & Method Map

### Dashboard — `routes/dashboard.py`
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Main dashboard; queries all models for summary data + chart data |

### Timeline — `routes/timeline.py` · prefix `/timeline`
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/timeline/` | List all events; `?type=<activity_type>` to filter |
| POST | `/timeline/add` | Create event; supports multipart (optional file attachment) |
| POST | `/timeline/edit/<id>` | Update event; may replace attachment |
| POST | `/timeline/delete/<id>` | Delete event + physical attachment file |

### Lab Results — `routes/lab_results.py` · prefix `/lab-results`
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/lab-results/` | List; `?test=<name>` to filter |
| POST | `/lab-results/add` | Create result |
| POST | `/lab-results/edit/<id>` | Update result |
| POST | `/lab-results/delete/<id>` | Delete result |
| GET | `/lab-results/api/chart-data` | JSON API; `?test=<name>`; returns `{labels, values, test_name}` |

### Medications — `routes/medications.py` · prefix `/medications`
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/medications/` | List; `?status=<status>` to filter |
| POST | `/medications/add` | Create medication |
| POST | `/medications/edit/<id>` | Update medication |
| POST | `/medications/delete/<id>` | Delete medication |
| POST | `/medications/update-status/<id>` | Quick status change (form field: `status`) |

### Reports — `routes/reports.py` · prefix `/reports`
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/reports/` | List; `?category=<cat>` to filter |
| POST | `/reports/upload` | Upload file (multipart); field name: `report_file` |
| GET | `/reports/download/<id>` | Download file as attachment |
| GET | `/reports/view/<id>` | Serve file inline (PDF preview) |
| POST | `/reports/delete/<id>` | Delete record + physical file |

### Journal — `routes/journal.py` · prefix `/journal`
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/journal/` | List all entries |
| POST | `/journal/add` | Upsert entry by `entry_date`; updates if date exists, inserts if new |
| POST | `/journal/delete/<id>` | Delete entry |

---

## Key Conventions

### Flash messages
All routes use `flash('message', 'success' | 'error')` and redirect. The base template renders flashes. Tests assert on flash text in the redirected HTML.

### Form validation pattern
```python
if not required_field:
    flash('Error message', 'error')
    return redirect(url_for('blueprint.index'))
```

### File uploads pattern
```python
filename = secure_filename(file.filename)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
filename = timestamp + filename          # collision-safe
file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
# Only filename (not full path) is stored in DB
```

### Allowed file types check
```python
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
# ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
```

### Date parsing
All dates come from HTML `<input type="date">` and are parsed with:
```python
datetime.strptime(date_str, '%Y-%m-%d').date()
```

### 404 handling
All delete/edit routes use `Model.query.get_or_404(id)` — Flask returns a 404 automatically for missing records.

### Journal upsert
```python
existing = JournalEntry.query.filter_by(entry_date=parsed_date).first()
if existing:
    # update fields
else:
    # create new
```

---

## Constants (models/schemas.py)

These are imported directly into routes and passed to templates. **Do not hardcode these values in routes or templates.**

| Constant | Used in | Values |
|----------|---------|--------|
| `ACTIVITY_TYPES` | timeline routes & template | List of `(key, label)` tuples |
| `ACTIVITY_TYPE_CONFIG` | timeline template | Dict of icon/color/bg per activity type |
| `REPORT_CATEGORIES` | reports routes & template | List of `(key, label)` tuples |
| `REPORT_CATEGORY_CONFIG` | reports template | Dict of icon/color per category |
| `MEDICATION_STATUS` | medications routes & template | `[('active',…), ('completed',…), ('discontinued',…)]` |
| `LAB_TEST_NAMES` | lab results routes & template | Predefined test name list (includes `'Other'`) |
| `LAB_RESULT_STATUS` | lab results routes & template | `[('normal',…), ('high',…), ('low',…), ('critical',…)]` |

---

## Configuration (config.py)

```python
class Config:
    SECRET_KEY          # from env var SECRET_KEY; has a dev fallback
    DEBUG               # from env var FLASK_DEBUG; default False
    SQLALCHEMY_DATABASE_URI  # sqlite:///jaundice_tracker.db (project root)
    UPLOAD_FOLDER       # <project_root>/static/uploads/
    MAX_CONTENT_LENGTH  # 16 MB
    ALLOWED_EXTENSIONS  # {'pdf', 'jpg', 'jpeg', 'png'}
    DIAGNOSIS_DATE      # '2025-05-01' — update to actual date (YYYY-MM-DD)
```

**To change diagnosis date:** edit `DIAGNOSIS_DATE` in `config.py`. The dashboard computes `days_since_diagnosis` from it.

---

## Testing Architecture

### Key facts
- Test DB is **in-memory SQLite** — real DB is never touched
- Every test function gets a **clean DB** (all rows deleted via `autouse` fixture)
- `conftest.py` defines `app` (session-scoped), `client` (function-scoped), `clean_db` (autouse function-scoped)
- Tests use `follow_redirects=True` to get the flash message in the response

### Running tests
```bash
python -m pytest tests/ -v          # all tests
python -m pytest tests/test_journal.py -v   # one module
```

### Test pattern for CRUD
```python
def test_add_x(self, client):
    resp = client.post('/route/add', data={...}, follow_redirects=True)
    assert resp.status_code == 200
    assert 'success' in resp.data.decode().lower()

def test_edit_x(self, client, app):
    # 1. Create via HTTP
    client.post(ADD_URL, data={...}, follow_redirects=True)
    # 2. Get the ID from DB inside app context
    with app.app_context():
        obj = Model.query.first()
        oid = obj.id
    # 3. Edit via HTTP
    client.post(f'/route/edit/{oid}', data={...}, follow_redirects=True)
    # 4. Assert DB state inside app context
    with app.app_context():
        updated = Model.query.get(oid)
        assert updated.field == 'expected'
```

### Test pattern for 404
```python
def test_delete_nonexistent_returns_404(self, client):
    resp = client.post('/route/delete/99999', follow_redirects=True)
    assert resp.status_code == 404
```

---

## Common Pitfalls

| Pitfall | Detail |
|---------|--------|
| **Journal unique date** | Posting a journal entry for an existing date must UPDATE, not INSERT. The unique constraint on `entry_date` will raise `IntegrityError` on duplicate insert. |
| **File path storage** | Only the filename is stored in `attachment_path` / `file_path`. Reconstruct full path with `os.path.join(Config.UPLOAD_FOLDER, filename)`. |
| **Date parsing format** | Always `'%Y-%m-%d'`. HTML date inputs produce this format. |
| **`init_db` must run in app context** | `db.create_all()` is inside `with app.app_context()`. When writing tests or scripts, always use the app context. |
| **Status validation on update-status** | Only `active`, `completed`, `discontinued` are accepted. Invalid values are silently ignored (no DB write). |
| **Ephemeral filesystem on free hosts** | Render free tier wipes `static/uploads/` and `jaundice_tracker.db` on redeploy. Use a persistent disk for production. |
| **`FLASK_DEBUG` in production** | Must be `False` (or unset). Never pass `debug=True` directly to `app.run()` in production. |
| **SQLAlchemy `.get()` deprecation** | `Model.query.get(id)` is legacy in SQLAlchemy 2.x. Prefer `db.session.get(Model, id)` in new code. |

---

## How to Add a New Feature (checklist)

- [ ] **Model:** Add class to `models/db.py`. No migration needed — `db.create_all()` handles it.
- [ ] **Constants:** Add any dropdown/choice lists to `models/schemas.py`.
- [ ] **Route:** Create `routes/myfeature.py` with a Blueprint and a URL prefix.
- [ ] **Register:** Import and `app.register_blueprint(myfeature_bp)` in `app.py`.
- [ ] **Template:** Create `templates/myfeature.html` extending `base.html`.
- [ ] **Nav link:** Add a nav item in `templates/base.html`.
- [ ] **Tests:** Create `tests/test_myfeature.py` following existing patterns.

---

## Environment Variables

| Variable | Required in prod | Description |
|----------|-----------------|-------------|
| `SECRET_KEY` | ✅ Yes | Flask session signing key. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_DEBUG` | ❌ (default False) | Set to `true` only in local dev |

---

## Running Locally (quick reference)

```powershell
# Windows
.\venv\Scripts\Activate.ps1
python app.py
# → http://127.0.0.1:5000

# Run tests (separate terminal, venv active)
python -m pytest tests/ -v
```
