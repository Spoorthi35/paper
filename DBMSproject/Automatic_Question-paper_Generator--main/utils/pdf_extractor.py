"""
PDF Question Extractor
----------------------
Utility to extract text from a PDF file and parse it into individual questions.
"""

from pypdf import PdfReader
import re


def extract_questions_from_pdf(pdf_stream):
    """
    Extracts text from a PDF stream and attempts to parse it into distinct questions.
    Looks for common numbering patterns (e.g., "1.", "Q1:", "1)").

    Args:
        pdf_stream: A file-like object containing the PDF data.

    Returns:
        list[str]: A list of extracted question texts.
    """
    reader = PdfReader(pdf_stream)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    return _parse_questions_from_text(full_text)


def _parse_questions_from_text(text):
    """
    Parses a block of text to identify and extract individual questions.
    Uses regex to split based on typical question numbering patterns.
    """
    # Pattern to match question numbers like "1.", "1)", "Q1.", "Q1:", "Q.1", etc.
    # It looks for start of line (or after some whitespace), optional 'Q' or 'Q.', digits, and then a separator (., ), or :)
    pattern = re.compile(r'(?:^|\n)\s*(?:Q\.?\s*)?(\d+)[\.\)\:]\s+', re.IGNORECASE)

    # Split the text based on the pattern
    parts = pattern.split(text)

    questions = []
    # parts will be like: [intro_text, q_num_1, q_text_1, q_num_2, q_text_2, ...]
    
    # If the first part is empty or just whitespace (meaning the text started with a question),
    # we can ignore it. Otherwise, it might be intro text which we'll ignore for now.
    
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            # q_num = parts[i]  # We don't necessarily need the extracted number
            q_text = parts[i+1].strip()
            
            # Clean up the question text (remove excessive newlines, etc.)
            q_text = re.sub(r'\s+', ' ', q_text).strip()
            
            if q_text:
                questions.append(q_text)

    # Fallback: if no patterns matched, just treat non-empty lines as potential questions
    if not questions:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # Simple heuristic: lines longer than 15 chars might be questions
        questions = [line for line in lines if len(line) > 15]

    return questions
