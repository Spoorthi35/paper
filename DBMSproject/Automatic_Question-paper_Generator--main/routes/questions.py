"""
Question Bank Routes
--------------------
CRUD operations for managing the question bank.
Supports add, edit, delete, and search/filter functionality.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from utils.db import execute_query
from utils.pdf_extractor import extract_questions_from_pdf

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')


@questions_bp.route('/')
@login_required
def list_questions():
    """
    List all questions with optional search and filter.
    Supports filtering by subject, module, and difficulty level.
    """
    # Get filter parameters
    subject_id = request.args.get('subject_id', '', type=str)
    module = request.args.get('module', '', type=str)
    difficulty = request.args.get('difficulty', '', type=str)
    search = request.args.get('search', '', type=str)

    # Build dynamic query
    query = """
        SELECT q.*, s.subject_name, s.subject_code
        FROM QuestionBank q
        JOIN Subject s ON q.subject_id = s.subject_id
        WHERE 1=1
    """
    params = []

    if subject_id:
        query += " AND q.subject_id = %s"
        params.append(int(subject_id))

    if module:
        query += " AND q.module_number = %s"
        params.append(int(module))

    if difficulty:
        query += " AND q.difficulty_level = %s"
        params.append(difficulty)

    if search:
        query += " AND q.question_text LIKE %s"
        params.append(f'%{search}%')

    query += " ORDER BY q.subject_id, q.module_number, q.question_id"

    questions = execute_query(query, tuple(params), fetchall=True)

    # Get subjects for filter dropdown
    subjects = execute_query(
        "SELECT * FROM Subject ORDER BY subject_name",
        fetchall=True
    )

    return render_template('questions/list.html',
                           questions=questions,
                           subjects=subjects,
                           filters={
                               'subject_id': subject_id,
                               'module': module,
                               'difficulty': difficulty,
                               'search': search
                           })


@questions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_question():
    """Add a new question to the question bank."""

    if request.method == 'POST':
        # Extract form data
        subject_id = request.form.get('subject_id', type=int)
        question_text = request.form.get('question_text', '').strip()
        module_number = request.form.get('module_number', type=int)
        marks = request.form.get('marks', type=int)
        difficulty_level = request.form.get('difficulty_level', '').strip()
        co_mapping = request.form.get('co_mapping', '').strip()
        po_mapping = request.form.get('po_mapping', '').strip()

        # Server-side validation
        errors = []
        if not subject_id:
            errors.append('Subject is required.')
        if not question_text:
            errors.append('Question text is required.')
        if not module_number or module_number < 1 or module_number > 6:
            errors.append('Module number must be between 1 and 6.')
        if not marks or marks < 1:
            errors.append('Marks must be a positive number.')
        if difficulty_level not in ('Easy', 'Medium', 'Hard'):
            errors.append('Invalid difficulty level.')
        if not co_mapping:
            errors.append('CO mapping is required.')
        if not po_mapping:
            errors.append('PO mapping is required.')

        # Check for duplicate question text in same subject
        if question_text and subject_id:
            existing = execute_query(
                "SELECT question_id FROM QuestionBank WHERE subject_id = %s AND question_text = %s",
                (subject_id, question_text),
                fetchone=True
            )
            if existing:
                errors.append('A question with identical text already exists for this subject.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
            return render_template('questions/add.html', subjects=subjects,
                                   form_data=request.form)

        # Insert the question
        try:
            execute_query(
                """INSERT INTO QuestionBank
                   (subject_id, question_text, module_number, marks,
                    difficulty_level, co_mapping, po_mapping, added_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (subject_id, question_text, module_number, marks,
                 difficulty_level, co_mapping, po_mapping, session['faculty_id']),
                commit=True
            )
            flash('Question added successfully!', 'success')
            return redirect(url_for('questions.list_questions'))
        except Exception as e:
            flash(f'Error adding question: {str(e)}', 'danger')

    # GET request — show empty form
    subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
    return render_template('questions/add.html', subjects=subjects, form_data={})


