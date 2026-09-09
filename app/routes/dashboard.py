from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, date
from app.models import db
from app.models.course import Course
from app.models.live_class import LiveClass, AuditLog
from app.models.user import Learner
from app.models.issue import LmsIssue
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.services.lock_service import check_and_auto_lock_classes

from app.utils.decorators import admin_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@admin_required
def index():

    # Auto-lock check on load
    check_and_auto_lock_classes()

    today = date.today()
    current_month_start = date(today.year, today.month, 1)

    # Core Metrics
    total_courses = Course.query.count()
    self_paced_courses = Course.query.filter_by(mode='Self Paced').count()
    live_courses = Course.query.filter(Course.mode.in_(['Live In Person', 'Live Online', 'Live'])).count()
    
    total_classes = LiveClass.query.count()
    upcoming_classes_query = LiveClass.query.filter(LiveClass.class_date >= today).order_by(LiveClass.class_date.asc())
    upcoming_classes_count = upcoming_classes_query.count()
    upcoming_classes_list = upcoming_classes_query.limit(5).all()

    total_learners = Learner.query.count()
    certificates_count = Certificate.query.count()

    # Attendance Percentage Calculation
    total_attendances = Attendance.query.count()
    present_attendances = Attendance.query.filter(Attendance.status.in_(['Present', 'Late'])).count()
    attendance_pct = round((present_attendances / total_attendances * 100.0), 1) if total_attendances > 0 else 0.0

    # Facilitation Credits Calculation
    all_classes = LiveClass.query.all()
    overall_facilitator_hours = sum(c.duration_hours for c in all_classes)
    overall_co_facilitator_hours = sum(c.duration_hours for c in all_classes if c.co_facilitator_id)

    current_month_classes = LiveClass.query.filter(LiveClass.class_date >= current_month_start).all()
    current_month_hours = sum(c.duration_hours for c in current_month_classes)

    # Recent Audit Activities
    recent_activities = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(6).all()
    

    return render_template(
        'dashboard/index.html',
        total_courses=total_courses,
        self_paced_courses=self_paced_courses,
        live_courses=live_courses,
        total_classes=total_classes,
        upcoming_classes_count=upcoming_classes_count,
        upcoming_classes_list=upcoming_classes_list,
        total_learners=total_learners,
        attendance_pct=attendance_pct,
        certificates_count=certificates_count,
        overall_facilitator_hours=overall_facilitator_hours,
        overall_co_facilitator_hours=overall_co_facilitator_hours,
        current_month_hours=current_month_hours,
        recent_activities=recent_activities
    )


@dashboard_bp.route('/admin-profile', methods=['GET', 'POST'])
@admin_required
def admin_profile():
    from app.models.course import Course
    from app.models.user import Learner, AdminUser
    from app.models.issue import LmsIssue
    from flask import session, request, flash, current_app, redirect, url_for
    from app.models import db
    from datetime import datetime
    import os, uuid
    from werkzeug.utils import secure_filename

    total_courses = Course.query.count()
    total_learners = Learner.query.count()
    open_tickets = LmsIssue.query.filter_by(status='Open').count()

    admin = AdminUser.query.filter_by(username=session.get('admin_username')).first()

    if request.method == 'POST' and admin:
        dob_str = request.form.get('date_of_birth')
        profile_pic = request.files.get('profile_picture')
        
        updated = False
        if dob_str:
            try:
                admin.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
                updated = True
                # Check for birthdays
                from app.services.learning_wall_service import check_and_generate_birthday_posts
                check_and_generate_birthday_posts()
            except ValueError:
                flash("Invalid Date Format. Please try again.", "danger")
                
        if profile_pic and profile_pic.filename:
            ext = os.path.splitext(profile_pic.filename)[1]
            pic_filename = f"admin_{admin.id}_{uuid.uuid4().hex[:8]}{ext}"
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
            os.makedirs(upload_dir, exist_ok=True)
            profile_pic.save(os.path.join(upload_dir, pic_filename))
            admin.profile_picture = pic_filename
            updated = True
            
        if updated:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('dashboard.admin_profile'))


    return render_template(
        'dashboard/admin_profile.html',
        total_courses=total_courses,
        total_learners=total_learners,
        open_tickets=open_tickets,
        admin=admin
    )

