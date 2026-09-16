# Learning Hub V3 — UI Screen Documentation Inventory

This document provides a screen-by-screen inventory of all accessible user interface screens in **Learning Hub V3**, documenting URLs, user roles, layout components, forms, tables, modals, states, backend dependencies, and screenshot references.

---

## Screen Inventory Summary Table

| Screen ID | Screen Name | Route / URL | Role | Status |
| :--- | :--- | :--- | :--- | :--- |
| **SCR-01** | Admin Login Screen | `/login` | Public / Admin | **Documented** |
| **SCR-02** | Learner Login Screen | `/learner/login` | Public / Learner | **Documented** |
| **SCR-03** | Executive Admin Dashboard | `/dashboard` | Admin | **Documented** |
| **SCR-04** | Course Management Catalog | `/courses/` | Admin | **Documented** |
| **SCR-05** | Course Creation & Edit Form | `/courses/create` | Admin | **Documented** |
| **SCR-06** | Interactive Rise 360 Editor | `/courses/rise_editor/<id>` | Admin | **Documented** |
| **SCR-07** | SCORM Player Iframe Screen | `/courses/courseware/<id>/scorm_player` | Learner | **Documented** |
| **SCR-08** | Live Classes Schedule Roster | `/classes/` | Admin / Facilitator | **Documented** |
| **SCR-09** | Live Class QR Seating Screen | `/attendance/qr_view/<id>` | Facilitator | **Documented** |
| **SCR-10** | Learner Mobile QR Scanner | `/attendance/scan/<id>` | Learner | **Documented** |
| **SCR-11** | Manual Attendance & Audit Screen | `/attendance/manual/<id>` | Admin | **Documented** |
| **SCR-12** | Learner Directory & Import | `/learners/` | Admin | **Documented** |
| **SCR-13** | Main Learner Portal | `/learners/portal` | Learner | **Documented** |
| **SCR-14** | Social Learning Community Wall | `/learning_wall/` | All Users | **Documented** |
| **SCR-15** | Feedback Survey Repository | `/feedback/` | Admin | **Documented** |
| **SCR-16** | Certificate Download & Verification | `/certificates/verify` | Public / Learner | **Documented** |
| **SCR-17** | Executive Reports & Analytics | `/reports/` | Admin | **Documented** |
| **SCR-18** | Super Admin Operations Console | `/super_admin/` | Super Admin | **Documented** |

---

## Detailed Screen Specifications

### SCR-01 — Admin Login Screen
- **Route**: `http://localhost:5000/login`
- **User Role**: Unauthenticated Admin
- **Purpose**: Authenticates L&D administrators.
- **UI Elements**: Centered login card, `Username` text input, `Password` password input, `Sign In` submit button, link to Learner Login.
- **Error States**: Displays red alert banner "Invalid Username or Password".
- **Backend Dependencies**: `auth_bp.admin_login`, `AdminUser.check_password()`.

