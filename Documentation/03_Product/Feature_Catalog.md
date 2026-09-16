# Learning Hub V3 — Detailed Feature Catalog

This document lists every implemented feature module in **Learning Hub V3**, detailing its purpose, entry point, user roles, API/backend implementation, database interactions, and implementation status.

---

## Feature Index Matrix

| Feature ID | Feature Name | Entry Point | User Role | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FEAT-01** | Admin Authentication & Dashboard | `/login`, `/dashboard` | Admin | **Fully Implemented** |
| **FEAT-02** | Learner Global ID Login | `/learner/login` | Learner | **Fully Implemented** |
| **FEAT-03** | Course Management & Catalog | `/courses/` | Admin | **Fully Implemented** |
| **FEAT-04** | Multi-Format Courseware Engine | `/courses/<id>/lessons` | Admin / Learner | **Fully Implemented** |
| **FEAT-05** | SCORM 1.2 / 2004 Package Player | `/courses/courseware/<id>/scorm_player` | Learner | **Fully Implemented** |
| **FEAT-06** | Interactive Rise 360 Authoring | `/courses/rise_editor/<id>` | Admin | **Fully Implemented** |
| **FEAT-07** | Live Class Roster & Scheduling | `/classes/` | Admin / Facilitator | **Fully Implemented** |
| **FEAT-08** | Real-Time QR Attendance Engine | `/attendance/` | Facilitator / Learner | **Fully Implemented** |
| **FEAT-09** | Manual Attendance & Audit Log | `/attendance/manual` | Admin | **Fully Implemented** |
| **FEAT-10** | Assessment & Quiz Engine | `/courses/<id>/assessment` | Learner | **Fully Implemented** |
| **FEAT-11** | PDF Certificate Generation | `/certificates/` | Learner / Admin | **Fully Implemented** |
| **FEAT-12** | Certificate Verification Portal | `/certificates/verify` | Public | **Fully Implemented** |
| **FEAT-13** | Feedback Survey Repository | `/feedback/` | Admin / Learner | **Fully Implemented** |
| **FEAT-14** | Gamification (Points/Streaks/Badges) | `/learners/portal` | Learner | **Fully Implemented** |
| **FEAT-15** | Social Learning Wall | `/learning_wall/` | All | **Fully Implemented** |
| **FEAT-16** | Learner Directory & Excel Import | `/learners/` | Admin | **Fully Implemented** |
| **FEAT-17** | Manager Team Dashboard | `/learners/portal` | Manager Learner | **Fully Implemented** |
| **FEAT-18** | Support Ticket Helpdesk | `/learners/issues` | Learner / Admin | **Fully Implemented** |
| **FEAT-19** | Decoupled S3/B2 Storage | `/b2_routes` | System | **Fully Implemented** |
| **FEAT-20** | Super Admin Management | `/super_admin/` | Super Admin | **Fully Implemented** |

---

## Detailed Feature Descriptions

### FEAT-01: Admin Authentication & Dashboard
- **Purpose**: Authenticates L&D administrators and presents system-wide metrics (total learners, active courses, scheduled live classes, open support tickets, completion trends).
- **User Role**: Admin / Super Admin
- **Entry Point**: `http://localhost:5000/login` → `http://localhost:5000/dashboard`
- **APIs Used**: `GET /login`, `POST /login`, `GET /dashboard`, `GET /logout`
- **Database Operations**: Reads `AdminUser`, `Learner`, `Course`, `LiveClass`, `LmsIssue`.
- **Status**: **Fully Implemented**

### FEAT-02: Learner Global ID Login
- **Purpose**: Authenticates learners via passwordless Global ID lookup, calculates login streak, awards daily gamification points, and grants badges.
- **User Role**: Learner
- **Entry Point**: `http://localhost:5000/learner/login`
- **APIs Used**: `GET /learner/login`, `POST /learner/login`
- **Database Operations**: Queries `Learner` by `global_id`; updates `points`, `current_streak`, `last_active_date`; inserts `LearnerBadge`.
- **Status**: **Fully Implemented**

### FEAT-03: Course Management & Catalog
- **Purpose**: Provides full CRUD management of Self-Paced, Live Online, and Live In-Person courses with auto-generated course IDs (`CRS-SP-XXX`, `CRS-ON-XXX`, `CRS-IP-XXX`).
- **User Role**: Admin
- **Entry Point**: `http://localhost:5000/courses/`
- **APIs Used**: `GET /courses/`, `GET /courses/create`, `POST /courses/create`, `POST /courses/<id>/edit`, `POST /courses/<id>/archive`
- **Database Operations**: `Course.query`, `Course.generate_course_id()`.
- **Status**: **Fully Implemented**

