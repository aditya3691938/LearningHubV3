# Learning Hub V3 — Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document defines the functional and non-functional requirements of **Learning Hub V3**, based strictly on the current implemented codebase.

### 1.2 Scope
Learning Hub V3 is an enterprise Learning & Development management web application designed for corporate and educational organizations. It supports multi-mode course delivery (Self-Paced, Live Online, Live In-Person), QR-code based live session attendance, interactive quizzes, automated PDF certificate generation, Rise 360 block content authoring, SCORM package execution, gamified engagement, social learning wall interactions, and administrative report exports.

### 1.3 Definitions and Terminology
- **Global ID**: Unique learner identification string (e.g. `10001`) used for passwordless login and corporate roster mapping.
- **Rise 360 Block**: Modular courseware JSON content schema allowing interactive accordion, flipcard, process, and quiz blocks.
- **SCORM**: Sharable Content Object Reference Model standard package (`.zip`) parsed and served by the platform.
- **WAL Mode**: Write-Ahead Logging database mode configured in SQLite for high-concurrency read/write operations.

---

## 2. System Overview

Learning Hub V3 follows a modular Flask architecture:
- **Presentation Layer**: Responsive HTML5 templates rendered server-side via Jinja2, styled with vanilla CSS, custom theme skins, and Bootstrap 5.
- **Application Layer**: 13 domain-specific Flask Blueprints managing business logic, routing, authentication, and file processing.
- **Persistence & Storage Layer**: SQLAlchemy ORM backing SQLite (`lms.db`) or PostgreSQL (`DATABASE_URL`), with hybrid local/S3-compatible object storage.

---

## 3. User Roles & Access Control Matrix

| Role | Role Description | Accessible Modules | Key Restrictions |
| :--- | :--- | :--- | :--- |
| **Super Administrator** | Platform DevOps & DB Maintenance | `/super_admin`, `/dashboard`, all admin modules | Full unrestricted system access |
| **L&D Administrator** | Curriculum & Operations Manager | `/courses`, `/classes`, `/learners`, `/attendance`, `/feedback`, `/certificates`, `/reports`, `/quizzes` | Cannot modify system-level S3 configs or trigger DB wipes unless in super admin |
| **Learner** | Student / Employee | `/learners/portal`, `/learning_wall`, `/certificates/verify`, course flows | Cannot access admin interfaces or view other learners' private reports |
| **Facilitator** | Session Instructor | Live class roster view, QR seating display, attendance marking | Access limited to assigned live classes |
| **Manager** | Subordinate Manager | Learner portal team tab | Can only view direct reports (`manager_id` foreign key) |

---

## 4. Functional Requirements

### FR-001: Admin Authentication
- **Description**: L&D Administrators authenticate via username and password.
- **Actor**: L&D Administrator
- **Preconditions**: User navigates to `/login`.
- **Main Flow**: Admin inputs username/password → system verifies hash with `AdminUser.password_hash` → session variable `admin_logged_in=True` set → redirect to `/dashboard`.
- **Validation**: Username and password required.
- **Error Conditions**: Invalid credentials display error banner "Invalid Username or Password".
- **Implementation Status**: **Fully Implemented**

### FR-002: Passwordless Learner Authentication
- **Description**: Learners log in using their Global ID without requiring a password.
- **Actor**: Learner
- **Preconditions**: Learner navigates to `/learner/login`.
- **Main Flow**: Learner submits Global ID → system matches `Learner.global_id` → updates login streak and awards daily points → sets `session['learner_id']` → redirects to `/learners/portal`.
- **Validation**: Global ID string required.
- **Error Conditions**: Non-existent Global ID returns "Learner with Global ID X not found".
- **Implementation Status**: **Fully Implemented** (Security weakness: passwordless).

### FR-003: Course Creation & Management
- **Description**: Admins create, edit, archive, and delete courses.
- **Actor**: L&D Administrator
- **Preconditions**: Admin is logged in.
- **Main Flow**: Admin accesses `/courses/create` → fills details (Title, Duration, Mode: Self Paced / Live Online / Live In Person, Pass Percentage, Thumbnail) → system auto-generates ID (`CRS-SP-001`, `CRS-ON-001`, `CRS-IP-001`) → saves `Course` record.
- **Validation**: Pass percentage 0-100%, required title and mode.
- **Implementation Status**: **Fully Implemented**

### FR-004: Course Lesson & Courseware Management
- **Description**: Admins add lessons and attach multi-format courseware (Video URL, PDF, PPT, Text, SCORM, Google Drive).
- **Actor**: L&D Administrator
- **Preconditions**: Course exists.
- **Main Flow**: Admin selects course → adds lesson (number, title, min_time_minutes) → uploads file or enters external URL → saves `LessonCourseware`.
- **Implementation Status**: **Fully Implemented**