**Figure 1 — Admin Login Screen**
![Admin Login Screen](../07_UI/Screenshots/admin_login.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-02 — Learner Login Screen
- **Route**: `http://localhost:5000/learner/login`
- **User Role**: Unauthenticated Learner
- **Purpose**: Passwordless authentication for employees/students using Global ID.
- **UI Elements**: Hero banner, `Global ID` text input (supports `10001` or aliases `learner01`-`learner05`), quick login hint pill, `Enter Portal` button.
- **Error States**: Displays alert "Learner with Global ID X not found".
- **Backend Dependencies**: `auth_bp.learner_login`, `gamification.award_points()`.

**Figure 2 — Learner Login Screen**
![Learner Login Screen](../07_UI/Screenshots/learner_login.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-03 — Executive Admin Dashboard
- **Route**: `http://localhost:5000/dashboard`
- **User Role**: L&D Administrator / Super Admin
- **Purpose**: Central command overview of system activity.
- **UI Elements**: Stat widgets (Total Learners, Active Courses, Live Classes Today, Open Support Tickets), Chart.js enrollment trend graph, Recent System Activity feed, Quick action buttons.
- **Backend Dependencies**: `dashboard_bp.index`.

**Figure 3 — Executive Admin Dashboard**
![Admin Dashboard](../07_UI/Screenshots/admin_dashboard.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-04 — Course Management Catalog
- **Route**: `http://localhost:5000/courses/`
- **User Role**: L&D Administrator
- **Purpose**: Manages all course offerings.
- **UI Elements**: Filter bar (All, Self Paced, Live Online, Live In Person), search input, course cards with thumbnail, duration badge, mode tag, pass percentage, action buttons (`Manage Lessons`, `Edit`, `Archive`).
- **Backend Dependencies**: `courses_bp.index`, `Course.query`.

**Figure 4 — Course Management Catalog**
![Course Catalog](../07_UI/Screenshots/courses_catalog.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-08 — Live Classes Schedule Roster
- **Route**: `http://localhost:5000/classes/`
- **User Role**: L&D Administrator / Facilitator
- **Purpose**: Schedules live classes and displays session status.
- **UI Elements**: Class schedule table (Class ID, Name, Date, Mode, Facilitator, Roster Count, Lock Status), `Schedule Class` button, `QR Display` button, `Manual Attendance` button.
- **Backend Dependencies**: `classes_bp.index`, `LiveClass.query`.

**Figure 5 — Live Classes Schedule Roster**
![Live Classes](../07_UI/Screenshots/live_classes.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-09 — Live Class QR Seating Screen
- **Route**: `http://localhost:5000/attendance/qr_view/<class_id>`
- **User Role**: Facilitator
- **Purpose**: Projects live session QR code on classroom display screen for student attendance scanning.
- **UI Elements**: High-contrast QR code image, Class ID badge, Facilitator name, live counter of marked learners.
- **Backend Dependencies**: `attendance_bp.qr_view`, `qr_service.py`.

**Figure 6 — Live Class QR Seating Screen**
![QR Seating Screen](../07_UI/Screenshots/qr_seating.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-13 — Main Learner Portal
- **Route**: `http://localhost:5000/learners/portal`
- **User Role**: Learner
- **Purpose**: Learner's personalized home dashboard.
- **UI Elements**: Streak flame counter (`🔥 5 Days`), Points counter, Badges showcase, Enrolled Courses carousel, "My Team" tab (for managers), Support ticket shortcut.
- **Backend Dependencies**: `learners_bp.my_portal`, `LearnerEnrollment.query`.

**Figure 7 — Main Learner Portal**
![Learner Portal](../07_UI/Screenshots/learner_portal.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-14 — Social Learning Community Wall
- **Route**: `http://localhost:5000/learning_wall/`
- **User Role**: All Logged-in Users
- **Purpose**: Community feed for announcements, birthday wishes, and peer achievements.
- **UI Elements**: Post creation card, social feed posts, reaction buttons (`like`, `love`, `celebrate`, `clap`, `fire`), comment threads, user profile avatars.
- **Backend Dependencies**: `learning_wall_bp.index`.

**Figure 8 — Social Learning Community Wall**
![Learning Wall](../07_UI/Screenshots/learning_wall.png)
*Screenshot unavailable — requires manual capture.*

---

### SCR-18 — Super Admin Operations Console
- **Route**: `http://localhost:5000/super_admin/`
- **User Role**: Super Administrator
- **Purpose**: System-level maintenance and infrastructure management.
- **UI Elements**: DB Backup button, DB Restore file dropzone, System Reset confirmation modal, Storage provider credentials viewer, Audit log table.
- **Backend Dependencies**: `super_admin_bp.index`, `AuditLog.query`.

**Figure 9 — Super Admin Operations Console**
![Super Admin Console](../07_UI/Screenshots/super_admin.png)
*Screenshot unavailable — requires manual capture.*
