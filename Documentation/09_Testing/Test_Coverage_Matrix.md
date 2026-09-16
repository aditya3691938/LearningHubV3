# Learning Hub V3 — Test Coverage Matrix

This matrix documents the automated test coverage status across all feature modules in **Learning Hub V3**.

---

## Module-by-Module Test Coverage Matrix

| Module / Blueprint | Feature | Unit Test Exists | Integration Test Exists | E2E Test Exists | Overall Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `auth_bp` | Admin Login / Logout | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `auth_bp` | Learner Passwordless Login | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `courses_bp` | Course Creation & Management | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `courses_bp` | SCORM Package Player | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `courses_bp` | Rise 360 Block Authoring | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `classes_bp` | Live Class Scheduling | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `attendance_bp` | Real-Time QR Code Scanning | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `attendance_bp` | Manual Attendance & Audit Log | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `certificates_bp` | ReportLab PDF Certificate Gen | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `certificates_bp` | Certificate Verification | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `feedback_bp` | Feedback Survey Engine | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `learning_wall_bp` | Social Wall Posts & Reactions | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `learners_bp` | Learner Directory & Excel Import | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `learners_bp` | Support Ticket Helpdesk | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `super_admin_bp` | DB Backup / Restore / Reset | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |
| `b2_bp` | S3 / Backblaze B2 Upload | ❌ No | ❌ No | ❌ No | **0% (UNTESTED)** |

---

## Untested Critical Functionality Risk Assessment

> [!WARNING]
> High-risk critical paths currently lacking automated test regression coverage:
> 1. **Assessment Grading & Certification Trigger**: Incorrect pass percentage calculations could issue certificates to failing learners.
> 2. **Audit Logging Integrity**: Manual attendance overrides must be guaranteed to log audit entries without silent failures.
> 3. **SCORM Unzipping & Path Traversal**: Untested SCORM zip extraction could lead to directory traversal security risks.
> 4. **Excel Import Parsing**: Malformed Excel rows during learner import could corrupt database tables without schema validation tests.
