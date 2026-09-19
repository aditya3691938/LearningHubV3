import pandas as pd
import io
from datetime import datetime, date
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.models import db
from app.models.course import Course, CourseLesson, LessonCourseware, LearnerBlockProgress
from app.models.live_class import LiveClass
from app.models.user import Learner
from app.models.enrollment import LearnerEnrollment, AssessmentAttempt, LessonReview, NextSessionRequest
from app.models.attendance import Attendance
from app.models.certificate import Certificate
from app.models.feedback import FeedbackResponse, FeedbackRepository

REPORT_TYPES = {
    'master': 'Master Enrollment & Progress',
    'lesson': 'Lesson-Wise & SCORM Activity Audit',
    'class': 'Class Cohort & Attendance Audit',
    'assessment': 'Assessment & Exam Detailed Log',
    'compliance': 'Department Compliance & Summary'
}

MASTER_COLUMNS = {
    'course_name': 'Course Name',
    'class_name': 'Class / Batch Name',
    'global_id': 'Learner Global ID',
    'learner_name': 'Learner Name',
    'department': 'Department',
    'attendance_status': 'Attendance Status',
    'pre_assessment': 'Pre Assessment Score (%)',
    'post_assessment': 'Post Assessment Score (%)',
    'final_score': 'Final Score (%)',
    'completion_status': 'Completion Status',
    'enrolled_date': 'Enrolled Date',
    'completion_date': 'Completion Date',
    'certificate_id': 'Certificate ID',
    'facilitator': 'Facilitator Name',
    'co_facilitator': 'Co-Facilitator Name',
    'duration': 'Duration (Hours)',
    'feedback_status': 'Feedback Submitted'
}

LESSON_COLUMNS = {
    'course_name': 'Course Name',
    'lesson_num': 'Lesson #',
    'lesson_title': 'Lesson Title',
    'courseware_title': 'Courseware / SCORM Title',
    'courseware_type': 'Content Type',
    'global_id': 'Learner Global ID',
    'learner_name': 'Learner Name',
    'department': 'Department',
    'review_status': 'Lesson Review Status',
    'time_spent': 'Time Spent (Mins)',
    'attempts_count': 'Block Attempts',
    'review_date': 'Reviewed On',
    'pre_score': 'Lesson Pre-Quiz Score (%)',
    'post_score': 'Lesson Post-Quiz Score (%)'
}

CLASS_COLUMNS = {
    'class_id_str': 'Class Code',
    'class_name': 'Class / Batch Name',
    'course_name': 'Associated Course',
    'class_mode': 'Class Mode',
    'class_date': 'Scheduled Date',
    'session_time': 'Session Time',
    'facilitator': 'Facilitator',
    'co_facilitator': 'Co-Facilitator',
    'location': 'Branch / Location',
    'global_id': 'Learner Global ID',
    'learner_name': 'Learner Name',
    'department': 'Department',
    'attendance_status': 'Attendance Status',
    'recorded_via': 'Scan / Mark Method',
    'checkin_time': 'Check-In Timestamp',
    'request_status': 'Next Session Request'
}

ASSESSMENT_COLUMNS = {
    'course_name': 'Course Name',
    'assessment_type': 'Exam Type',
    'lesson_title': 'Lesson / Module',
    'global_id': 'Learner Global ID',
    'learner_name': 'Learner Name',
    'department': 'Department',
    'score_pct': 'Score Percentage (%)',
    'passed': 'Pass / Fail Result',
    'attempt_num': 'Attempt #',
    'submitted_at': 'Submission Timestamp'
}

COMPLIANCE_COLUMNS = {
    'department': 'Department Name',
    'total_learners': 'Total Employees',
    'active_enrollments': 'Active Course Enrollments',
    'completed_courses': 'Completed Courses',
    'compliance_rate': 'Compliance Completion Rate (%)',
    'avg_score': 'Average Exam Score (%)',
    'total_hours': 'Learning Hours Delivered',
    'pending_requests': 'Pending Extension Requests'
}

# Backward compatibility alias
ALL_REPORT_COLUMNS = MASTER_COLUMNS


def get_report_columns(report_type='master'):
    """
    Returns column dict key -> title for given report type.
    """
    if report_type == 'lesson':
        return LESSON_COLUMNS
    elif report_type == 'class':
        return CLASS_COLUMNS
    elif report_type == 'assessment':
        return ASSESSMENT_COLUMNS
    elif report_type == 'compliance':
        return COMPLIANCE_COLUMNS
    return MASTER_COLUMNS


