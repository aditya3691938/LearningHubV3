# Learning Hub V3 — Complete Database Documentation & Entity Reference

This document provides complete documentation for all database entities, tables, fields, data types, constraints, foreign keys, cascading behavior, and soft delete/archival policies in **Learning Hub V3**.

---

## 1. Relational Data Dictionary

### 1.1 `admin_users` Table
- **Purpose**: Stores administrator account credentials.
- **Fields**:
  - `id` (Integer, Primary Key, Auto-increment)
  - `username` (String(80), Unique, Not Null, Default: `'admin'`)
  - `password_hash` (String(255), Not Null) — Hashed via PBKDF2/SHA256
  - `name` (String(120), Default: `'L&D Administrator'`)
  - `profile_picture` (String(255), Nullable)
  - `date_of_birth` (Date, Nullable)
  - `created_at` (DateTime, Default: `utcnow`)

### 1.2 `learners` Table
- **Purpose**: Stores employee and student learner profiles, org structure, streaks, and points.
- **Fields**:
  - `id` (Integer, Primary Key, Auto-increment)
  - `global_id` (String(50), Unique, Not Null, Indexed) — e.g. `'10001'`
  - `name` (String(120), Not Null)
  - `email` (String(120), Nullable)
  - `profile_picture` (String(255), Nullable)
  - `department` (String(100), Default: `'L&D'`)
  - `date_of_birth` (Date, Nullable)
  - `designation` (String(120), Nullable)
  - `location` (String(120), Nullable) — e.g. `'Hyderabad'`
  - `branch` (String(120), Nullable) — e.g. `'Madhapur'`
  - `manager_id` (Integer, Foreign Key `learners.id`, Indexed, Nullable)
  - `points` (Integer, Not Null, Default: `0`, Indexed)
  - `current_streak` (Integer, Not Null, Default: `0`)
  - `last_active_date` (Date, Nullable)
  - `theme` (String(50), Not Null, Default: `'navy'`)
  - `created_at` (DateTime, Default: `utcnow`)
- **Relationships**:
  - `subordinates`: Self-referential backref `manager`
  - `enrollments`: Cascade delete orphan
  - `attendances`: Cascade delete orphan
  - `certificates`: Cascade delete orphan
  - `badges`: Cascade delete orphan

### 1.3 `courses` Table
- **Purpose**: Stores self-paced and live course offerings.
- **Fields**:
  - `id` (Integer, Primary Key, Auto-increment)
  - `course_id` (String(20), Unique, Not Null, Indexed) — e.g. `'CRS-SP-001'`
  - `name` (String(150), Not Null)
  - `duration_hours` (Float, Default: `1.0`)
  - `description` (Text, Nullable)
  - `mode` (String(20), Default: `'Live'`) — `'Self Paced'`, `'Live Online'`, `'Live In Person'`
  - `pass_percentage` (Float, Not Null, Default: `80.0`)
  - `feedback_repo_id` (Integer, Foreign Key `feedback_repositories.id`, Nullable)
  - `has_certificate` (Boolean, Default: `True`)
  - `thumbnail_filename` (String(255), Nullable)
  - `is_sequential` (Boolean, Default: `True`)
  - `completion_date` (DateTime, Nullable)
  - `is_archived` (Boolean, Default: `False`, Not Null) — Soft deletion flag
  - `created_at` (DateTime, Default: `utcnow`)
  - `pre_quiz_id` (Integer, Foreign Key `quizzes.id`, Nullable)
  - `post_quiz_id` (Integer, Foreign Key `quizzes.id`, Nullable)

### 1.4 `course_lessons` Table
- **Purpose**: Stores individual lesson modules belonging to a course.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `course_id` (Integer, Foreign Key `courses.id`, Not Null)
  - `lesson_number` (Integer, Default: `1`)
  - `title` (String(150), Not Null)
  - `summary` (Text, Nullable)
  - `content` (Text, Nullable)
  - `video_url` (String(500), Nullable)
  - `duration_hours` (Float, Default: `1.0`)
  - `min_time_minutes` (Float, Default: `1.0`) — Required minimum time spent before lesson completion
  - `deadline` (DateTime, Nullable)
  - `created_at` (DateTime, Default: `utcnow`)
  - `pre_quiz_id` (Integer, Foreign Key `quizzes.id`, Nullable)
  - `post_quiz_id` (Integer, Foreign Key `quizzes.id`, Nullable)