### FEAT-04: Multi-Format Courseware Engine
- **Purpose**: Supports video links (YouTube embed), uploaded PDFs, PPTX slides, text lessons, Google Drive links, and non-downloadable materials.
- **User Role**: Admin / Learner
- **Entry Point**: `http://localhost:5000/courses/<id>/lessons`
- **APIs Used**: `POST /courses/<id>/lessons/create`, `GET /courses/courseware/<id>/raw`
- **Database Operations**: `CourseLesson`, `LessonCourseware`, `CourseMaterial`.
- **Status**: **Fully Implemented**

### FEAT-05: SCORM 1.2 / 2004 Package Player
- **Purpose**: Unzips SCORM `.zip` packages, parses `imsmanifest.xml`, and executes interactive HTML5 courseware inside an embedded iframe.
- **User Role**: Learner
- **Entry Point**: `http://localhost:5000/courses/courseware/<id>/scorm_player`
- **APIs Used**: `GET /courses/courseware/<id>/scorm_player`, `GET /courses/scorm_content/<id>/<path>`
- **Database Operations**: Reads `LessonCourseware` (type SCORM). `scorm_service.py` handles unzipping.
- **Status**: **Fully Implemented**

### FEAT-06: Interactive Rise 360 Block Authoring
- **Purpose**: Provides a block-based courseware builder to author interactive accordions, flipcards, process diagrams, and quizzes with version control.
- **User Role**: Admin
- **Entry Point**: `http://localhost:5000/courses/rise_editor/<courseware_id>`
- **APIs Used**: `GET /courses/rise_editor/<id>`, `POST /courses/rise_editor/<id>/save`
- **Database Operations**: Creates `RiseCoursewareVersion` records storing JSON payloads.
- **Status**: **Fully Implemented**

### FEAT-07: Live Class Roster & Scheduling
- **Purpose**: Schedules live classes (In Person or Online via Google Meet), assigns facilitators, and manages learner enrollment rosters.
- **User Role**: Admin / Facilitator
- **Entry Point**: `http://localhost:5000/classes/`
- **APIs Used**: `GET /classes/`, `POST /classes/create`, `POST /classes/<id>/enroll`
- **Database Operations**: `LiveClass`, `LearnerEnrollment`.
- **Status**: **Fully Implemented**

### FEAT-08: Real-Time QR Attendance Engine
- **Purpose**: Generates dynamic QR codes for facilitators and provides mobile camera scanning for learners to mark instantaneous attendance.
- **User Role**: Facilitator / Learner
- **Entry Point**: `http://localhost:5000/attendance/qr_view/<class_id>`
- **APIs Used**: `GET /attendance/qr_view/<id>`, `GET /attendance/scan/<id>`
- **Database Operations**: `Attendance.query.filter_by(class_id=..., learner_id=...)`, creates `Attendance(recorded_via='QR')`.
- **Status**: **Fully Implemented**

### FEAT-09: Manual Attendance & Audit Log
- **Purpose**: Allows admins to manually update learner attendance status while requiring a mandatory justification reason logged to the audit table.
- **User Role**: Admin
- **Entry Point**: `http://localhost:5000/attendance/manual/<class_id>`
- **APIs Used**: `POST /attendance/manual/<class_id>`
- **Database Operations**: Updates `Attendance`, inserts `AuditLog(action='MANUAL_ATTENDANCE')`.
- **Status**: **Fully Implemented**

### FEAT-10: Assessment & Quiz Engine
- **Purpose**: Conducts MCQ assessments (Pre-Course, Lesson Post, End-Course, Standalone Quiz), evaluates score percentages, and determines passing criteria (default 80%).
- **User Role**: Learner
- **Entry Point**: `http://localhost:5000/courses/<id>/assessment/<type>`
- **APIs Used**: `GET /courses/<id>/assessment/<type>`, `POST /courses/<id>/assessment/<type>/submit`
- **Database Operations**: Inserts `AssessmentAttempt`, updates `LearnerEnrollment.completion_status`.
- **Status**: **Fully Implemented**

### FEAT-11: PDF Certificate Generation
- **Purpose**: Automatically generates verifiable, downloadable PDF certificates via ReportLab when course completion requirements are satisfied.
- **User Role**: Learner / Admin
- **Entry Point**: `http://localhost:5000/certificates/download/<cert_id>`
- **APIs Used**: `GET /certificates/download/<id>`, `GET /certificates/generate/<enrollment_id>`
- **Database Operations**: Creates `Certificate` with unique `CERT-XXXXXX` ID. `pdf_service.py` outputs PDF.
- **Status**: **Fully Implemented**

