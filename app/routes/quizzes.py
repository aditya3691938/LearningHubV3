import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db
from app.models.quiz import Quiz, QuizQuestion
from app.utils.decorators import admin_required
from app.services.assessment_service import parse_assessment_csv

quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes')

@quizzes_bp.route('/')
@admin_required
def list_quizzes():
    quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    return render_template('quizzes/list.html', quizzes=quizzes)

@quizzes_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        try:
            pass_percentage = float(request.form.get('pass_percentage', 80.0))
        except ValueError:
            pass_percentage = 80.0

        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('quizzes.create_quiz'))

        quiz = Quiz(title=title, description=description, pass_percentage=pass_percentage)
        db.session.add(quiz)
        db.session.commit()
        flash(f'Quiz "{title}" created successfully.', 'success')
        return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

    return render_template('quizzes/create_edit.html', quiz=None)

@quizzes_bp.route('/<int:quiz_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        try:
            pass_percentage = float(request.form.get('pass_percentage', 80.0))
        except ValueError:
            pass_percentage = quiz.pass_percentage

        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('quizzes.edit_quiz', quiz_id=quiz.id))

        quiz.title = title
        quiz.description = description
        quiz.pass_percentage = pass_percentage
        db.session.commit()
        flash(f'Quiz "{title}" updated successfully.', 'success')
        return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

    return render_template('quizzes/create_edit.html', quiz=quiz)

@quizzes_bp.route('/<int:quiz_id>')
@admin_required
def detail_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).order_by(QuizQuestion.serial_number.asc()).all()
    return render_template('quizzes/detail.html', quiz=quiz, questions=questions)

@quizzes_bp.route('/<int:quiz_id>/add_question', methods=['POST'])
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question_text = request.form.get('question_text', '').strip()
    
    if not question_text:
        flash("Question text is required.", "danger")
        return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

    option1 = request.form.get('option1', '').strip()
    option2 = request.form.get('option2', '').strip()
    option3 = request.form.get('option3', '').strip()
    option4 = request.form.get('option4', '').strip()
    option5 = request.form.get('option5', '').strip()
    correct_option = request.form.get('correct_option', '').strip()

    if not all([option1, option2, option3, option4, correct_option]):
        flash("Options 1-4 and a correct option are required.", "danger")
        return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

    max_serial = db.session.query(db.func.max(QuizQuestion.serial_number)).filter_by(quiz_id=quiz.id).scalar()
    new_serial = (max_serial or 0) + 1

    question = QuizQuestion(
        quiz_id=quiz.id,
        serial_number=new_serial,
        question_text=question_text,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        option5=option5,
        correct_option=correct_option
    )
    db.session.add(question)
    db.session.commit()
    flash("Question added successfully.", "success")
    return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

@quizzes_bp.route('/<int:quiz_id>/upload_csv', methods=['POST'])
@admin_required
def upload_csv(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    csv_file = request.files.get('csv_file')
    if not csv_file or not csv_file.filename:
        flash("No CSV or Excel file selected.", "danger")
        return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

    q_list, errs = parse_assessment_csv(csv_file.stream, filename=csv_file.filename)
    if errs:
        flash(f"CSV import notes: {'; '.join(errs[:3])}", "warning")

    if not q_list:
        flash("No valid questions found in CSV.", "danger")
        return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

    max_serial = db.session.query(db.func.max(QuizQuestion.serial_number)).filter_by(quiz_id=quiz.id).scalar() or 0

    added_count = 0
    for q in q_list:
        max_serial += 1
        question = QuizQuestion(
            quiz_id=quiz.id,
            serial_number=max_serial,
            question_text=q.get('question'),
            option1=q.get('option1'),
            option2=q.get('option2'),
            option3=q.get('option3'),
            option4=q.get('option4'),
            option5=q.get('option5'),
            correct_option=q.get('correct_option')
        )
        db.session.add(question)
        added_count += 1

    db.session.commit()
    flash(f"Successfully imported {added_count} questions from CSV.", "success")
    return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

@quizzes_bp.route('/<int:quiz_id>/questions/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(quiz_id, question_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    question = QuizQuestion.query.filter_by(id=question_id, quiz_id=quiz.id).first_or_404()
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully.", "success")
    return redirect(url_for('quizzes.detail_quiz', quiz_id=quiz.id))

@quizzes_bp.route('/<int:quiz_id>/delete', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully.", "success")
    return redirect(url_for('quizzes.list_quizzes'))