### FR-005: Interactive Rise 360 Courseware Authoring
- **Description**: Admins author interactive block-based courseware versioned in JSON.
- **Actor**: L&D Administrator
- **Preconditions**: `ENABLE_CONTENT_AUTHORING=True` in environment.
- **Main Flow**: Admin accesses Rise editor for courseware → adds text, accordion, flipcard, process, or quiz blocks → saves version to `RiseCoursewareVersion` → publishes.
- **Implementation Status**: **Fully Implemented**

### FR-006: SCORM Package Upload & Execution
- **Description**: Admins upload SCORM `.zip` packages; learners execute them via an embedded iframe.
- **Actor**: Admin / Learner
- **Preconditions**: SCORM zip package uploaded.
- **Main Flow**: Admin uploads SCORM zip → `scorm_service.py` extracts manifest `imsmanifest.xml` → finds launch HTML → learner launches courseware → iframe renders package.
- **Implementation Status**: **Fully Implemented**

### FR-007: Live Class Scheduling & Roster Management
- **Description**: Admins schedule live classes linked to courses with facilitators and rosters.
- **Actor**: L&D Administrator
- **Preconditions**: Course and Facilitator learner exist.
- **Main Flow**: Admin navigates to `/classes/create` → selects course, mode (In Person/Online), date, location/meet_link, facilitator → system generates `CRS-CLS-XXXXXX` → admin enrolls learners.
- **Implementation Status**: **Fully Implemented**

### FR-008: Real-Time QR Code Attendance
- **Description**: Facilitators display a class QR code; learners scan to mark attendance.
- **Actor**: Facilitator / Learner
- **Preconditions**: Live class active; learner logged in on mobile.
- **Main Flow**: Facilitator opens QR seating view → Learner scans QR URL `/attendance/scan/<class_id>` → system records `Attendance(status='Present', recorded_via='QR')`.
- **Implementation Status**: **Fully Implemented**

### FR-009: Manual Attendance Override & Audit Logging
- **Description**: Admins manually update learner attendance status with mandatory reason logging.
- **Actor**: L&D Administrator
- **Preconditions**: Live class roster displayed.
- **Main Flow**: Admin changes status to Present/Absent/Late → submits mandatory justification reason → system updates `Attendance` and creates `AuditLog` entry.
- **Implementation Status**: **Fully Implemented**

### FR-010: Assessment & Quiz Engine
- **Description**: System delivers Pre, Post, and Lesson MCQ assessments and calculates pass percentage.
- **Actor**: Learner
- **Preconditions**: Learner enrolled in course.
- **Main Flow**: Learner submits assessment answers → system evaluates correct options → computes percentage → records `AssessmentAttempt` → if score ≥ `course.pass_percentage`, marks passed.
- **Implementation Status**: **Fully Implemented**

### FR-011: Automated PDF Certificate Generation
- **Description**: System generates verifiable PDF certificates upon course completion and feedback submission.
- **Actor**: System / Learner
- **Preconditions**: Course completed and feedback submitted.
- **Main Flow**: System checks eligibility → invokes `pdf_service.py` using ReportLab → generates PDF file `CERT-XXXXXX.pdf` → saves `Certificate` record → learner downloads.
- **Implementation Status**: **Fully Implemented**

### FR-012: Certificate Verification Portal
- **Description**: Public endpoint to verify certificate authenticity by Certificate ID.
- **Actor**: Public / Employer
- **Preconditions**: Certificate ID provided.
- **Main Flow**: User visits `/certificates/verify?id=CERT-XXXXXX` → system queries database → displays learner name, course title, and issue date.
- **Implementation Status**: **Fully Implemented**

### FR-013: Feedback Survey Repository & Submission
- **Description**: Admins build reusable feedback questionnaires; learners complete surveys after classes/courses.
- **Actor**: Admin / Learner
- **Preconditions**: Feedback repository attached to course/class.
- **Main Flow**: Learner completes course → redirected to feedback survey → submits responses → saved as JSON in `FeedbackResponse`.
- **Implementation Status**: **Fully Implemented**

### FR-014: Gamification Engine (Streaks, Points, Badges)
- **Description**: System tracks daily login streaks, awards points for activities, and grants badges.
- **Actor**: Learner / System
- **Preconditions**: Learner logs in or completes action.
- **Main Flow**: Learner logs in on consecutive days → streak increments → points awarded via `award_points()` → badge awarded via `award_badge()` when criteria met (e.g. 5-day streak).
- **Implementation Status**: **Fully Implemented**