def get_report_summary_stats():
    """
    Computes system-wide high level KPI analytics for reporting header cards.
    """
    total_enrollments = LearnerEnrollment.query.count()
    completed_enrollments = LearnerEnrollment.query.filter_by(completion_status='Completed').count()
    completion_rate = round((completed_enrollments / total_enrollments * 100), 1) if total_enrollments > 0 else 0.0

    attempts = AssessmentAttempt.query.all()
    avg_score = round(sum(a.score_percentage for a in attempts) / len(attempts), 1) if attempts else 0.0

    scorm_reviews = LessonReview.query.count() + LearnerBlockProgress.query.filter_by(is_completed=True).count()
    attendance_records = Attendance.query.count()
    present_records = Attendance.query.filter_by(status='Present').count()
    attendance_rate = round((present_records / attendance_records * 100), 1) if attendance_records > 0 else 0.0

    return {
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'completion_rate': completion_rate,
        'avg_score': avg_score,
        'scorm_reviews': scorm_reviews,
        'attendance_records': attendance_records,
        'attendance_rate': attendance_rate
    }


def generate_report_dataframe(
    report_type='master',
    selected_columns=None, 
    search_query=None, 
    mode_filter=None, 
    date_from=None, 
    date_to=None, 
    class_id_filter=None, 
    course_id_filter=None
):
    """
    Queries DB based on report_type, builds flat data records,
    and returns a Pandas DataFrame with selected columns.
    """
    column_map = get_report_columns(report_type)
    if not selected_columns:
        selected_columns = list(column_map.keys())

    sq = (search_query or '').strip().lower()

    if report_type == 'lesson':
        return _generate_lesson_report(selected_columns, sq, mode_filter, date_from, date_to, course_id_filter)
    elif report_type == 'class':
        return _generate_class_report(selected_columns, sq, mode_filter, date_from, date_to, class_id_filter, course_id_filter)
    elif report_type == 'assessment':
        return _generate_assessment_report(selected_columns, sq, mode_filter, date_from, date_to, course_id_filter)
    elif report_type == 'compliance':
        return _generate_compliance_report(selected_columns, sq)
    else:
        return _generate_master_report(selected_columns, sq, mode_filter, date_from, date_to, class_id_filter, course_id_filter)


def _generate_master_report(selected_columns, sq, mode_filter, date_from, date_to, class_id_filter, course_id_filter):
    enrollments = LearnerEnrollment.query.all()
    rows = []

    for en in enrollments:
        learner = en.learner
        course = en.course
        live_cls = en.live_class

        if not learner or not course:
            continue

        if sq:
            match = (
                sq in course.name.lower() or
                sq in (learner.global_id or '').lower() or
                sq in (learner.name or '').lower() or
                sq in (learner.department or '').lower() or
                (live_cls and sq in (live_cls.class_name or '').lower())
            )
            if not match:
                continue

        if mode_filter and mode_filter != 'ALL':
            if course.mode != mode_filter:
                continue

        if course_id_filter and course_id_filter != 'ALL':
            if str(course.id) != str(course_id_filter):
                continue

        if class_id_filter and class_id_filter != 'ALL':
            if not live_cls or str(live_cls.id) != str(class_id_filter):
                continue

        if date_from and en.assigned_at and en.assigned_at.date() < date_from:
            continue
        if date_to and en.assigned_at and en.assigned_at.date() > date_to:
            continue

        att_status = 'N/A'
        if live_cls:
            att = Attendance.query.filter_by(class_id=live_cls.id, learner_id=learner.id).first()
            att_status = att.status if att else 'Absent'

        pre_attempt = AssessmentAttempt.query.filter_by(enrollment_id=en.id, assessment_type='PRE').order_by(AssessmentAttempt.id.desc()).first()
        post_attempt = AssessmentAttempt.query.filter_by(enrollment_id=en.id, assessment_type='POST').order_by(AssessmentAttempt.id.desc()).first()

        pre_score = f"{pre_attempt.score_percentage}%" if pre_attempt else "N/A"
        post_score = f"{post_attempt.score_percentage}%" if post_attempt else "N/A"

        cert = Certificate.query.filter_by(learner_id=learner.id, course_id=course.id).first()
        cert_id = cert.certificate_id if cert else "None"

        fb_resp = None
        if live_cls and live_cls.feedback_repo_id:
            fb_resp = FeedbackResponse.query.filter_by(class_id=live_cls.id, learner_id=learner.id).first()
        fb_status = "Yes" if fb_resp else "No"

        row = {
            'course_name': course.name,
            'class_name': live_cls.class_name if live_cls else 'Self-Paced (N/A)',
            'global_id': learner.global_id or 'N/A',
            'learner_name': learner.name or 'N/A',
            'department': learner.department or 'N/A',
            'attendance_status': att_status,
            'pre_assessment': pre_score,
            'post_assessment': post_score,
            'final_score': f"{en.final_score}%" if en.final_score is not None else 'N/A',
            'completion_status': en.completion_status,
            'enrolled_date': en.assigned_at.strftime('%d-%b-%Y') if en.assigned_at else 'N/A',
            'completion_date': en.completion_date.strftime('%d-%b-%Y') if en.completion_date else 'N/A',
            'certificate_id': cert_id,
            'facilitator': live_cls.facilitator_name if live_cls else 'N/A',
            'co_facilitator': live_cls.co_facilitator_name if (live_cls and live_cls.co_facilitator_name) else 'N/A',
            'duration': f"{course.duration_hours} hrs",
            'feedback_status': fb_status
        }
        rows.append(row)

    return _format_dataframe(rows, selected_columns, MASTER_COLUMNS)


