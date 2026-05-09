"""
Paper Generation & Archive Routes
-----------------------------------
Handles paper generation wizard, preview, saving, listing,
viewing, and PDF download.
"""

import json
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session, send_file, jsonify)
from routes.auth import login_required
from utils.db import execute_query
from utils.paper_generator import generate_paper, validate_paper_config
from utils.pdf_export import generate_pdf

papers_bp = Blueprint('papers', __name__, url_prefix='/papers')


@papers_bp.route('/')
@login_required
def list_papers():
    """List all generated papers with search/filter."""
    subject_id = request.args.get('subject_id', '', type=str)
    search = request.args.get('search', '', type=str)

    query = """
        SELECT ep.*, s.subject_name, s.subject_code, f.name as faculty_name,
               (SELECT COUNT(*) FROM PaperQuestions pq WHERE pq.paper_id = ep.paper_id) as question_count
        FROM ExamPaper ep
        JOIN Subject s ON ep.subject_id = s.subject_id
        JOIN Faculty f ON ep.faculty_id = f.faculty_id
        WHERE 1=1
    """
    params = []
    if subject_id:
        query += " AND ep.subject_id = %s"
        params.append(int(subject_id))
    if search:
        query += " AND (s.subject_name LIKE %s OR ep.exam_type LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    query += " ORDER BY ep.generated_at DESC"

    papers = execute_query(query, tuple(params), fetchall=True)
    subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
    return render_template('papers/list.html', papers=papers, subjects=subjects,
                           filters={'subject_id': subject_id, 'search': search})


@papers_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    """Paper generation wizard."""
    if request.method == 'POST':
        subject_id = request.form.get('subject_id', type=int)
        total_marks = request.form.get('total_marks', type=int)
        modules = request.form.getlist('modules', type=int)
        easy_pct = request.form.get('easy_pct', 30, type=int)
        medium_pct = request.form.get('medium_pct', 50, type=int)
        hard_pct = request.form.get('hard_pct', 20, type=int)
        difficulty_dist = {'Easy': easy_pct, 'Medium': medium_pct, 'Hard': hard_pct}

        is_valid, error_msg = validate_paper_config(total_marks, modules, difficulty_dist)
        if not is_valid:
            flash(error_msg, 'danger')
            subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
            return render_template('papers/generate.html', subjects=subjects, form_data=request.form)

        result = generate_paper(subject_id, total_marks, modules, difficulty_dist)
        if not result['questions']:
            flash(result['message'], 'warning')
            subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
            return render_template('papers/generate.html', subjects=subjects, form_data=request.form)

        subject = execute_query("SELECT * FROM Subject WHERE subject_id = %s", (subject_id,), fetchone=True)

        # Serialize dates for session storage
        questions_for_session = []
        for q in result['questions']:
            q_copy = dict(q)
            for key in ['last_used_date', 'created_at', 'updated_at']:
                if q_copy.get(key):
                    q_copy[key] = str(q_copy[key])
            questions_for_session.append(q_copy)

        session['paper_preview'] = {
            'subject_id': subject_id, 'subject_name': subject['subject_name'],
            'total_marks': total_marks, 'achieved_marks': result['total_marks'],
            'questions': questions_for_session, 'distribution': result['distribution'],
            'difficulty_dist': difficulty_dist, 'modules': modules,
            'message': result['message'], 'success': result['success']
        }
        return redirect(url_for('papers.preview'))

    subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
    return render_template('papers/generate.html', subjects=subjects, form_data={})


@papers_bp.route('/preview')
@login_required
def preview():
    """Preview generated paper before saving."""
    preview_data = session.get('paper_preview')
    if not preview_data:
        flash('No paper preview available. Please generate a paper first.', 'warning')
        return redirect(url_for('papers.generate'))
    return render_template('papers/preview.html', preview=preview_data)


