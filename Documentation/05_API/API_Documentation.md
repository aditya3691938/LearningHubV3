# Learning Hub V3 — Complete API Documentation & Endpoint Inventory

This document provides complete documentation for every HTTP route and API endpoint implemented in **Learning Hub V3**.

---

## 1. API Endpoint Inventory Table

| API ID | Method | Endpoint | Purpose | Auth Required | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **API-001** | `GET` | `/` | Root redirect to dashboard or login | No | **Active** |
| **API-002** | `GET, POST` | `/login` | L&D Admin login page and authentication | No | **Active** |
| **API-003** | `GET` | `/logout` | Clears session data and logs user out | Yes (Session) | **Active** |
| **API-004** | `GET, POST` | `/learner/login` | Passwordless Learner Global ID login | No | **Active** |
| **API-005** | `GET` | `/dashboard` | Renders administrative executive dashboard | Yes (Admin) | **Active** |
| **API-006** | `GET` | `/courses/` | Lists all courses (Self Paced, Live Online, In Person) | Yes (Admin) | **Active** |
| **API-007** | `GET, POST` | `/courses/create` | Renders creation form & creates new course | Yes (Admin) | **Active** |
| **API-008** | `GET, POST` | `/courses/<id>/edit` | Renders edit form & updates course metadata | Yes (Admin) | **Active** |
| **API-009** | `POST` | `/courses/<id>/archive` | Archives a course (`is_archived=True`) | Yes (Admin) | **Active** |
| **API-010** | `GET, POST` | `/courses/<id>/lessons/create` | Adds a new lesson to a course | Yes (Admin) | **Active** |
| **API-011** | `GET` | `/courses/courseware/<id>/raw` | Streams raw courseware file (PDF, MP4, SCORM) | Yes (Session) | **Active** |
| **API-012** | `GET` | `/courses/courseware/<id>/scorm_player` | Serves embedded SCORM player iframe | Yes (Session) | **Active** |
| **API-013** | `GET, POST` | `/courses/rise_editor/<courseware_id>` | Rise 360 block courseware interactive editor | Yes (Admin) | **Active** |
| **API-014** | `GET, POST` | `/courses/<id>/assessment/<type>` | Serves MCQ assessment & evaluates answers | Yes (Learner) | **Active** |
| **API-015** | `GET` | `/classes/` | Lists all scheduled live classes | Yes (Admin) | **Active** |
| **API-016** | `GET, POST` | `/classes/create` | Schedules a new live online / in-person class | Yes (Admin) | **Active** |
| **API-017** | `GET, POST` | `/classes/<id>/enroll` | Enrolls learners into live class roster | Yes (Admin) | **Active** |
| **API-018** | `POST` | `/classes/<id>/lock` | Locks class roster against attendance edits | Yes (Admin) | **Active** |
| **API-019** | `POST` | `/classes/<id>/unlock` | Unlocks class roster with mandatory audit reason | Yes (Admin) | **Active** |
| **API-020** | `GET` | `/attendance/` | Lists attendance records & live class QR links | Yes (Admin) | **Active** |
| **API-021** | `GET` | `/attendance/qr_view/<class_id>` | Facilitator view displaying live QR code | Yes (Session) | **Active** |
| **API-022** | `GET` | `/attendance/scan/<class_id>` | Learner mobile camera scanner endpoint | Yes (Learner) | **Active** |
| **API-023** | `GET, POST` | `/attendance/manual/<class_id>` | Admin manual attendance override & audit log | Yes (Admin) | **Active** |
| **API-024** | `GET` | `/learners/` | Lists learner directory with filters | Yes (Admin) | **Active** |
| **API-025** | `POST` | `/learners/import` | Bulk imports learners from uploaded Excel file | Yes (Admin) | **Active** |
| **API-026** | `GET` | `/learners/export` | Exports learner roster to downloadable Excel | Yes (Admin) | **Active** |
| **API-027** | `GET` | `/learners/portal` | Main Learner Portal view (courses, badges, team) | Yes (Learner) | **Active** |
| **API-028** | `GET, POST` | `/learners/issues` | Learner support ticket log & creation | Yes (Learner) | **Active** |
| **API-029** | `POST` | `/learners/issues/<id>/resolve` | Admin marks support ticket resolved | Yes (Admin) | **Active** |
| **API-030** | `GET` | `/feedback/` | Lists feedback question repositories | Yes (Admin) | **Active** |
| **API-031** | `GET, POST` | `/feedback/create` | Creates new feedback question repository | Yes (Admin) | **Active** |
| **API-032** | `GET, POST` | `/feedback/submit/<repo_id>` | Learner submits session feedback responses | Yes (Learner) | **Active** |
| **API-033** | `GET` | `/certificates/download/<cert_id>` | Downloads generated PDF certificate | Yes (Learner) | **Active** |
| **API-034** | `GET` | `/certificates/verify` | Public certificate authenticity verification | No | **Active** |
| **API-035** | `GET` | `/reports/` | Executive compliance analytics & exports | Yes (Admin) | **Active** |
| **API-036** | `GET, POST` | `/learning_wall/` | Renders social wall, creates posts/reactions | Yes (Session) | **Active** |
| **API-037** | `GET` | `/super_admin/` | Renders Super Admin console | Yes (SuperAdmin) | **Active** |
| **API-038** | `GET` | `/super_admin/backup_db` | Downloads database backup zip/db file | Yes (SuperAdmin) | **Active** |
| **API-039** | `POST` | `/super_admin/reset_data` | Triggers database wipe and initial re-seeding | Yes (SuperAdmin) | **Active** |
| **API-040** | `POST` | `/b2/upload` | Direct file upload endpoint to S3/B2 storage | Exempt (CSRF) | **Active** |

