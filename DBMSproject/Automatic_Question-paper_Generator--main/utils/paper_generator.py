"""
Semi-Automatic Question Paper Generator
----------------------------------------
Implements the intelligent question selection algorithm that:
1. Filters questions by subject, modules, and recency
2. Balances difficulty distribution
3. Matches exact total marks
4. Prevents duplicate questions from recent papers
"""

from datetime import datetime, timedelta
from utils.db import execute_query
from config import Config
import random


def get_available_questions(subject_id, modules, exclude_question_ids=None):
    """
    Fetch all eligible questions for paper generation.

    Args:
        subject_id (int): Target subject ID.
        modules (list[int]): List of module numbers to include.
        exclude_question_ids (list[int]): Question IDs to exclude (recently used).

    Returns:
        list[dict]: List of eligible question records.
    """
    # Build the module placeholders
    module_placeholders = ','.join(['%s'] * len(modules))

    query = f"""
        SELECT q.question_id, q.question_text, q.module_number, q.marks,
               q.difficulty_level, q.co_mapping, q.po_mapping, q.last_used_date
        FROM QuestionBank q
        WHERE q.subject_id = %s
          AND q.module_number IN ({module_placeholders})
    """
    params = [subject_id] + modules

    # Exclude recently used questions
    if exclude_question_ids:
        id_placeholders = ','.join(['%s'] * len(exclude_question_ids))
        query += f" AND q.question_id NOT IN ({id_placeholders})"
        params.extend(exclude_question_ids)

    query += " ORDER BY q.module_number, q.difficulty_level, q.marks"

    return execute_query(query, tuple(params), fetchall=True)


def get_recently_used_question_ids(subject_id, years=None):
    """
    Get IDs of questions used in papers within the last N years.

    Args:
        subject_id (int): Subject to check.
        years (int): Number of years to look back.

    Returns:
        list[int]: List of recently used question IDs.
    """
    if years is None:
        years = Config.DUPLICATE_CHECK_YEARS

    cutoff_date = datetime.now() - timedelta(days=years * 365)

    query = """
        SELECT DISTINCT pq.question_id
        FROM PaperQuestions pq
        JOIN ExamPaper ep ON pq.paper_id = ep.paper_id
        WHERE ep.subject_id = %s
          AND ep.exam_date >= %s
    """
    results = execute_query(query, (subject_id, cutoff_date.date()), fetchall=True)
    return [r['question_id'] for r in results] if results else []


def get_duplicate_text_question_ids(subject_id):
    """
    Get IDs of questions whose exact text appears in previously generated papers.
    Uses exact text matching to prevent repeated questions.

    Args:
        subject_id (int): Subject to check.

    Returns:
        list[int]: List of question IDs with duplicate text.
    """
    query = """
        SELECT DISTINCT q2.question_id
        FROM QuestionBank q2
        WHERE q2.subject_id = %s
          AND q2.question_text IN (
              SELECT q.question_text
              FROM PaperQuestions pq
              JOIN QuestionBank q ON pq.question_id = q.question_id
              JOIN ExamPaper ep ON pq.paper_id = ep.paper_id
              WHERE ep.subject_id = %s
                AND ep.exam_date >= DATE_SUB(CURDATE(), INTERVAL %s YEAR)
          )
    """
    results = execute_query(
        query,
        (subject_id, subject_id, Config.DUPLICATE_CHECK_YEARS),
        fetchall=True
    )
    return [r['question_id'] for r in results] if results else []