@questions_bp.route('/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    """Edit an existing question."""

    # Fetch the question
    question = execute_query(
        "SELECT * FROM QuestionBank WHERE question_id = %s",
        (question_id,),
        fetchone=True
    )

    if not question:
        flash('Question not found.', 'danger')
        return redirect(url_for('questions.list_questions'))

    if request.method == 'POST':
        # Extract form data
        subject_id = request.form.get('subject_id', type=int)
        question_text = request.form.get('question_text', '').strip()
        module_number = request.form.get('module_number', type=int)
        marks = request.form.get('marks', type=int)
        difficulty_level = request.form.get('difficulty_level', '').strip()
        co_mapping = request.form.get('co_mapping', '').strip()
        po_mapping = request.form.get('po_mapping', '').strip()

        # Server-side validation
        errors = []
        if not subject_id:
            errors.append('Subject is required.')
        if not question_text:
            errors.append('Question text is required.')
        if not module_number or module_number < 1 or module_number > 6:
            errors.append('Module number must be between 1 and 6.')
        if not marks or marks < 1:
            errors.append('Marks must be a positive number.')
        if difficulty_level not in ('Easy', 'Medium', 'Hard'):
            errors.append('Invalid difficulty level.')
        if not co_mapping:
            errors.append('CO mapping is required.')
        if not po_mapping:
            errors.append('PO mapping is required.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
            return render_template('questions/edit.html', question=question,
                                   subjects=subjects, form_data=request.form)

        # Update the question
        try:
            execute_query(
                """UPDATE QuestionBank SET
                   subject_id = %s, question_text = %s, module_number = %s,
                   marks = %s, difficulty_level = %s, co_mapping = %s, po_mapping = %s
                   WHERE question_id = %s""",
                (subject_id, question_text, module_number, marks,
                 difficulty_level, co_mapping, po_mapping, question_id),
                commit=True
            )
            flash('Question updated successfully!', 'success')
            return redirect(url_for('questions.list_questions'))
        except Exception as e:
            flash(f'Error updating question: {str(e)}', 'danger')

    # GET request — show pre-filled form
    subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
    return render_template('questions/edit.html', question=question,
                           subjects=subjects, form_data={})


@questions_bp.route('/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    """Delete a question from the question bank."""

    # Check if question exists
    question = execute_query(
        "SELECT question_id FROM QuestionBank WHERE question_id = %s",
        (question_id,),
        fetchone=True
    )

    if not question:
        flash('Question not found.', 'danger')
        return redirect(url_for('questions.list_questions'))

    # Check if question is used in any paper
    used_in_paper = execute_query(
        "SELECT COUNT(*) as count FROM PaperQuestions WHERE question_id = %s",
        (question_id,),
        fetchone=True
    )['count']

    if used_in_paper > 0:
        flash('Cannot delete this question as it is used in existing papers.', 'warning')
        return redirect(url_for('questions.list_questions'))

    try:
        execute_query(
            "DELETE FROM QuestionBank WHERE question_id = %s",
            (question_id,),
            commit=True
        )
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'danger')

    return redirect(url_for('questions.list_questions'))


@questions_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_pdf():
    """Upload a PDF file to extract questions."""
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['pdf_file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and file.filename.lower().endswith('.pdf'):
            try:
                extracted_questions = extract_questions_from_pdf(file)
                if not extracted_questions:
                    flash('No questions could be extracted from the PDF. Please ensure it contains readable text.', 'warning')
                    return redirect(request.url)
                    
                session['extracted_questions'] = extracted_questions
                flash(f'Successfully extracted {len(extracted_questions)} questions from the PDF.', 'success')
                return redirect(url_for('questions.review_upload'))
                
            except Exception as e:
                flash(f'Error processing PDF: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Please upload a valid PDF file.', 'danger')
            return redirect(request.url)

    return render_template('questions/upload.html')


@questions_bp.route('/review_upload', methods=['GET'])
@login_required
def review_upload():
    """Review and categorize extracted questions before saving."""
    extracted_questions = session.get('extracted_questions')
    
    if not extracted_questions:
        flash('No extracted questions found. Please upload a PDF first.', 'warning')
        return redirect(url_for('questions.upload_pdf'))
        
    subjects = execute_query("SELECT * FROM Subject ORDER BY subject_name", fetchall=True)
    return render_template('questions/review_upload.html', questions=extracted_questions, subjects=subjects)


@questions_bp.route('/save_upload', methods=['POST'])
@login_required
def save_upload():
    """Save the reviewed and categorized questions to the database."""
    from utils.db import execute_many
    extracted_questions = session.get('extracted_questions')
    
    if not extracted_questions:
        flash('Session expired. Please upload the PDF again.', 'warning')
        return redirect(url_for('questions.upload_pdf'))

    subject_id = request.form.get('subject_id', type=int)
    if not subject_id:
        flash('Please select a subject.', 'danger')
        return redirect(url_for('questions.review_upload'))

    questions_to_save = []
    
    # Process each question submitted in the form
    for i in range(len(extracted_questions)):
        # Check if the user selected to include this question
        if request.form.get(f'include_{i}'):
            q_text = request.form.get(f'q_text_{i}', '').strip()
            module = request.form.get(f'module_{i}', type=int)
            marks = request.form.get(f'marks_{i}', type=int)
            difficulty = request.form.get(f'difficulty_{i}')
            co_mapping = request.form.get(f'co_{i}', '').strip()
            po_mapping = request.form.get(f'po_{i}', '').strip()
            
            if q_text and module and marks and difficulty and co_mapping and po_mapping:
                questions_to_save.append((
                    subject_id, q_text, module, marks, difficulty, 
                    co_mapping, po_mapping, session['faculty_id']
                ))

    if not questions_to_save:
        flash('No valid questions selected to save. Please ensure all fields are filled for selected questions.', 'warning')
        return redirect(url_for('questions.review_upload'))

    try:
        execute_many(
            """INSERT INTO QuestionBank
               (subject_id, question_text, module_number, marks,
                difficulty_level, co_mapping, po_mapping, added_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            questions_to_save
        )
        
        session.pop('extracted_questions', None)
        flash(f'Successfully added {len(questions_to_save)} questions to the bank!', 'success')
        return redirect(url_for('questions.list_questions'))
        
    except Exception as e:
        flash(f'Error saving questions: {str(e)}', 'danger')
        return redirect(url_for('questions.review_upload'))
