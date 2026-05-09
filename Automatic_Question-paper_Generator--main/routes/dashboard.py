"""
Dashboard Routes
----------------
Main dashboard with statistics cards and recent activity.
"""

from flask import Blueprint, render_template, session
from routes.auth import login_required
from utils.db import execute_query

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Display the main dashboard with key statistics.
    Shows total questions, papers, subjects, and recent papers.
    """
    faculty_id = session['faculty_id']

    # Total questions in the bank
    total_questions = execute_query(
        "SELECT COUNT(*) as count FROM QuestionBank",
        fetchone=True
    )['count']

    # Total generated papers
    total_papers = execute_query(
        "SELECT COUNT(*) as count FROM ExamPaper",
        fetchone=True
    )['count']

    # Total subjects
    total_subjects = execute_query(
        "SELECT COUNT(*) as count FROM Subject",
        fetchone=True
    )['count']

    # Questions added by this faculty
    my_questions = execute_query(
        "SELECT COUNT(*) as count FROM QuestionBank WHERE added_by = %s",
        (faculty_id,),
        fetchone=True
    )['count']

    # Questions by difficulty
    difficulty_stats = execute_query(
        """SELECT difficulty_level, COUNT(*) as count
           FROM QuestionBank
           GROUP BY difficulty_level
           ORDER BY FIELD(difficulty_level, 'Easy', 'Medium', 'Hard')""",
        fetchall=True
    )

    # Questions by subject
    subject_stats = execute_query(
        """SELECT s.subject_name, COUNT(q.question_id) as count
           FROM Subject s
           LEFT JOIN QuestionBank q ON s.subject_id = q.subject_id
           GROUP BY s.subject_id, s.subject_name
           ORDER BY count DESC""",
        fetchall=True
    )

    # Recent papers (last 5)
    recent_papers = execute_query(
        """SELECT ep.paper_id, ep.total_marks, ep.exam_type, ep.exam_date,
                  ep.generated_at, s.subject_name, f.name as faculty_name
           FROM ExamPaper ep
           JOIN Subject s ON ep.subject_id = s.subject_id
           JOIN Faculty f ON ep.faculty_id = f.faculty_id
           ORDER BY ep.generated_at DESC
           LIMIT 5""",
        fetchall=True
    )

    return render_template('dashboard.html',
                           total_questions=total_questions,
                           total_papers=total_papers,
                           total_subjects=total_subjects,
                           my_questions=my_questions,
                           difficulty_stats=difficulty_stats,
                           subject_stats=subject_stats,
                           recent_papers=recent_papers)