def generate_paper(subject_id, total_marks, modules, difficulty_dist):
    """
    Generate a question paper using semi-automatic selection.

    Algorithm:
    1. Calculate target marks for each difficulty level
    2. Filter out recently used questions (last 2 years)
    3. Filter out duplicate text questions
    4. Group available questions by difficulty
    5. Use greedy selection with backtracking to match total marks
    6. Ensure module-wise distribution

    Args:
        subject_id (int): Target subject.
        total_marks (int): Total marks for the paper (20/30/50).
        modules (list[int]): List of modules to include.
        difficulty_dist (dict): Distribution like {'Easy': 30, 'Medium': 50, 'Hard': 20}
            Values are percentages that should sum to 100.

    Returns:
        dict: {
            'success': bool,
            'questions': list[dict],
            'total_marks': int,
            'message': str,
            'distribution': dict  # actual difficulty distribution achieved
        }
    """
    # Step 1: Calculate target marks per difficulty
    targets = {}
    for level, percentage in difficulty_dist.items():
        targets[level] = round(total_marks * percentage / 100)

    # Adjust rounding errors to match total
    diff = total_marks - sum(targets.values())
    if diff != 0:
        # Add/subtract from the largest group
        largest = max(targets, key=targets.get)
        targets[largest] += diff

    # Step 2: Get recently used and duplicate text question IDs
    recently_used_ids = get_recently_used_question_ids(subject_id)
    duplicate_text_ids = get_duplicate_text_question_ids(subject_id)
    exclude_ids = list(set(recently_used_ids + duplicate_text_ids))

    # Step 3: Get available questions
    available = get_available_questions(subject_id, modules, exclude_ids)

    if not available:
        return {
            'success': False,
            'questions': [],
            'total_marks': 0,
            'message': 'No eligible questions found. All questions may have been recently used.',
            'distribution': {}
        }

    # Step 4: Group by difficulty
    by_difficulty = {'Easy': [], 'Medium': [], 'Hard': []}
    for q in available:
        level = q['difficulty_level']
        if level in by_difficulty:
            by_difficulty[level].append(q)

    # Step 5: Select questions for each difficulty level
    selected = []
    actual_marks = {'Easy': 0, 'Medium': 0, 'Hard': 0}

    for level in ['Easy', 'Medium', 'Hard']:
        target_marks = targets.get(level, 0)
        if target_marks <= 0:
            continue

        pool = by_difficulty[level][:]
        random.shuffle(pool)

        # Try to find a combination that sums to target marks
        level_selected = _select_questions_for_marks(pool, target_marks)
        selected.extend(level_selected)
        actual_marks[level] = sum(q['marks'] for q in level_selected)

    # Step 6: Check if we hit the total
    achieved_total = sum(q['marks'] for q in selected)

    if achieved_total < total_marks:
        # Try to fill remaining marks from any difficulty
        remaining = total_marks - achieved_total
        used_ids = {q['question_id'] for q in selected}
        remaining_pool = [q for q in available if q['question_id'] not in used_ids]
        random.shuffle(remaining_pool)

        fill = _select_questions_for_marks(remaining_pool, remaining)
        selected.extend(fill)
        for q in fill:
            actual_marks[q['difficulty_level']] += q['marks']
        achieved_total = sum(q['marks'] for q in selected)

    # Sort selected questions by module then question order
    selected.sort(key=lambda q: (q['module_number'], q['marks']))

    # Assign question order
    for i, q in enumerate(selected, 1):
        q['question_order'] = i

    success = achieved_total == total_marks
    message = 'Paper generated successfully!' if success else (
        f'Could only achieve {achieved_total}/{total_marks} marks with available questions. '
        'Consider adding more questions to the bank or adjusting constraints.'
    )

    return {
        'success': success,
        'questions': selected,
        'total_marks': achieved_total,
        'message': message,
        'distribution': actual_marks
    }


def _select_questions_for_marks(pool, target_marks):
    """
    Select a subset of questions from pool that sums to exactly target_marks.
    Uses greedy approach with multiple random shuffles.

    Args:
        pool (list[dict]): Available questions.
        target_marks (int): Target marks to achieve.

    Returns:
        list[dict]: Selected questions (may not reach target if impossible).
    """
    best_selection = []
    best_total = 0

    # Try multiple random orderings
    for attempt in range(min(Config.MAX_GENERATION_ATTEMPTS, 50)):
        random.shuffle(pool)
        selection = []
        current_total = 0

        for q in pool:
            if current_total + q['marks'] <= target_marks:
                selection.append(q)
                current_total += q['marks']

            if current_total == target_marks:
                return selection  # Perfect match found

        # Track best attempt
        if current_total > best_total:
            best_total = current_total
            best_selection = selection[:]

    return best_selection


def validate_paper_config(total_marks, modules, difficulty_dist):
    """
    Validate paper generation configuration.

    Args:
        total_marks (int): Must be 20, 30, or 50.
        modules (list[int]): Must be non-empty, values 1-6.
        difficulty_dist (dict): Percentages must sum to 100.

    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # Validate total marks
    if total_marks not in [20, 30, 50]:
        return False, 'Total marks must be 20, 30, or 50.'

    # Validate modules
    if not modules:
        return False, 'At least one module must be selected.'
    if any(m < 1 or m > 6 for m in modules):
        return False, 'Module numbers must be between 1 and 6.'

    # Validate difficulty distribution
    total_pct = sum(difficulty_dist.values())
    if abs(total_pct - 100) > 1:  # Allow 1% rounding tolerance
        return False, f'Difficulty percentages must sum to 100 (currently {total_pct}).'

    return True, ''