### 1.5 `lesson_courseware` Table
- **Purpose**: Stores multi-format learning objects attached to a lesson.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `lesson_id` (Integer, Foreign Key `course_lessons.id`, Not Null)
  - `title` (String(150), Not Null)
  - `courseware_type` (String(80), Default: `'Text'`) — `'Video'`, `'PDF'`, `'PPT'`, `'Text'`, `'SCORM'`, `'Google Drive'`
  - `filename` (String(255), Nullable)
  - `external_url` (String(500), Nullable)
  - `content_text` (Text, Nullable)
  - `uploaded_at` (DateTime, Default: `utcnow`)

### 1.6 `live_classes` Table
- **Purpose**: Stores scheduled in-person and online classroom training sessions.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `class_id` (String(30), Unique, Not Null, Indexed) — e.g. `'CRS-CLS-000001'`
  - `class_name` (String(150), Not Null)
  - `course_id` (Integer, Foreign Key `courses.id`, Not Null)
  - `class_mode` (String(20), Default: `'In Person'`) — `'In Person'`, `'Online'`
  - `class_date` (Date, Not Null)
  - `location` (String(100), Nullable)
  - `branch` (String(100), Nullable)
  - `session_time` (String(50), Default: `'Morning'`)
  - `meet_link` (String(255), Nullable) — Google Meet URL for online mode
  - `facilitator_id` (Integer, Foreign Key `learners.id`, Not Null)
  - `co_facilitator_id` (Integer, Foreign Key `learners.id`, Nullable)
  - `duration_hours` (Float, Default: `1.0`)
  - `expected_attendance` (Integer, Default: `30`)
  - `feedback_repo_id` (Integer, Foreign Key `feedback_repositories.id`, Nullable)
  - `quiz_id` (Integer, Foreign Key `quizzes.id`, Nullable)
  - `is_locked` (Boolean, Default: `False`) — Prevents attendance edits when locked
  - `locked_at` (DateTime, Nullable)
  - `unlock_reason` (Text, Nullable)
  - `created_at` (DateTime, Default: `utcnow`)

### 1.7 `learner_enrollments` Table
- **Purpose**: Tracks learner course enrollments, current progress, assessment scores, and completion status.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `learner_id` (Integer, Foreign Key `learners.id`, Not Null, Indexed)
  - `course_id` (Integer, Foreign Key `courses.id`, Not Null, Indexed)
  - `class_id` (Integer, Foreign Key `live_classes.id`, Nullable)
  - `completion_status` (String(30), Default: `'Enrolled'`) — `'Enrolled'`, `'In Progress'`, `'Completed'`, `'Failed'`
  - `current_lesson` (Integer, Default: `1`)
  - `attempts_count` (Integer, Default: `0`)
  - `final_score` (Float, Nullable)
  - `assigned_at` (DateTime, Default: `utcnow`)
  - `completion_date` (DateTime, Nullable)
  - `extended_deadline` (DateTime, Nullable)
  - `extension_requested` (Boolean, Default: `False`)

### 1.8 `attendances` Table
- **Purpose**: Stores live class attendance entries.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `class_id` (Integer, Foreign Key `live_classes.id`, Not Null)
  - `learner_id` (Integer, Foreign Key `learners.id`, Not Null)
  - `status` (String(20), Default: `'Present'`) — `'Present'`, `'Absent'`, `'Late'`
  - `recorded_via` (String(20), Default: `'QR'`) — `'QR'`, `'Manual'`
  - `manual_reason` (Text, Nullable)
  - `timestamp` (DateTime, Default: `utcnow`)

### 1.9 `certificates` Table
- **Purpose**: Stores earned verifiable PDF certificates.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `certificate_id` (String(50), Unique, Not Null, Indexed) — e.g. `'CERT-A1B2C3'`
  - `learner_id` (Integer, Foreign Key `learners.id`, Not Null)
  - `course_id` (Integer, Foreign Key `courses.id`, Not Null)
  - `issue_date` (DateTime, Default: `utcnow`)
  - `pdf_filename` (String(255), Nullable)

### 1.10 `audit_logs` Table
- **Purpose**: Compliance log for manual attendance overrides and roster unlocks.
- **Fields**:
  - `id` (Integer, Primary Key)
  - `entity_type` (String(50), Not Null) — e.g. `'LiveClass'`, `'Attendance'`
  - `entity_id` (String(50), Not Null)
  - `action` (String(50), Not Null) — e.g. `'UNLOCK'`, `'MANUAL_ATTENDANCE'`
  - `reason` (Text, Not Null)
  - `performed_by` (String(100), Default: `'admin'`)
  - `timestamp` (DateTime, Default: `utcnow`)
