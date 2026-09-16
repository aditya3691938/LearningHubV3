# Learning Hub V3 — Database Architecture Document

This document provides a technical explanation of the relational data architecture, ORM models, primary/foreign keys, indexes, and database engine configurations in **Learning Hub V3**.

---

## 1. Overview

**Learning Hub V3** uses **SQLAlchemy 2.0 ORM** to manage relational tables across 14 database models.

- **Primary Database Engine (Local Dev & Standalone)**: SQLite (`lms.db`) configured with WAL mode (`PRAGMA journal_mode=WAL`) and normal synchronization (`PRAGMA synchronous=NORMAL`) for concurrent reads and writes.
- **Production Database Engine**: PostgreSQL support configured via `DATABASE_URL` environment variable with `psycopg2-binary` driver.
- **Schema Management**: Managed via Flask-Migrate (Alembic) with fallback dynamic schema modification statements in `app/seed.py`.

---

## 2. Table Summary Matrix

| Table Name | Primary Key | Key Foreign Keys | Purpose |
| :--- | :--- | :--- | :--- |
| `admin_users` | `id` (Integer) | None | Stores L&D administrator authentication records |
| `learners` | `id` (Integer) | `manager_id` -> `learners.id` | Stores learner profiles, points, streaks, departments |
| `courses` | `id` (Integer) | `feedback_repo_id`, `pre_quiz_id`, `post_quiz_id` | Stores self-paced and live course metadata |
| `course_lessons` | `id` (Integer) | `course_id`, `pre_quiz_id`, `post_quiz_id` | Stores lesson modules within courses |
| `lesson_courseware` | `id` (Integer) | `lesson_id` | Stores multi-format courseware files, SCORM, video links |
| `courseware_audio_tracks` | `id` (Integer) | `courseware_id` | Stores multilingual audio tracks for courseware |
| `course_materials` | `id` (Integer) | `course_id` | Stores supplemental materials and download toggles |
| `course_assessments` | `id` (Integer) | `course_id`, `lesson_id` | MCQ question bank for pre, lesson post, and course end tests |
| `live_classes` | `id` (Integer) | `course_id`, `facilitator_id`, `co_facilitator_id`, `quiz_id` | Live in-person campus and virtual online sessions |
| `learner_enrollments` | `id` (Integer) | `learner_id`, `course_id`, `class_id` | Enrolls learners in courses/classes, tracks status & scores |
| `assessment_attempts` | `id` (Integer) | `enrollment_id`, `lesson_id` | Tracks individual MCQ assessment submissions & scores |
| `lesson_reviews` | `id` (Integer) | `enrollment_id`, `lesson_id` | Audit log of completed lessons per enrollment |
| `attendances` | `id` (Integer) | `class_id`, `learner_id` | Live class attendance records (QR or Manual) |
| `certificates` | `id` (Integer) | `learner_id`, `course_id` | Issued PDF certificate records with unique UUID IDs |
| `external_certificates` | `id` (Integer) | `learner_id` | External certificates uploaded by learners |
| `learner_badges` | `id` (Integer) | `learner_id` | Gamification badges awarded to learners |
| `learner_notifications` | `id` (Integer) | `learner_id`, `course_id`, `lesson_id` | In-app notification messages for learners |
| `feedback_repositories` | `id` (Integer) | None | Reusable survey questionnaire templates |
| `feedback_questions` | `id` (Integer) | `repo_id` | Individual survey questions (MCQ or Text) |
| `feedback_responses` | `id` (Integer) | `repo_id`, `class_id`, `learner_id` | Learner survey response submissions (JSON dictionary) |
| `learning_wall_posts` | `id` (Integer) | `learner_id`, `course_id` | Social community wall announcements and posts |
| `learning_wall_reactions` | `id` (Integer) | `post_id` | Reactions (`like`, `love`, `celebrate`, `clap`, `fire`) |
| `learning_wall_comments` | `id` (Integer) | `post_id` | Text comments on community wall posts |
| `lms_issues` | `id` (Integer) | `learner_id` | Support ticket helpdesk records |
| `audit_logs` | `id` (Integer) | None | Compliance audit trail for manual attendance & overrides |
| `quizzes` | `id` (Integer) | None | Standalone quiz metadata |
| `quiz_questions` | `id` (Integer) | `quiz_id` | Questions belonging to standalone quizzes |
| `rise_courseware_version` | `id` (Integer) | `courseware_id` | Versioned JSON block content for Rise courseware |
| `learner_block_progress` | `id` (Integer) | `learner_id`, `courseware_id` | Granular learner progress per Rise 360 interactive block |

---

## 3. Explicit Database Indexes

To optimize high-concurrency lookups for 60,000+ active learners, the following columns feature explicit B-Tree database indexes:
1. `learners.global_id` (`unique=True`, `index=True`) — Instant learner lookup during login.
2. `courses.course_id` (`unique=True`, `index=True`) — Course lookup by human-readable ID (`CRS-SP-001`).
3. `live_classes.class_id` (`unique=True`, `index=True`) — Class lookup for QR scanning (`CRS-CLS-000001`).
4. `certificates.certificate_id` (`unique=True`, `index=True`) — Public verification portal lookup (`CERT-XXXXXX`).
5. `learner_enrollments.learner_id` (`index=True`) — Learner portal enrollment queries.
6. `learner_enrollments.course_id` (`index=True`) — Course enrollment roster queries.
7. `learners.manager_id` (`index=True`) — Subordinate team queries.
8. `learners.points` (`index=True`) — Leaderboard ranking queries.
9. `rise_courseware_version.courseware_id` (`index=True`) — Rise block version queries.
10. `learner_block_progress.learner_id`, `courseware_id` (`index=True`) — Block progress queries. Unique constraint on `(learner_id, courseware_id, block_id)`.
