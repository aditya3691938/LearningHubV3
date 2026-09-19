from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure registration for db.create_all() and migrations
from app.models.user import AdminUser, Learner
from app.models.course import Course, CourseLesson, CourseAssessment, LessonCourseware, CoursewareAudioTrack, CourseMaterial, RiseCoursewareVersion, LearnerBlockProgress
from app.models.live_class import LiveClass, AuditLog
from app.models.enrollment import LearnerEnrollment, AssessmentAttempt, LessonReview
from app.models.badge import LearnerBadge
from app.models.feedback import FeedbackRepository, FeedbackQuestion, FeedbackResponse
from app.models.learning_wall import LearningWallPost, LearningWallReaction
from app.models.notification import LearnerNotification
from app.models.issue import LmsIssue
from app.models.external_certificate import ExternalCertificate
from app.models.quiz import Quiz, QuizQuestion

def ensure_db_schema_integrity():
    """
    Safely ensures new columns exist in PostgreSQL/SQLite for dynamic model schema additions.
    """
    from sqlalchemy import text
    # 1. external_certificates missing columns
    try:
        db.session.execute(text("ALTER TABLE external_certificates ADD COLUMN IF NOT EXISTS expiry_date DATE"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE external_certificates ADD COLUMN IF NOT EXISTS ocr_validated BOOLEAN DEFAULT TRUE"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    # 2. lms_issues missing columns
    try:
        db.session.execute(text("ALTER TABLE lms_issues ADD COLUMN IF NOT EXISTS admin_comment TEXT"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE lms_issues ADD COLUMN IF NOT EXISTS image_path VARCHAR(255)"))
        db.session.commit()
    except Exception:
        db.session.rollback()

