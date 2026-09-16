# Learning Hub V3 — Frontend Architecture Document

This document describes the frontend design, layout inheritance, component structure, asset management, and browser interactions in **Learning Hub V3**.

---

## 1. Overview

The frontend of **Learning Hub V3** is constructed using server-side rendered HTML5 templates (Flask Jinja2) augmented with modular CSS stylesheets, Bootstrap 5 UI framework, FontAwesome 6 icons, Chart.js for data visualization, and client-side JavaScript utilities.

---

## 2. Template Structure & Layout Hierarchy

```
app/templates/
├── base.html                     # Root master layout (Navbar, Sidebar, Flash Banners, Modals, Footer)
├── auth/                         # Admin & Learner login pages
│   ├── admin_login.html
│   └── learner_login.html
├── dashboard/                    # Main administrative executive dashboard
│   └── index.html
├── learner_portal/               # Learner Portal layout and tabbed views
│   └── portal.html
├── courses/                      # Course creation, list, detail, lesson editor, Rise builder
│   ├── index.html
│   ├── create.html
│   ├── detail.html
│   ├── rise_editor.html
│   └── scorm_player.html
├── classes/                      # Live class schedule, creation, roster management
│   ├── index.html
│   └── detail.html
├── learners/                     # Learner directory, profile, issue desk
│   ├── index.html
│   ├── profile.html
│   └── issues.html
├── attendance/                   # QR view, camera scanner, manual attendance table
│   ├── qr_view.html
│   ├── scan.html
│   └── manual.html
├── feedback/                     # Feedback repository builder and survey form
│   ├── index.html
│   └── survey.html
├── certificates/                 # Certificate viewer & public verification portal
│   ├── view.html
│   └── verify.html
├── learning_wall/                # Community social wall feed & comment modal
│   └── index.html
├── super_admin/                  # Super admin system operations console
│   └── index.html
└── errors/                       # Custom HTTP 404, 500, 413 error templates
    ├── 404.html
    └── 500.html
```

---

## 3. Component Architecture & Master Layout (`base.html`)

The master layout `base.html` provides standard shell elements:
1. **Global Header / Top Navigation**: Displays branding logo, global Search bar, Notification Bell dropdown (with real-time unread counter), Gamification Points pill, Learner Profile picture/avatar, and Theme Switcher.
2. **Sidebar Navigation**: Role-aware dynamic menu rendering distinct navigation links for Admin (`/dashboard`, `/courses`, `/classes`, `/learners`, `/attendance`, `/feedback`, `/certificates`, `/reports`, `/quizzes`, `/learning_wall`, `/super_admin`) and Learner (`/learners/portal`, `/learning_wall`).
3. **Flash Message Toast Banners**: Rendered dynamically from Flask's `get_flashed_messages()` with alert levels (`success`, `danger`, `warning`, `info`).
4. **Modal Containers**: Reusable HTML modals for profile picture upload, issue ticketing, feedback survey popups, and confirmation dialogs.

---

## 4. Theme System & Dynamic Styling

The UI supports a dynamic theme engine initialized via global Jinja context processors (`inject_global_vars()` in `app/__init__.py`):
- Default theme variant: `navy` (deep dark blue navbar headers, sleek card borders, glassmorphic accents).
- Theme preferences are saved per learner in `Learner.theme` and synced to `session['learner_theme']`.
- Custom CSS utility classes format badges (`bg-teal-subtle text-teal`), progress bars, and stats widgets.

---

## 5. Key Client-Side JavaScript Libraries

| Library | Version / Source | Purpose in Application |
| :--- | :--- | :--- |
| **Bootstrap 5** | CDN JS / CSS bundle | Grid layout, responsive modals, collapse toggles, dropdowns |
| **FontAwesome 6** | CDN icon fonts | Comprehensive UI icons for badges, course modes, and menu items |
| **Chart.js** | CDN script | Renders interactive analytics charts on `/dashboard` and `/reports` |
| **Html5-QRCode Scanner** | CDN JS plugin | Camera access utility for reading attendance QR codes on `/attendance/scan` |
| **QRCode.js** | CDN script | Client-side QR rendering backup for live class session codes |
