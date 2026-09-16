# Learning Hub V3 — Backend Architecture Document

This document describes the backend design, application factory, blueprint routing structure, service modules, middleware, error handling, and authorization in **Learning Hub V3**.

---

## 1. Overview

The backend of **Learning Hub V3** is constructed as a modular Python Flask monolith using Flask Blueprints, SQLAlchemy ORM, Flask-WTF CSRF protection, Flask-Migrate database migrations, and specialized service modules.

---

## 2. Application Factory (`create_app`)

The application entry point (`run.py` and `api/index.py`) invokes `create_app()` defined in `app/__init__.py`:

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    config_class.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Configure SQLite PRAGMAs for high concurrency
    # Register 13 Blueprints
    # Register custom Jinja filters & global context processors
    # Register custom HTTP error handlers (404, 500, 413)
```

---

## 3. Blueprint Roster & Routing Architecture

| Blueprint Name | Prefix | Python Source File | Purpose |
| :--- | :--- | :--- | :--- |
| `auth_bp` | `/` | `app/routes/auth.py` | Admin login/logout, Learner Global ID login |
| `dashboard_bp` | `/dashboard` | `app/routes/dashboard.py` | Executive analytics dashboard |
| `courses_bp` | `/courses` | `app/routes/courses.py` | Course CRUD, lesson courseware, Rise editor, SCORM |
| `classes_bp` | `/classes` | `app/routes/classes.py` | Live class scheduling, rosters, seating |
| `learners_bp` | `/learners` | `app/routes/learners.py` | Learner directory, profile, Excel import/export, issues |
| `attendance_bp` | `/attendance` | `app/routes/attendance.py` | QR view, mobile scan, manual override & audit |
| `feedback_bp` | `/feedback` | `app/routes/feedback.py` | Feedback repositories, question builder, survey submit |
| `certificates_bp` | `/certificates` | `app/routes/certificates.py` | Certificate download, PDF generation, verification |
| `reports_bp` | `/reports` | `app/routes/reports.py` | Compliance reporting & Excel/PDF export |
| `learning_wall_bp` | `/learning_wall` | `app/routes/learning_wall.py` | Social posts, reactions, comments |
| `super_admin_bp` | `/super_admin` | `app/routes/super_admin.py` | System backup, restore, reset, audit trail |
| `quizzes_bp` | `/quizzes` | `app/routes/quizzes.py` | Standalone quiz creation & management |
| `b2_bp` | `/b2` | `app/routes/b2_routes.py` | Backblaze B2 S3 API upload & file retrieval |

---

## 4. Business Logic Service Layer

```
app/services/
├── assessment_service.py     # Evaluation of MCQ assessments, score calculations, pass thresholds
├── b2_service.py             # Backblaze B2 / S3 client wrapper using boto3
├── gdrive_service.py         # Google Drive URL parser (extracts File IDs, transforms to embed URLs)
├── learning_wall_service.py  # Automated post generation (birthdays, course completion announcements)
├── lock_service.py           # Live class locking / unlocking rules & constraint checking
├── pdf_service.py            # ReportLab PDF canvas drawing engine for certificates
├── qr_service.py             # qrcode library wrapper for generating PNG QR streams
├── report_service.py         # Aggregates completion data and formats pandas / openpyxl DataFrames
├── scorm_service.py          # ZipFile extraction of SCORM archives and manifest parsing
└── storage_service.py        # Abstract storage manager (local filesystem vs S3 cloud)
```

---

## 5. Middleware & Security Controls

1. **CSRF Protection**: Handled globally by `CSRFProtect(app)`. Blueprint `b2_bp` is explicitly exempted via `csrf.exempt(b2_bp)` to allow direct REST API file payload uploads.
2. **Session Context Injection**: Global context processor `inject_global_vars()` runs on every template request to resolve `learner_id`, `admin_logged_in`, unread notification counts, and profile picture paths.
3. **Payload Threshold Enforcement**: Request payload max size configured to 1 GB (`MAX_CONTENT_LENGTH = 1024 * 1024 * 1024`). HTTP 413 error handler captures file size limit violations gracefully.