@dashboard_bp.route('/issues')
@admin_required
def list_issues():
    from app.models.issue import LmsIssue
    issues = LmsIssue.query.order_by(LmsIssue.created_at.desc()).all()
    return render_template('dashboard/issues.html', issues=issues)


@dashboard_bp.route('/broadcast_notification', methods=['POST'])
@admin_required
def broadcast_notification():
    from app.models.notification import LearnerNotification
    from app.models.user import Learner
    from flask import request, flash, redirect, url_for
    from app.models import db
    
    audience = request.form.get('audience', 'all')
    title = request.form.get('title', '').strip()
    message = request.form.get('message', '').strip()
    
    if not title or not message:
        flash("Title and Message are required.", "danger")
        return redirect(url_for('dashboard.index'))
        
    image_path = None
    image_file = request.files.get('image')
    if image_file and image_file.filename:
        from werkzeug.utils import secure_filename
        import uuid
        import os
        from flask import current_app
        filename = secure_filename(image_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'notifications')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        image_file.save(file_path)
        image_path = f"uploads/notifications/{unique_filename}"

    if audience == 'specific':
        raw_gids = request.form.get('global_id', '')
        gids = [g.strip() for g in raw_gids.replace('\r', '\n').split('\n') if g.strip()]
        
        if not gids:
            flash("Please provide at least one Global ID.", "danger")
            return redirect(url_for('dashboard.index'))
            
        success_count = 0
        not_found = []
        for gid in gids:
            learner = Learner.query.filter_by(global_id=gid).first()
            if not learner:
                not_found.append(gid)
                continue
            
            notif = LearnerNotification(
                learner_id=learner.id,
                title=title,
                message=message,
                notification_type='SYSTEM_UPDATE',
                image_path=image_path
            )
            db.session.add(notif)
            success_count += 1
            
        db.session.commit()
        if success_count > 0:
            flash(f"Notification sent to {success_count} learner(s) successfully.", "success")
        if not_found:
            flash(f"Could not find learners for the following Global IDs: {', '.join(not_found)}", "warning")
    else:
        # Broadcast to all learners
        learners = Learner.query.all()
        for learner in learners:
            notif = LearnerNotification(
                learner_id=learner.id,
                title=title,
                message=message,
                notification_type='SYSTEM_UPDATE',
                image_path=image_path
            )
            db.session.add(notif)
        db.session.commit()
        flash(f"Notification broadcasted to all {len(learners)} learners successfully.", "success")
        
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/issues/resolve/<int:issue_id>', methods=['POST'])
@admin_required
def resolve_issue(issue_id):
    from app.models.issue import LmsIssue
    from app.models.notification import LearnerNotification
    from datetime import datetime, timedelta
    from flask import flash
    
    issue = LmsIssue.query.get_or_404(issue_id)
    issue.status = 'Resolved'
    issue.resolved_at = datetime.utcnow()
    
    # Auto-grant extension if it's a manager fallback escalation ticket
    extension_msg = ""
    if issue.description and '[Escalation] Extension requested for course' in issue.description:
        import re
        match = re.search(r'Enrollment ID:\s*(\d+)', issue.description)
        if match:
            enrollment_id = int(match.group(1))
            from app.models.enrollment import LearnerEnrollment
            enrollment = LearnerEnrollment.query.get(enrollment_id)
            if enrollment:
                enrollment.extended_deadline = datetime.utcnow() + timedelta(days=30)
                enrollment.extension_requested = False
                extension_msg = f" Also granted a 30-day course extension for '{enrollment.course.name}'."
    
    # Notify learner
    notif = LearnerNotification(
        learner_id=issue.learner_id,
        title="Support Issue Resolved! ✅",
        message=f"Your support ticket #{issue.id} regarding '{issue.category}' has been marked as resolved by the Administrator.{extension_msg} Let us know if you need anything else!",
        notification_type='SYSTEM_UPDATE'
    )
    db.session.add(notif)
    db.session.commit()
    
    flash(f"Support issue #{issue.id} marked as resolved, and learner notified.{extension_msg}", "success")
    return redirect(url_for('dashboard.list_issues'))
