# Learning Hub V3 — Security, Authentication & Authorization Audit

This document provides a technical security evaluation of the authentication mechanisms, authorization controls, session management, CSRF protection, and security weaknesses in **Learning Hub V3**.

---

## 1. Authentication Mechanisms

### 1.1 Administrator Authentication
- **Endpoint**: `/login` (`POST`)
- **Mechanism**: Form-based username/password login.
- **Password Storage & Hashing**: Admin passwords are stored in `admin_users.password_hash` hashed using PBKDF2 with SHA-256 via Werkzeug's `generate_password_hash()` and `check_password_hash()`.
- **Session Assignment**: On successful validation, Flask session variable `session['admin_logged_in'] = True` and `session['admin_username'] = admin.username` are set.

### 1.2 Learner Authentication
- **Endpoint**: `/learner/login` (`POST`)
- **Mechanism**: Passwordless Global ID authentication. Learners submit their corporate/academic Global ID (e.g. `10001` or mapped aliases `learner01`-`learner05`).
- **Password Check**: **None**. The current codebase does NOT require or verify a password for learners.
- **Session Assignment**: On Global ID lookup, system sets `session['learner_id'] = learner.id`, `session['learner_global_id'] = learner.global_id`, `session['learner_name'] = learner.name`, and `session['learner_theme'] = learner.theme`.
- **Architectural Note in Code**: Inline comments note: *"Later this endpoint will be replaced by Google SSO."*

---

## 2. Session Management & Cookie Security

- **Session Type**: Flask client-side cryptographically signed session cookies stored in the user's browser.
- **Secret Key Configuration**: Configured via `SECRET_KEY` environment variable. Defaults to `'narayana-lnd-lms-super-secret-key-2026'` in `app/config.py`.
- **Session Invalidation**: Endpoint `/logout` clears session data via `session.clear()`.

---

## 3. Cross-Site Request Forgery (CSRF) Protection

- **CSRF Engine**: Integrated via Flask-WTF `CSRFProtect(app)`.
- **Form Enforcement**: HTML forms in Jinja2 templates include `{{ csrf_token() }}` hidden inputs.
- **CSRF Exemptions**: `b2_bp` blueprint is explicitly exempted from CSRF (`csrf.exempt(b2_bp)` in `app/__init__.py`) to support direct payload uploads to S3 storage endpoints.

---

## 4. Protected Routes & Authorization

Route protection is evaluated in route handlers using session variables:
```python
# Admin Route Guard Pattern
if not session.get('admin_logged_in'):
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.admin_login'))

# Learner Route Guard Pattern
learner_id = session.get('learner_id')
if not learner_id:
    flash('Please log in with your Global ID.', 'warning')
    return redirect(url_for('auth.learner_login'))
```

---

## 5. Security Audit Findings & Vulnerabilities

> [!WARNING]
> **SEC-01: Passwordless Learner Authentication**
> Any user who knows or guesses a valid Global ID (e.g., `10001`, `10002`) can log in as that learner without entering a password, accessing their profile, certificates, and team views.

> [!WARNING]
> **SEC-02: Default Hardcoded Administrator Credentials**
> The database seed script (`app/seed.py`) automatically generates an administrator account with username `admin` and password `admin` if missing.

> [!CAUTION]
> **SEC-03: Hardcoded Fallback Secret Key**
> If the `SECRET_KEY` environment variable is not defined, Flask falls back to a hardcoded string (`'narayana-lnd-lms-super-secret-key-2026'`), enabling attackers to forge valid session cookies if deployed without `.env`.

> [!IMPORTANT]
> **SEC-04: CSRF Exemption on File Uploads**
> Disabling CSRF protection on `b2_bp` routes allows cross-site requests to upload unauthenticated payloads to S3 storage endpoints.
