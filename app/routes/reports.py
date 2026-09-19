from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from datetime import date
import math
from app.services.report_service import (
    generate_report_dataframe, 
    export_report_csv, 
    export_report_pdf,
    get_report_columns, 
    get_report_summary_stats,
    REPORT_TYPES
)
from app.utils.decorators import admin_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@admin_required
def index():
    report_type = request.args.get('type', 'master').strip().lower()
    if report_type not in REPORT_TYPES:
        report_type = 'master'

    search_query = request.args.get('search', '').strip()
    mode_filter = request.args.get('mode', 'ALL').strip()
    selected_cols = request.args.getlist('cols')
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    course_filter = request.args.get('course_id', 'ALL').strip()
    class_filter = request.args.get('class_id', 'ALL').strip()
    department_filter = request.args.get('department', 'ALL').strip()
    status_filter = request.args.get('status', 'ALL').strip()
    assessment_type_filter = request.args.get('assessment_type', 'ALL').strip()

    # Pagination params
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    if per_page not in [10, 25, 50, 100, 250, 0]:
        per_page = 25

    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = date.fromisoformat(date_from_str)
        if date_to_str:
            date_to = date.fromisoformat(date_to_str)
    except ValueError:
        pass

    available_columns = get_report_columns(report_type)
    if not selected_cols:
        selected_cols = list(available_columns.keys())

    df = generate_report_dataframe(
        report_type=report_type,
        selected_columns=selected_cols, 
        search_query=search_query, 
        mode_filter=mode_filter, 
        date_from=date_from, 
        date_to=date_to,
        course_id_filter=course_filter,
        class_id_filter=class_filter,
        department_filter=department_filter,
        status_filter=status_filter,
        assessment_type_filter=assessment_type_filter
    )

    total_records = len(df)
    if per_page > 0:
        total_pages = max(1, math.ceil(total_records / per_page))
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged_df = df.iloc[start_idx:end_idx] if total_records > 0 else df
        start_record = start_idx + 1 if total_records > 0 else 0
        end_record = min(end_idx, total_records)
    else:
        total_pages = 1
        page = 1
        paged_df = df
        start_record = 1 if total_records > 0 else 0
        end_record = total_records

    records = paged_df.to_dict(orient='records')
    headers = list(df.columns)

    summary_stats = get_report_summary_stats()

    from app.models.course import Course
    from app.models.live_class import LiveClass
    from app.models.user import Learner
    courses = Course.query.order_by(Course.name).all()
    classes = LiveClass.query.order_by(LiveClass.class_name).all()
    
    dept_tuples = Learner.query.with_entities(Learner.department).distinct().all()
    departments = sorted([d[0] for d in dept_tuples if d[0]])

    return render_template(
        'reports/index.html',
        report_type=report_type,
        report_types=REPORT_TYPES,
        all_columns=available_columns,
        selected_cols=selected_cols,
        headers=headers,
        records=records,
        summary_stats=summary_stats,
        search_query=search_query,
        mode_filter=mode_filter,
        date_from_str=date_from_str,
        date_to_str=date_to_str,
        course_filter=course_filter,
        class_filter=class_filter,
        department_filter=department_filter,
        status_filter=status_filter,
        assessment_type_filter=assessment_type_filter,
        courses=courses,
        classes=classes,
        departments=departments,
        total_records=total_records,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        start_record=start_record,
        end_record=end_record
    )


@reports_bp.route('/export_csv')
@admin_required
def export_csv():
    report_type = request.args.get('type', 'master').strip().lower()
    if report_type not in REPORT_TYPES:
        report_type = 'master'

    search_query = request.args.get('search', '').strip()
    mode_filter = request.args.get('mode', 'ALL').strip()
    selected_cols = request.args.getlist('cols')
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    course_filter = request.args.get('course_id', 'ALL').strip()
    class_filter = request.args.get('class_id', 'ALL').strip()
    department_filter = request.args.get('department', 'ALL').strip()
    status_filter = request.args.get('status', 'ALL').strip()
    assessment_type_filter = request.args.get('assessment_type', 'ALL').strip()

    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = date.fromisoformat(date_from_str)
        if date_to_str:
            date_to = date.fromisoformat(date_to_str)
    except ValueError:
        pass

    available_columns = get_report_columns(report_type)
    if not selected_cols:
        selected_cols = list(available_columns.keys())

    df = generate_report_dataframe(
        report_type=report_type,
        selected_columns=selected_cols, 
        search_query=search_query, 
        mode_filter=mode_filter, 
        date_from=date_from, 
        date_to=date_to,
        course_id_filter=course_filter,
        class_id_filter=class_filter,
        department_filter=department_filter,
        status_filter=status_filter,
        assessment_type_filter=assessment_type_filter
    )
    csv_buffer = export_report_csv(df)

    filename = f"Aditya_LND_{report_type.capitalize()}_Report.csv"

    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@reports_bp.route('/export_pdf')
@admin_required
def export_pdf():
    report_type = request.args.get('type', 'master').strip().lower()
    if report_type not in REPORT_TYPES:
        report_type = 'master'

    search_query = request.args.get('search', '').strip()
    mode_filter = request.args.get('mode', 'ALL').strip()
    selected_cols = request.args.getlist('cols')
    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    course_filter = request.args.get('course_id', 'ALL').strip()
    class_filter = request.args.get('class_id', 'ALL').strip()
    department_filter = request.args.get('department', 'ALL').strip()
    status_filter = request.args.get('status', 'ALL').strip()
    assessment_type_filter = request.args.get('assessment_type', 'ALL').strip()

    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = date.fromisoformat(date_from_str)
        if date_to_str:
            date_to = date.fromisoformat(date_to_str)
    except ValueError:
        pass

    available_columns = get_report_columns(report_type)
    if not selected_cols:
        selected_cols = list(available_columns.keys())

    df = generate_report_dataframe(
        report_type=report_type,
        selected_columns=selected_cols, 
        search_query=search_query, 
        mode_filter=mode_filter, 
        date_from=date_from, 
        date_to=date_to,
        course_id_filter=course_filter,
        class_id_filter=class_filter,
        department_filter=department_filter,
        status_filter=status_filter,
        assessment_type_filter=assessment_type_filter
    )

    summary_stats = get_report_summary_stats()
    report_title = REPORT_TYPES.get(report_type, "Analytics Report")
    pdf_buffer = export_report_pdf(df, report_title=report_title, report_type=report_type, summary_stats=summary_stats)

    filename = f"Aditya_LND_{report_type.capitalize()}_Report.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
