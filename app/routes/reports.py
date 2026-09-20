from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from datetime import date
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

def _get_course_id_filters():
    raw_list = request.args.getlist('course_id')
    course_filter_ids = []
    for item in raw_list:
        for sub in str(item).split(','):
            sub_s = sub.strip()
            if sub_s and sub_s.upper() != 'ALL' and sub_s not in course_filter_ids:
                course_filter_ids.append(sub_s)
    return course_filter_ids if course_filter_ids else ['ALL']


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
    course_filter = _get_course_id_filters()
    class_filter = request.args.get('class_id', 'ALL').strip()

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
        class_id_filter=class_filter
    )

    records = df.to_dict(orient='records')
    headers = list(df.columns)

    summary_stats = get_report_summary_stats()

    from app.models.course import Course
    from app.models.live_class import LiveClass
    courses = Course.query.order_by(Course.name).all()
    classes = LiveClass.query.order_by(LiveClass.class_name).all()

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
        courses=courses,
        classes=classes
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
    course_filter = _get_course_id_filters()
    class_filter = request.args.get('class_id', 'ALL').strip()

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
        class_id_filter=class_filter
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
    course_filter = _get_course_id_filters()
    class_filter = request.args.get('class_id', 'ALL').strip()

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
        class_id_filter=class_filter
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