def _generate_lesson_report(selected_columns, sq, mode_filter, date_from, date_to, course_id_filter):
    lessons = CourseLesson.query.all()
    rows = []

    for lesson in lessons:
        course = lesson.course
        if not course:
            continue

        if mode_filter and mode_filter != 'ALL' and course.mode != mode_filter:
            continue

        if course_id_filter and course_id_filter != 'ALL' and str(course.id) != str(course_id_filter):
            continue

        courseware_items = lesson.courseware or [None]
        enrollments = LearnerEnrollment.query.filter_by(course_id=course.id).all()

        for cw in courseware_items:
            cw_title = cw.title if cw else 'N/A'
            cw_type = cw.courseware_type if cw else 'Text'

            for en in enrollments:
                learner = en.learner
                if not learner:
                    continue

                if sq:
                    match = (
                        sq in course.name.lower() or
                        sq in lesson.title.lower() or
                        sq in cw_title.lower() or
                        sq in (learner.name or '').lower() or
                        sq in (learner.global_id or '').lower() or
                        sq in (learner.department or '').lower()
                    )
                    if not match:
                        continue

                if date_from and en.assigned_at and en.assigned_at.date() < date_from:
                    continue
                if date_to and en.assigned_at and en.assigned_at.date() > date_to:
                    continue

                # Check lesson review
                rev = LessonReview.query.filter_by(enrollment_id=en.id, lesson_id=lesson.id).first()
                rev_status = 'Reviewed' if rev else 'Pending'
                rev_date = rev.reviewed_at.strftime('%d-%b-%Y %H:%M') if rev else 'N/A'

                # Check block progress if SCORM/Rise
                time_mins = 'N/A'
                attempts = 0
                if cw:
                    blk_prog = LearnerBlockProgress.query.filter_by(learner_id=learner.id, courseware_id=cw.id).all()
                    if blk_prog:
                        total_sec = sum(b.time_spent_seconds for b in blk_prog)
                        time_mins = f"{round(total_sec / 60.0, 1)}"
                        attempts = sum(b.attempts_count for b in blk_prog)
                        if any(b.is_completed for b in blk_prog):
                            rev_status = 'Completed (SCORM)'

                # Check lesson assessments
                pre_att = AssessmentAttempt.query.filter_by(enrollment_id=en.id, lesson_id=lesson.id, assessment_type='LESSON_PRE').order_by(AssessmentAttempt.id.desc()).first()
                post_att = AssessmentAttempt.query.filter_by(enrollment_id=en.id, lesson_id=lesson.id, assessment_type='LESSON_POST').order_by(AssessmentAttempt.id.desc()).first()

                row = {
                    'course_name': course.name,
                    'lesson_num': f"Lesson {lesson.lesson_number}",
                    'lesson_title': lesson.title,
                    'courseware_title': cw_title,
                    'courseware_type': cw_type,
                    'global_id': learner.global_id or 'N/A',
                    'learner_name': learner.name or 'N/A',
                    'department': learner.department or 'N/A',
                    'review_status': rev_status,
                    'time_spent': time_mins,
                    'attempts_count': attempts,
                    'review_date': rev_date,
                    'pre_score': f"{pre_att.score_percentage}%" if pre_att else 'N/A',
                    'post_score': f"{post_att.score_percentage}%" if post_att else 'N/A'
                }
                rows.append(row)

    return _format_dataframe(rows, selected_columns, LESSON_COLUMNS)


