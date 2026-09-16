# Learning Hub V3 — Operational Troubleshooting Guide

This document lists common operational issues, error codes, root causes, and step-by-step resolution procedures for **Learning Hub V3**.

---

## Troubleshooting Decision Matrix

| Issue Code | Symptoms | Root Cause | Resolution Procedure |
| :--- | :--- | :--- | :--- |
| **ERR-01** | `sqlite3.OperationalError: database is locked` | High concurrent write transactions locking SQLite file. | Ensure SQLite is running in WAL mode (`PRAGMA journal_mode=WAL`). For >500 active concurrent users, migrate to PostgreSQL by updating `DATABASE_URL` in `.env`. |
| **ERR-02** | HTTP 413 "The uploaded file is too large" | Uploaded file size exceeds 1 GB limit. | Check uploaded file size. If larger than 1 GB, compress video or upload via S3/B2 storage endpoint directly. |
| **ERR-03** | SCORM package fails to load inside iframe | Missing `imsmanifest.xml` or corrupted ZIP structure. | Verify SCORM package ZIP contains valid `imsmanifest.xml` at root directory. Inspect `scorm_service.py` logs. |
| **ERR-04** | QR Attendance scan returns "Class attendance is locked" | Facilitator or admin locked the class roster. | Admin must navigate to `/classes/`, click Unlock Class, and enter mandatory justification reason. |
| **ERR-05** | PDF Certificate fails to generate / download | Missing ReportLab library or template font error. | Verify `reportlab` is installed in virtual environment (`pip install reportlab`). Check `pdf_service.py` console stack trace. |
| **ERR-06** | B2 / S3 upload fails with 403 Forbidden | Expired or incorrect S3 keys in `.env`. | Check `S3_ACCESS_KEY` and `S3_SECRET_KEY` in `.env`. Verify bucket permissions in Backblaze B2 or MinIO console. |
| **ERR-07** | Learner cannot log in (Global ID not found) | Global ID typo or learner profile not imported. | Admin navigates to `/learners/`, verifies learner exists, or imports learner via Excel bulk upload. |
