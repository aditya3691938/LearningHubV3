# Learning Hub V3 — Deployment & Environment Setup Guide

This guide provides step-by-step instructions to configure, initialize, and deploy **Learning Hub V3** in local development, production Waitress/Gunicorn environments, and cloud serverless environments (Vercel/Render).

---

## 1. Prerequisites & Runtime Requirements

- **Python Version**: Python 3.10+ (tested on Python 3.14.2)
- **Database Backend**: SQLite 3 (Development) or PostgreSQL 13+ (Production)
- **C Compiler / Build Tools**: Required for `psycopg2-binary`, `pypdfium2`, `reportlab`, `pillow`
- **Object Storage (Optional)**: AWS S3, Backblaze B2, or self-hosted MinIO bucket for decoupled file hosting

---

## 2. Environment Configuration (`.env`)

Create a `.env` file in the root directory `LearningHubV3/` based on `.env.example`:

```env
# Flask Core Configuration
SECRET_KEY=<configured_secure_random_key>
FLASK_ENV=production
PORT=5000

# Database Configuration (SQLite default fallback; PostgreSQL for Production scale)
DATABASE_URL=postgresql://<user>:<password>@<hostname>:5432/<dbname>

# Decoupled Object Storage Provider Configuration ('local' or 's3')
STORAGE_PROVIDER=s3
S3_ACCESS_KEY=<configured_s3_key_id>
S3_SECRET_KEY=<configured_s3_application_key>
S3_ENDPOINT_URL=https://s3.us-west-004.backblazeb2.com
S3_BUCKET=narayana-lms

# Feature Flags
ENABLE_CONTENT_AUTHORING=True
```

> [!CAUTION]
> **NEVER** commit actual API keys, credentials, or production database connection strings to version control.

---

## 3. Local Development Setup

```bash
# 1. Navigate to product directory
cd LearningHubV3

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database tables and seed initial demo data
python -c "from app import create_app; from app.seed import init_db_and_seed; app=create_app(); init_db_and_seed(app)"

# 6. Run development server
python run.py
```
App will be accessible at `http://localhost:5000`.

---

## 4. Production Deployment

### A. Production Deployment on Windows/Linux (Waitress WSGI)
`run.py` detects `FLASK_ENV=production` and automatically starts the Waitress WSGI server:
```bash
python run.py
```

### B. Production Deployment on Render / Linux (Gunicorn)
Use the included `Procfile`:
```bash
web: gunicorn run:app --bind 0.0.0.0:$PORT --timeout 120
```

### C. Serverless Deployment on Vercel
Configuration is pre-built via `vercel.json` and `api/index.py`:
```json
{
  "version": 2,
  "builds": [{ "src": "api/index.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "api/index.py" }]
}
```

---

## 5. PostgreSQL Database Migration

To transition from local SQLite to PostgreSQL for 60,000+ active learners:
```bash
# 1. Update DATABASE_URL in .env
DATABASE_URL=postgresql://lms_user:secure_password@localhost:5432/lms_db

# 2. Run Flask-Migrate dynamic upgrade
flask db upgrade
```