@papers_bp.route('/save', methods=['POST'])
@login_required
def save_paper():
    """Save the previewed paper to the database."""
    preview_data = session.get('paper_preview')
    if not preview_data:
        flash('No paper data found.', 'warning')
        return redirect(url_for('papers.generate'))

    exam_type = request.form.get('exam_type', 'Internal Assessment').strip()
    exam_date = request.form.get('exam_date', '').strip()
    if not exam_date:
        flash('Exam date is required.', 'danger')
        return redirect(url_for('papers.preview'))

    try:
        paper_id = execute_query(
            """INSERT INTO ExamPaper (subject_id, faculty_id, total_marks, exam_type, exam_date)
               VALUES (%s, %s, %s, %s, %s)""",
            (preview_data['subject_id'], session['faculty_id'],
             preview_data['achieved_marks'], exam_type, exam_date),
            commit=True
        )
        for q in preview_data['questions']:
            execute_query(
                "INSERT INTO PaperQuestions (paper_id, question_id, question_order) VALUES (%s, %s, %s)",
                (paper_id, q['question_id'], q.get('question_order', 1)), commit=True
            )
            execute_query(
                "UPDATE QuestionBank SET last_used_date = %s WHERE question_id = %s",
                (exam_date, q['question_id']), commit=True
            )
        session.pop('paper_preview', None)
        flash('Question paper saved successfully!', 'success')
        return redirect(url_for('papers.view_paper', paper_id=paper_id))
    except Exception as e:
        flash(f'Error saving paper: {str(e)}', 'danger')
        return redirect(url_for('papers.preview'))


@papers_bp.route('/view/<int:paper_id>')
@login_required
def view_paper(paper_id):
    """View a single paper with all its questions."""
    paper = execute_query(
        """SELECT ep.*, s.subject_name, s.subject_code, f.name as faculty_name
           FROM ExamPaper ep JOIN Subject s ON ep.subject_id = s.subject_id
           JOIN Faculty f ON ep.faculty_id = f.faculty_id WHERE ep.paper_id = %s""",
        (paper_id,), fetchone=True
    )
    if not paper:
        flash('Paper not found.', 'danger')
        return redirect(url_for('papers.list_papers'))

    questions = execute_query(
        """SELECT q.*, pq.question_order FROM PaperQuestions pq
           JOIN QuestionBank q ON pq.question_id = q.question_id
           WHERE pq.paper_id = %s ORDER BY pq.question_order""",
        (paper_id,), fetchall=True
    )
    return render_template('papers/view.html', paper=paper, questions=questions)


@papers_bp.route('/download/<int:paper_id>')
@login_required
def download_paper(paper_id):
    """Generate and download PDF."""
    paper = execute_query(
        """SELECT ep.*, s.subject_name, f.name as faculty_name
           FROM ExamPaper ep JOIN Subject s ON ep.subject_id = s.subject_id
           JOIN Faculty f ON ep.faculty_id = f.faculty_id WHERE ep.paper_id = %s""",
        (paper_id,), fetchone=True
    )
    if not paper:
        flash('Paper not found.', 'danger')
        return redirect(url_for('papers.list_papers'))

    questions = execute_query(
        """SELECT q.*, pq.question_order FROM PaperQuestions pq
           JOIN QuestionBank q ON pq.question_id = q.question_id
           WHERE pq.paper_id = %s ORDER BY pq.question_order""",
        (paper_id,), fetchall=True
    )
    try:
        pdf_path = generate_pdf(paper, questions, paper['subject_name'], paper['faculty_name'])
        return send_file(pdf_path, as_attachment=True,
                         download_name=f"QuestionPaper_{paper['subject_name'].replace(' ', '_')}_{paper['exam_date']}.pdf")
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('papers.view_paper', paper_id=paper_id))


@papers_bp.route('/api/subject-modules/<int:subject_id>')
@login_required
def get_subject_modules(subject_id):
    """API: get available modules for a subject."""
    modules = execute_query(
        "SELECT DISTINCT module_number FROM QuestionBank WHERE subject_id = %s ORDER BY module_number",
        (subject_id,), fetchall=True
    )
    return jsonify([m['module_number'] for m in modules])
