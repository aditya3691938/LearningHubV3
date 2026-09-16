# Learning Hub V3 — Known Issues Inventory

This document documents all identified bugs, edge-case failures, and implementation anomalies discovered during code inspection of **Learning Hub V3**.

---

## Known Issues Inventory Matrix

| Issue ID | Description | Location | Severity | Impact | Current Status | Suggested Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ISS-01** | Passwordless Learner Authentication | `app/routes/auth.py` (L42-151) | **High** | Any user entering a valid Global ID (e.g. `10001`) instantly accesses learner portal without authentication. | Present in Code | Implement password hashing or integrate Google OAuth2 / SSO as indicated in code comments. |
| **ISS-02** | Hardcoded Admin Credentials in Seed Script | `app/seed.py` (L116-118) | **High** | Seeding generates admin user `admin` with password `admin`. | Present in Code | Enforce environment-variable driven initial admin password setup. |
| **ISS-03** | CSRF Exemption on B2 Upload Routes | `app/__init__.py` (L50) | **Medium** | `b2_bp` is explicitly exempted from CSRF protection (`csrf.exempt(b2_bp)`). | Present in Code | Implement API token header validation for S3 upload endpoints. |
| **ISS-04** | Hardcoded Fallback Secret Key | `app/config.py` (L9) | **Medium** | Session secret falls back to static hardcoded string if `.env` is missing. | Present in Code | Raise explicit error on startup if `SECRET_KEY` is not provided in production. |
| **ISS-05** | Legacy Redundant Columns in `live_classes` | `app/models/live_class.py` (L29-30) | **Low** | Columns `facilitator_name` and `co_facilitator_name` stored alongside relational IDs `facilitator_id`. | Present in Code | Perform DB migration to drop legacy string columns and rely on relational joins. |
| **ISS-06** | Lack of Automated Test Suite | Base repository | **High** | 0% test coverage across all 13 Blueprints and core services. | Present in Code | Build unit and integration test suite with `pytest`. |
