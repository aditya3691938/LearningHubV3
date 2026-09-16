# Learning Hub V3 — Product Vision & Concept Documentation

> [!IMPORTANT]
> **RECONSTRUCTED FROM IMPLEMENTATION**: Original requirement documents were not present in the repository. The vision, problem statement, scope, and target user profiles contained in this document have been factually reconstructed based strictly on the implemented codebase and application behavior.

---

## 1. Reconstructed Product Vision

**Learning Hub V3** is an enterprise Learning & Development (L&D) platform engineered to manage, deliver, and track corporate and academic training programs for large organizations (designed to scale up to 60,000+ active learners). 

The product bridges self-paced digital learning (video content, SCORM packages, interactive Rise 360 block modules, PPTX slides) with structured live classroom training (in-person campus workshops and online virtual sessions via Google Meet). It combines real-time attendance tracking (QR code scanning), automated certificate issuance, gamified engagement (points, badges, streak tracking), social community interaction (Learning Wall), and administrative operations (roster management, feedback surveys, helpdesk support ticketing).

---

## 2. Problem Statement

Large educational and enterprise institutions face critical challenges in operationalizing staff and faculty development:
1. **Fragmented Learning Delivery**: Inability to manage self-paced digital modules alongside physical campus workshops in a single platform.
2. **Attendance & Verification Overhead**: Manual paper-based attendance tracking for live sessions creates data entry delays, ghost attendance, and audit failures.
3. **Engagement Drop-off**: Lack of interactive feedback loops, gamification incentives, and peer recognition leads to low course completion rates.
4. **Infrastructure Bottlenecks**: Traditional monolithic LMS platforms incur exorbitant storage and egress bandwidth costs when streaming high-definition video and interactive materials to tens of thousands of simultaneous learners.

---

## 3. Target Users

Based on codebase models and database initializations (`app/seed.py`), the target audience comprises:
1. **L&D Administrators & Academic Directors**: Operational leaders managing curriculum, scheduling live classes, monitoring completion compliance, and generating audit reports.
2. **Learners / Faculty Members / Staff**: Enterprise employees (e.g. Lecturers, Professors, Instructional Designers, Managers across academic departments like Mathematics, Physics, Chemistry, CS, Engineering) taking self-paced or mandatory live training.
3. **Session Facilitators / Instructors**: Trainers conducting live online or campus sessions who need to track live attendance and collect session feedback.
4. **People Managers / Department Heads**: Managers monitoring direct reports' course progress and compliance matrices.
5. **System Administrators / DevOps Engineers**: System maintainers managing platform health, database migration, storage decoupling, and backups.

---

## 4. Business Objective

- **Standardize L&D Operations**: Centralize training administration across multiple geographical campuses (e.g., Hyderabad, Bangalore, Chennai, Pune) and local branches.
- **Cost-Optimized Scale**: Support 60,000+ active learners using low-cost cloud architecture (decoupled MinIO / Backblaze B2 storage, SQLite WAL mode / PostgreSQL, Cloudflare CDN).
- **Automate Compliance & Certification**: Seamlessly issue verifiable PDF certificates upon passing required post-assessments and feedback surveys.

---

## 5. Product Scope

### In-Scope (Implemented Features)
- **Multi-Mode Learning Management**: Self-Paced digital courses, Live Online classes (Google Meet links), and Live In-Person campus sessions.
- **Rich Courseware Support**: Embedded YouTube videos, non-downloadable materials, SCORM package player, PPTX slide rendering, and Rise 360 interactive block content.
- **Real-Time Attendance Engine**: Dual-mode attendance via automated QR code scanning (facilitator view / learner scan) and manual admin override with audit logging.
- **Assessment & Quiz Engine**: Pre-assessments, lesson post-assessments, course-end assessments, and standalone quizzes with configurable pass thresholds (default 80%).
- **Gamification & Social Engagement**: Daily login streak tracking, point accrual, badge distribution (`Streak Master 🔥`, `Fast Learner`), and interactive social Learning Wall (reactions, comments, birthday notices).
- **Feedback & Support**: Flexible feedback questionnaire repositories, session survey submission, and integrated L&D support ticket system.
- **Decoupled Object Storage**: Configurable local storage fallback or S3-compatible cloud storage (Backblaze B2 / MinIO).
- **Super Admin Operations**: System backup/restore, audit trail logging, and database resets.

### Out of Scope (Not Available / Cannot Be Determined)
- E-commerce / Course Monetization / Payment Gateway Integration
- Real-time video conferencing hosting built into the platform (relies on external links like Google Meet)
- Enterprise Single Sign-On (SSO / SAML 2.0 / OAuth2) — *Learner login currently uses passwordless Global ID; Google SSO commented in code as future phase*.
- Mobile Native Apps (iOS/Android) — *Platform is built as a responsive web app*.

---

## 6. User Roles Summary

| Role Name | Access Scope | Key Responsibilities |
| :--- | :--- | :--- |
| **Super Administrator** | Platform Management | Storage provider configuration, DB backups, audit trail inspection, database resets. |
| **L&D Administrator** | Full LMS Admin | Course creation, live class scheduling, roster management, quiz setup, report export. |
| **Learner** | Learner Portal | Course consumption, assessment submission, QR attendance scan, badge/cert collection. |
| **Facilitator** | Class Management | Class roster management, QR code seating display, live attendance marking. |
| **Manager** | Team Tracking | Views progress, completion rates, and extension requests of direct subordinates. |

---

## 7. High-Level User Journeys

### Journey 1: Learner Self-Paced Training Flow
```
Learner Login (Global ID) → Learner Portal → Select Self-Paced Course → Watch Video / View Courseware → Take Lesson Assessment → Pass Assessment (≥80%) → Complete Feedback Survey → Generate & Download PDF Certificate
```

### Journey 2: Live In-Person Class & QR Attendance Flow
```
Admin Schedules Live Class → Learner Enrolls → Facilitator Displays Class QR Code → Learner Scans QR Code via Mobile → Attendance Marked 'Present' → Facilitator Locks Class Roster
```

---

## 8. Success Criteria

1. **Zero-Downtime Multi-Mode Delivery**: Reliable streaming of learning materials across high-concurrency periods.
2. **Attendance Verification Speed**: QR scanning speed under 2 seconds per learner.
3. **Automated Certificate Delivery**: Instant PDF rendering upon passing post-assessment and feedback submission.
4. **Data Integrity**: Complete audit trail logging for manual attendance overrides and roster unlocks.