def _generate_class_report(selected_columns, sq, mode_filter, date_from, date_to, class_id_filter, course_id_filter):
    classes = LiveClass.query.all()
    rows = []

    for live_cls in classes:
        course = live_cls.course
        if not course:
            continue

        if mode_filter and mode_filter != 'ALL' and course.mode != mode_filter:
            continue

        if course_id_filter and course_id_filter != 'ALL' and str(course.id) != str(course_id_filter):
            continue

        if class_id_filter and class_id_filter != 'ALL' and str(live_cls.id) != str(class_id_filter):
            continue

        enrollments = LearnerEnrollment.query.filter_by(class_id=live_cls.id).all()
        for en in enrollments:
            learner = en.learner
            if not learner:
                continue

            if sq:
                match = (
                    sq in live_cls.class_name.lower() or
                    sq in (live_cls.class_id or '').lower() or
                    sq in course.name.lower() or
                    sq in (learner.name or '').lower() or
                    sq in (learner.global_id or '').lower() or
                    sq in (learner.department or '').lower()
                )
                if not match:
                    continue

            if date_from and live_cls.class_date and live_cls.class_date < date_from:
                continue
            if date_to and live_cls.class_date and live_cls.class_date > date_to:
                continue

            att = Attendance.query.filter_by(class_id=live_cls.id, learner_id=learner.id).first()
            att_status = att.status if att else 'Absent'
            recorded_via = att.recorded_via if att else 'N/A'
            checkin_time = att.timestamp.strftime('%d-%b-%Y %H:%M') if (att and att.timestamp) else 'N/A'

            sess_req = NextSessionRequest.query.filter_by(enrollment_id=en.id).order_by(NextSessionRequest.id.desc()).first()
            req_status = sess_req.status if sess_req else ('Missed Class' if att_status == 'Absent' else 'None')

            row = {
                'class_id_str': live_cls.class_id or 'N/A',
                'class_name': live_cls.class_name,
                'course_name': course.name,
                'class_mode': live_cls.class_mode or 'Online',
                'class_date': live_cls.class_date.strftime('%d-%b-%Y') if live_cls.class_date else 'N/A',
                'session_time': live_cls.session_time or 'N/A',
                'facilitator': live_cls.facilitator_name or 'N/A',
                'co_facilitator': live_cls.co_facilitator_name or 'N/A',
                'location': live_cls.location or (live_cls.meet_link if live_cls.class_mode == 'Online' else 'N/A'),
                'global_id': learner.global_id or 'N/A',
                'learner_name': learner.name or 'N/A',
                'department': learner.department or 'N/A',
                'attendance_status': att_status,
                'recorded_via': recorded_via,
                'checkin_time': checkin_time,
                'request_status': req_status
            }
            rows.append(row)

    return _format_dataframe(rows, selected_columns, CLASS_COLUMNS)


def _generate_assessment_report(selected_columns, sq, mode_filter, date_from, date_to, course_id_filter):
    attempts = AssessmentAttempt.query.order_by(AssessmentAttempt.id.desc()).all()
    rows = []

    for att in attempts:
        en = att.enrollment
        if not en:
            continue
        learner = en.learner
        course = en.course
        if not learner or not course:
            continue

        if mode_filter and mode_filter != 'ALL' and course.mode != mode_filter:
            continue

        if course_id_filter and course_id_filter != 'ALL' and str(course.id) != str(course_id_filter):
            continue

        if sq:
            match = (
                sq in course.name.lower() or
                sq in att.assessment_type.lower() or
                sq in (learner.name or '').lower() or
                sq in (learner.global_id or '').lower() or
                sq in (learner.department or '').lower()
            )
            if not match:
                continue

        if date_from and att.submitted_at and att.submitted_at.date() < date_from:
            continue
        if date_to and att.submitted_at and att.submitted_at.date() > date_to:
            continue

        lesson_title = 'Course-Level'
        if att.lesson_id:
            l_obj = CourseLesson.query.get(att.lesson_id)
            if l_obj:
                lesson_title = f"Lesson {l_obj.lesson_number}: {l_obj.title}"

        row = {
            'course_name': course.name,
            'assessment_type': att.assessment_type,
            'lesson_title': lesson_title,
            'global_id': learner.global_id or 'N/A',
            'learner_name': learner.name or 'N/A',
            'department': learner.department or 'N/A',
            'score_pct': f"{att.score_percentage}%",
            'passed': 'PASSED' if att.passed else 'FAILED',
            'attempt_num': f"Attempt #{att.attempt_number}",
            'submitted_at': att.submitted_at.strftime('%d-%b-%Y %H:%M') if att.submitted_at else 'N/A'
        }
        rows.append(row)

    return _format_dataframe(rows, selected_columns, ASSESSMENT_COLUMNS)