### FR-015: Social Learning Wall
- **Description**: Interactive wall for announcements, birthday wishes, course completion posts, reactions, and comments.
- **Actor**: Learner / Admin
- **Preconditions**: User logged in.
- **Main Flow**: System or user creates post (`LearningWallPost`) → users add reactions (`like`, `love`, `celebrate`, `clap`, `fire`) or submit text comments.
- **Implementation Status**: **Fully Implemented**

### FR-016: Support Ticket Management
- **Description**: Learners log support tickets; admins review and resolve them.
- **Actor**: Learner / Admin
- **Preconditions**: Learner logged in.
- **Main Flow**: Learner submits issue description & category → `LmsIssue` created (`Open`) → Admin reviews in `/learners/issues` → marks `Resolved`.
- **Implementation Status**: **Fully Implemented**

### FR-017: Learner Bulk Import & Export
- **Description**: Admins import learners via Excel/CSV and export learner directories.
- **Actor**: L&D Administrator
- **Preconditions**: Valid Excel file uploaded.
- **Main Flow**: Admin uploads Excel file → pandas parses rows → validates Global IDs → creates/updates `Learner` records.
- **Implementation Status**: **Fully Implemented**

### FR-018: Manager Team Roster View
- **Description**: Managers view progress of direct reports.
- **Actor**: Manager Learner
- **Preconditions**: Learner has subordinates (`Learner.manager_id` points to learner ID).
- **Main Flow**: Manager accesses "My Team" tab in portal → system queries `Learner.query.filter_by(manager_id=...)` → renders team completion statistics.
- **Implementation Status**: **Fully Implemented**

### FR-019: Decoupled Backblaze B2 / MinIO Storage Integration
- **Description**: Storage service delegates file storage to S3 API endpoints when configured.
- **Actor**: System
- **Preconditions**: `STORAGE_PROVIDER=s3` set in environment.
- **Main Flow**: Upload requested → `b2_service.py` uploads byte stream via `boto3` to S3 bucket → generates direct/presigned S3 URL.
- **Implementation Status**: **Fully Implemented**

### FR-020: Super Admin Backup, Restore & Reset
- **Description**: Super admin exports database backup, restores DB, or resets data cleanly.
- **Actor**: Super Administrator
- **Preconditions**: Logged in as super admin.
- **Main Flow**: Super admin selects Backup Database → system copies `lms.db` to downloadable archive; select Reset → system re-executes `init_db_and_seed`.
- **Implementation Status**: **Fully Implemented**

---

## 5. Non-Functional Requirements

### 5.1 Performance
- **Database Indexing**: Explicit database indexes on `Learner.global_id`, `Course.course_id`, `LiveClass.class_id`, `Certificate.certificate_id`, `LearnerEnrollment.learner_id`, `LearnerEnrollment.course_id`.
- **SQLite Concurrency**: Configured WAL mode (`PRAGMA journal_mode=WAL`) and normal synchronous mode (`PRAGMA synchronous=NORMAL`) to support concurrent reader threads.
- **File Payload Limit**: Maximum HTTP payload upload size capped at 1 GB (`MAX_CONTENT_LENGTH = 1024 * 1024 * 1024`).

### 5.2 Security
- **Admin Password Protection**: Admin passwords hashed using PBKDF2/SHA256 via Werkzeug (`generate_password_hash`).
- **CSRF Protection**: Universal CSRF protection enabled via Flask-WTF (`CSRFProtect`), with explicit exemption for B2 storage routes.
- **Security Vulnerabilities Identified**: Learner authentication lacks password verification (passwordless Global ID). Hardcoded default admin credentials in seed script.

### 5.3 Reliability & Availability
- **WSGI Production Support**: Production deployment configured with Waitress WSGI server (`waitress.serve`) on Windows/Linux and Gunicorn on Render (`Procfile`).
- **Fallback Storage**: Automatic local storage fallback (`uploads/`) if S3/MinIO cloud storage credentials are not provided.

### 5.4 Maintainability & Extensibility
- **Modular Blueprints**: Clean separation of concerns across 13 Flask Blueprints.
- **Alembic Migrations**: Relational database migration support enabled via Flask-Migrate.

### 5.5 Usability
- **Dynamic Styling & Themes**: Theme engine supporting custom skins (`navy`, etc.) persisted per learner session.
- **Responsive Layout**: Bootstrap 5 responsive layout compatible with mobile browsers for QR attendance scanning.