---

## 2. Detailed Endpoint Documentation Examples

### API-002: L&D Admin Login
- **HTTP Method**: `POST`
- **Endpoint**: `/login`
- **Purpose**: Authenticates administrator credentials and initializes admin session.
- **Authentication**: None required prior to request.
- **Request Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Request Parameters**:
  - `username` (string, required): Admin username (default: `admin`)
  - `password` (string, required): Admin password (default: `admin`)
  - `csrf_token` (string, required): CSRF security token
- **Validation**: Verifies non-empty string and verifies password hash against `AdminUser.password_hash` via `check_password_hash`.
- **Response Success**: 302 Redirect to `/dashboard`. Session variables `session['admin_logged_in'] = True` set.
- **Response Error**: 200 OK rendering `auth/admin_login.html` with banner "Invalid Username or Password".
- **Database Operations**: `AdminUser.query.filter_by(username=username).first()`.

### API-004: Passwordless Learner Login
- **HTTP Method**: `POST`
- **Endpoint**: `/learner/login`
- **Purpose**: Log in learners via Global ID, calculate login streaks, and award gamification points.
- **Authentication**: None required.
- **Request Parameters**:
  - `global_id` (string, required): Learner Global ID (e.g. `10001` or alias `learner01`).
  - `class_id` (string, optional): Target class ID to redirect after login.
  - `course_id` (string, optional): Target course ID to redirect after login.
- **Success Flow**: Sets `session['learner_id']`, calculates streak against `last_active_date`, invokes `award_points()`, redirects to `/learners/portal`.
- **Database Operations**: `Learner.query`, updates `current_streak`, `points`, `last_active_date`, inserts `LearnerBadge`.

### API-022: Mobile QR Attendance Scanning
- **HTTP Method**: `GET`
- **Endpoint**: `/attendance/scan/<class_id>`
- **Purpose**: Records instantaneous live class attendance when a learner scans a QR code with their mobile device.
- **Authentication**: Required (`session['learner_id']`).
- **Path Parameters**: `class_id` (string/int): Target LiveClass ID.
- **Logic**: Checks if `LiveClass` is locked (`is_locked == True`). If locked, returns error "Class attendance is locked". If open, queries `Attendance`. If record exists, returns "Attendance already recorded". Otherwise creates `Attendance(class_id=..., learner_id=..., status='Present', recorded_via='QR')`.
- **Database Operations**: Inserts row into `attendances` table.
