# Learning Hub V3 — Technical Debt Assessment

This document identifies architectural concerns, missing validation, hardcoded values, deprecated patterns, and maintainability concerns in **Learning Hub V3**.

---

## 1. Architectural & Code Quality Assessment

### 1.1 Large Controller Files
- **Concern**: `app/routes/courses.py` contains **100,532 bytes** of code across a single file handling course CRUD, lesson editing, Rise 360 block parsing, SCORM unzipping, assessment evaluation, and certificate triggers.
- **Impact**: Poor separation of concerns; high risk of merge conflicts and difficulty in maintaining route handlers.
- **Recommendation**: Refactor `courses.py` into separate blueprint controllers (`course_crud.py`, `courseware.py`, `scorm.py`, `rise.py`).

### 1.2 `app/routes/learners.py` Bloat
- **Concern**: `app/routes/learners.py` contains **70,614 bytes** handling learner profiles, Excel import/export via pandas, team management, external certificate uploads, and support ticketing.
- **Recommendation**: Extract Excel import/export logic into `app/services/excel_service.py` and ticket desk into `app/routes/issues.py`.

### 1.3 Schema Modification Logic in `app/seed.py`
- **Concern**: `app/seed.py` contains 28 inline raw SQL `ALTER TABLE` statements (L23-52) executed on every app startup wrapped in try/except blocks to bypass missing column errors.
- **Impact**: Non-standard database schema migration practice bypassing Alembic tracking.
- **Recommendation**: Remove raw alter statements from seed code and rely strictly on standard `flask db migrate` and `flask db upgrade`.

---

## 2. Hardcoded Values & Magic Constants

1. **Default Pass Percentage**: Hardcoded to 80% across models (`Course`, `Quiz`) and seed functions.
2. **Maximum Assessment Attempts**: Hardcoded to 3 attempts in `LearnerEnrollment.attempts_count`.
3. **Hardcoded Upload Paths**: Direct path joins scattered across routes instead of centralized path helpers.