def _generate_compliance_report(selected_columns, sq):
    learners = Learner.query.all()
    dept_map = {}

    for l in learners:
        d = l.department or 'General L&D'
        if sq and sq not in d.lower():
            continue
        if d not in dept_map:
            dept_map[d] = {
                'total_learners': 0,
                'active_enrollments': 0,
                'completed_courses': 0,
                'scores': [],
                'total_hours': 0.0,
                'pending_requests': 0
            }

        dept_map[d]['total_learners'] += 1
        enrolls = LearnerEnrollment.query.filter_by(learner_id=l.id).all()
        dept_map[d]['active_enrollments'] += len(enrolls)

        for en in enrolls:
            if en.completion_status == 'Completed':
                dept_map[d]['completed_courses'] += 1
                if en.course:
                    dept_map[d]['total_hours'] += (en.course.duration_hours or 1.0)
            if en.final_score is not None:
                dept_map[d]['scores'].append(en.final_score)
            
            p_req = NextSessionRequest.query.filter_by(enrollment_id=en.id, status='Pending').count()
            dept_map[d]['pending_requests'] += p_req

    rows = []
    for dept_name, data in dept_map.items():
        tot_e = data['active_enrollments']
        comp_c = data['completed_courses']
        comp_rate = round((comp_c / tot_e * 100), 1) if tot_e > 0 else 0.0
        avg_score = round(sum(data['scores']) / len(data['scores']), 1) if data['scores'] else 0.0

        row = {
            'department': dept_name,
            'total_learners': data['total_learners'],
            'active_enrollments': tot_e,
            'completed_courses': comp_c,
            'compliance_rate': f"{comp_rate}%",
            'avg_score': f"{avg_score}%",
            'total_hours': f"{round(data['total_hours'], 1)} hrs",
            'pending_requests': data['pending_requests']
        }
        rows.append(row)

    return _format_dataframe(rows, selected_columns, COMPLIANCE_COLUMNS)


def _format_dataframe(rows, selected_columns, column_map):
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=[column_map[col] for col in selected_columns if col in column_map])
    else:
        filtered_cols = [c for c in selected_columns if c in df.columns]
        df = df[filtered_cols]
        df.rename(columns={c: column_map[c] for c in filtered_cols}, inplace=True)
    return df


def export_report_csv(df):
    """
    Exports DataFrame to CSV string buffer.
    """
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    return output


