# Learning Hub V3 — Requirements Traceability Matrix (RTM)

This matrix maps product requirements to features, UI screens, API endpoints, backend logic handlers, database models, test cases, and current implementation status.

---

| Requirement ID | Requirement Summary | Feature ID | UI Screen | API Endpoint | Backend Logic | Database Models | Test Case | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-001** | Admin Authentication | FEAT-01 | SCR-01 (`/login`) | `POST /login` | `auth_bp.admin_login` | `AdminUser` | Untested | **Implemented** |
| **FR-002** | Learner Passwordless Login | FEAT-02 | SCR-02 (`/learner/login`) | `POST /learner/login` | `auth_bp.learner_login` | `Learner`, `LearnerBadge` | Untested | **Implemented** |
| **FR-003** | Course Management | FEAT-03 | SCR-04 (`/courses/`) | `POST /courses/create` | `courses_bp.create_course` | `Course` | Untested | **Implemented** |
| **FR-004** | Multi-Format Courseware | FEAT-04 | SCR-05 (`/courses/<id>/lessons`) | `POST /courses/<id>/lessons/create` | `courses_bp.add_lesson` | `CourseLesson`, `LessonCourseware` | Untested | **Implemented** |
| **FR-005** | Rise 360 Authoring | FEAT-06 | SCR-06 (`/courses/rise_editor`) | `POST /courses/rise_editor/<id>/save` | `courses_bp.save_rise` | `RiseCoursewareVersion` | Untested | **Implemented** |
| **FR-006** | SCORM Player | FEAT-05 | SCR-07 (`/courses/scorm_player`) | `GET /courses/courseware/<id>/scorm_player` | `scorm_service.py` | `LessonCourseware` | Untested | **Implemented** |
| **FR-007** | Live Class Scheduling | FEAT-07 | SCR-08 (`/classes/`) | `POST /classes/create` | `classes_bp.create_class` | `LiveClass` | Untested | **Implemented** |
| **FR-008** | Real-Time QR Attendance | FEAT-08 | SCR-09, SCR-10 | `GET /attendance/scan/<id>` | `attendance_bp.scan` | `Attendance` | Untested | **Implemented** |
| **FR-009** | Attendance Audit Log | FEAT-09 | SCR-11 (`/attendance/manual`) | `POST /attendance/manual/<id>` | `attendance_bp.manual` | `Attendance`, `AuditLog` | Untested | **Implemented** |
| **FR-010** | Assessment Engine | FEAT-10 | Assessment View | `POST /courses/<id>/assessment` | `assessment_service.py` | `CourseAssessment`, `AssessmentAttempt` | Untested | **Implemented** |
| **FR-011** | PDF Certificate Gen | FEAT-11 | Learner Portal | `GET /certificates/download/<id>` | `pdf_service.py` | `Certificate` | Untested | **Implemented** |
| **FR-012** | Cert Verification | FEAT-12 | SCR-16 (`/certificates/verify`) | `GET /certificates/verify` | `certificates_bp.verify` | `Certificate` | Untested | **Implemented** |
| **FR-013** | Feedback Repository | FEAT-13 | SCR-15 (`/feedback/`) | `POST /feedback/submit/<id>` | `feedback_bp.submit` | `FeedbackRepository`, `FeedbackResponse` | Untested | **Implemented** |
| **FR-014** | Gamification Engine | FEAT-14 | SCR-13 (`/learners/portal`) | Session Hook | `gamification.py` | `Learner`, `LearnerBadge` | Untested | **Implemented** |
| **FR-015** | Social Learning Wall | FEAT-15 | SCR-14 (`/learning_wall/`) | `POST /learning_wall/post` | `learning_wall_bp.index` | `LearningWallPost`, `Reaction`, `Comment` | Untested | **Implemented** |
| **FR-016** | Support Ticketing | FEAT-18 | Learner Portal | `POST /learners/issues/create` | `learners_bp.issues` | `LmsIssue` | Untested | **Implemented** |
| **FR-017** | Learner Excel Import | FEAT-16 | SCR-12 (`/learners/`) | `POST /learners/import` | `learners_bp.import_excel` | `Learner` | Untested | **Implemented** |
| **FR-018** | Manager Team View | FEAT-17 | SCR-13 (My Team) | `GET /learners/portal` | `learners_bp.my_portal` | `Learner.subordinates` | Untested | **Implemented** |
| **FR-019** | Decoupled S3 Storage | FEAT-19 | Backend S3 | `POST /b2/upload` | `b2_service.py` | Cloud Storage Key | Untested | **Implemented** |
| **FR-020** | Super Admin Console | FEAT-20 | SCR-18 (`/super_admin/`) | `GET /super_admin/backup_db` | `super_admin_bp.index` | `AuditLog`, Database file | Untested | **Implemented** |