### FEAT-12: Certificate Verification Portal
- **Purpose**: Provides a public webpage to verify the authenticity of issued certificates using their unique ID.
- **User Role**: Public
- **Entry Point**: `http://localhost:5000/certificates/verify`
- **APIs Used**: `GET /certificates/verify?id=CERT-XXXXXX`
- **Database Operations**: Queries `Certificate` by `certificate_id`.
- **Status**: **Fully Implemented**

### FEAT-13: Feedback Survey Repository
- **Purpose**: Manages reusable feedback question repositories (MCQ & Text) and collects survey responses after course/class completion.
- **User Role**: Admin / Learner
- **Entry Point**: `http://localhost:5000/feedback/`
- **APIs Used**: `GET /feedback/`, `POST /feedback/create`, `POST /feedback/submit/<repo_id>`
- **Database Operations**: `FeedbackRepository`, `FeedbackQuestion`, `FeedbackResponse`.
- **Status**: **Fully Implemented**

### FEAT-14: Gamification Engine
- **Purpose**: Tracks daily login streaks, awards experience points, and automatically bestows badges (`Streak Master 🔥`, `Fast Learner`).
- **User Role**: Learner
- **Entry Point**: `http://localhost:5000/learners/portal`
- **APIs Used**: Integrated into auth and course completion hooks (`gamification.py`).
- **Database Operations**: `Learner.points`, `Learner.current_streak`, `LearnerBadge`.
- **Status**: **Fully Implemented**

### FEAT-15: Social Learning Wall
- **Purpose**: Community wall displaying system updates, birthday wishes, course completions, earned certificates, reactions (like, love, celebrate, clap, fire), and comments.
- **User Role**: Learner / Admin
- **Entry Point**: `http://localhost:5000/learning_wall/`
- **APIs Used**: `GET /learning_wall/`, `POST /learning_wall/post`, `POST /learning_wall/react`, `POST /learning_wall/comment`
- **Database Operations**: `LearningWallPost`, `LearningWallReaction`, `LearningWallComment`.
- **Status**: **Fully Implemented**

### FEAT-16: Learner Directory & Bulk Import/Export
- **Purpose**: Admin directory listing all learners, filtering by department/location/branch, Excel bulk import via pandas, and Excel export.
- **User Role**: Admin
- **Entry Point**: `http://localhost:5000/learners/`
- **APIs Used**: `GET /learners/`, `POST /learners/import`, `GET /learners/export`
- **Database Operations**: `Learner.query`, bulk insert/update.
- **Status**: **Fully Implemented**

### FEAT-17: Manager Team Dashboard
- **Purpose**: Allows learners with direct reports (`manager_id`) to monitor team members' course progress, completion status, and extension requests.
- **User Role**: Manager Learner
- **Entry Point**: `http://localhost:5000/learners/portal` (My Team tab)
- **APIs Used**: `GET /learners/portal`
- **Database Operations**: `Learner.subordinates`, `LearnerEnrollment.query`.
- **Status**: **Fully Implemented**

### FEAT-18: Support Ticket Helpdesk
- **Purpose**: Allows learners to file technical/content/certificate support tickets and enables admins to resolve them.
- **User Role**: Learner / Admin
- **Entry Point**: `http://localhost:5000/learners/issues`
- **APIs Used**: `POST /learners/issues/create`, `POST /learners/issues/<id>/resolve`
- **Database Operations**: `LmsIssue`.
- **Status**: **Fully Implemented**

### FEAT-19: Decoupled S3/Backblaze B2 Storage
- **Purpose**: Decouples media file storage from local server to S3-compatible cloud storage (Backblaze B2 or MinIO) using `boto3`.
- **User Role**: System
- **Entry Point**: `/b2_routes`
- **APIs Used**: `POST /b2/upload`, `GET /b2/file/<filename>`
- **Database Operations**: Stores S3 file keys in database models.
- **Status**: **Fully Implemented**

### FEAT-20: Super Admin Management Console
- **Purpose**: Provides system-level database backup download, DB restore, system reset, and audit log inspection.
- **User Role**: Super Admin
- **Entry Point**: `http://localhost:5000/super_admin/`
- **APIs Used**: `GET /super_admin/`, `GET /super_admin/backup_db`, `POST /super_admin/reset_data`
- **Database Operations**: `AuditLog.query`, SQLite file copy.
- **Status**: **Fully Implemented**