def export_report_pdf(df, report_title="L&D Analytics Report", report_type="master", summary_stats=None):
    """
    Generates a PDF document from a report DataFrame using ReportLab.
    Returns BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'RepTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0A4B5C'),
        spaceAfter=4
    )

    sub_style = ParagraphStyle(
        'RepSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=12
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#1E293B')
    )

    elements = []

    # Title & Subtitle Header
    elements.append(Paragraph(f"Aditya Learning Hub — {report_title}", title_style))
    now_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    elements.append(Paragraph(f"Generated on {now_str} | System Report Type: {report_type.upper()}", sub_style))

    # Summary Stats Bar Table if available
    if summary_stats:
        stat_items = [
            [
                Paragraph(f"<b>Total Enrollments:</b> {summary_stats.get('total_enrollments', 0)}", td_style),
                Paragraph(f"<b>Completion Rate:</b> {summary_stats.get('completion_rate', 0.0)}%", td_style),
                Paragraph(f"<b>Avg Score:</b> {summary_stats.get('avg_score', 0.0)}%", td_style),
                Paragraph(f"<b>Attendance Rate:</b> {summary_stats.get('attendance_rate', 0.0)}%", td_style),
            ]
        ]
        stat_table = Table(stat_items, colWidths=[180, 180, 180, 180])
        stat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(stat_table)
        elements.append(Spacer(1, 10))

    if df.empty:
        elements.append(Paragraph("<b>No data records found matching current criteria.</b>", sub_style))
    else:
        cols = list(df.columns)
        table_data = []
        
        header_row = [Paragraph(str(c), th_style) for c in cols]
        table_data.append(header_row)

        for idx, row in df.head(1000).iterrows():
            r_data = []
            for col in cols:
                val = str(row[col]) if pd.notna(row[col]) else "N/A"
                r_data.append(Paragraph(val, td_style))
            table_data.append(r_data)

        total_width = 732
        num_cols = len(cols)
        col_w = max(40, total_width / num_cols)
        col_widths = [col_w] * num_cols

        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A4B5C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_course_analytics_csv(course_id):
    """
    Builds and exports Course Performance Analytics CSV for a specific course.
    """
    course = Course.query.get(course_id)
    if not course:
        df = pd.DataFrame()
        return export_report_csv(df)

    enrollments = LearnerEnrollment.query.filter_by(course_id=course.id).all()
    rows = []

    for en in enrollments:
        learner = en.learner
        live_cls = en.live_class

        att_status = 'N/A'
        if live_cls:
            att = Attendance.query.filter_by(class_id=live_cls.id, learner_id=learner.id).first()
            att_status = att.status if att else 'Absent'

        pre_attempt = AssessmentAttempt.query.filter((AssessmentAttempt.enrollment_id == en.id) & (AssessmentAttempt.assessment_type.in_(['PRE', 'LESSON_PRE']))).order_by(AssessmentAttempt.id.desc()).first()
        post_attempt = AssessmentAttempt.query.filter((AssessmentAttempt.enrollment_id == en.id) & (AssessmentAttempt.assessment_type.in_(['POST', 'LESSON_POST']))).order_by(AssessmentAttempt.id.desc()).first()
        course_end_attempt = AssessmentAttempt.query.filter((AssessmentAttempt.enrollment_id == en.id) & (AssessmentAttempt.assessment_type == 'COURSE_END')).order_by(AssessmentAttempt.id.desc()).first()

        cert = Certificate.query.filter_by(learner_id=learner.id, course_id=course.id).first()

        row = {
            'Course ID': course.course_id,
            'Course Name': course.name,
            'Course Mode': course.mode,
            'Learner Global ID': learner.global_id if learner else 'N/A',
            'Learner Name': learner.name if learner else 'N/A',
            'Department': learner.department if learner else 'N/A',
            'Attendance Status': att_status,
            'Pre Assessment Score': f"{pre_attempt.score_percentage}%" if pre_attempt else "N/A",
            'Post Assessment Score': f"{post_attempt.score_percentage}%" if post_attempt else "N/A",
            'Course End Exam Score': f"{course_end_attempt.score_percentage}%" if course_end_attempt else "N/A",
            'Completion Status': en.completion_status,
            'Certificate Issued': cert.certificate_id if cert else 'None',
            'Enrolled At': en.assigned_at.strftime('%Y-%m-%d %H:%M') if en.assigned_at else 'N/A'
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return export_report_csv(df)


def generate_class_attendance_csv(class_id):
    """
    Builds and exports Class Attendance Log CSV for a specific live class.
    """
    live_cls = LiveClass.query.get(class_id)
    if not live_cls:
        df = pd.DataFrame()
        return export_report_csv(df)

    attendances = Attendance.query.filter_by(class_id=live_cls.id).all()
    rows = []

    for att in attendances:
        learner = att.learner
        row = {
            'Class ID': live_cls.class_id,
            'Class Name': live_cls.class_name,
            'Class Date': live_cls.class_date.strftime('%Y-%m-%d') if live_cls.class_date else 'N/A',
            'Session Time': live_cls.session_time or 'N/A',
            'Learner Global ID': learner.global_id if learner else 'N/A',
            'Learner Name': learner.name if learner else 'N/A',
            'Department': learner.department if learner else 'N/A',
            'Attendance Status': att.status,
            'Scan Method': att.recorded_via,
            'Recorded Timestamp': att.timestamp.strftime('%Y-%m-%d %H:%M:%S') if att.timestamp else 'N/A'
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return export_report_csv(df)
