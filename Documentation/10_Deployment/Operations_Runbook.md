# Learning Hub V3 — Operations & Maintenance Runbook

This runbook provides system administrators and L&D operations teams with blueprints to monitor, maintain, backup, troubleshoot, and scale **Learning Hub V3**.

---

## 1. System Control Commands

### Start System Server (Development)
```bash
python run.py
```

### Start System Server (Production - Waitress)
```bash
set FLASK_ENV=production
python run.py
```

### Stop System Server
Press `Ctrl + C` in console or terminate WSGI process (`taskkill /F /IM python.exe` on Windows).

---

## 2. Database Backup & Disaster Recovery

### 2.1 Database Backup via Super Admin Web Console
1. Log in as Super Admin (`/login`).
2. Navigate to `http://localhost:5000/super_admin/`.
3. Click **"Download Database Backup"**.
4. System serves a downloadable archive of `lms.db`.

### 2.2 Manual File Backup (SQLite)
```bash
cp lms.db backups/lms_backup_$(date +%Y%m%d_%H%M%S).db
```

### 2.3 Database Disaster Recovery (Restore)
1. Stop Flask WSGI server.
2. Replace corrupt `lms.db` with latest backup file.
3. Restart server (`python run.py`).

---

## 3. High-Scale Storage Decoupling Blueprint (MinIO & Backblaze B2)

To prevent server storage exhaustion when streaming video and SCORM packages to 60,000+ learners:

### Self-Hosted MinIO Container Setup
```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -v /mnt/data:/data \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=<configured_secure_password>" \
  minio/minio server /data --console-address ":9001"
```

Configure `.env`:
```env
STORAGE_PROVIDER=s3
S3_ACCESS_KEY=admin
S3_SECRET_KEY=<configured_secure_password>
S3_ENDPOINT_URL=http://localhost:9000
S3_BUCKET=narayana-lms
```

---

## 4. Log Inspection & Monitoring

- **Flask Console Output**: Log messages are output directly to stdout/stderr.
- **Audit Logs Table**: All administrative roster unlocks and manual attendance updates are stored in table `audit_logs` and viewable under `http://localhost:5000/super_admin/`.
