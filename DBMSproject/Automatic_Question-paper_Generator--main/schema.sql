-- ============================================================
-- SmartQGen Database Schema
-- Intelligent Internal Assessment Question Paper Generator
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS smartqgen;
USE smartqgen;

-- ============================================================
-- Table: Faculty
-- Stores faculty member credentials and profile information.
-- ============================================================
CREATE TABLE IF NOT EXISTS Faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_faculty_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Table: Subject
-- Stores subject/course information linked to departments.
-- ============================================================
CREATE TABLE IF NOT EXISTS Subject (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(150) NOT NULL,
    semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
    department VARCHAR(100) NOT NULL,

    INDEX idx_subject_code (subject_code),
    INDEX idx_subject_dept (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Table: QuestionBank
-- Central question repository with metadata for paper generation.
-- ============================================================
CREATE TABLE IF NOT EXISTS QuestionBank (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    question_text TEXT NOT NULL,
    module_number INT NOT NULL CHECK (module_number BETWEEN 1 AND 6),
    marks INT NOT NULL CHECK (marks > 0),
    difficulty_level ENUM('Easy', 'Medium', 'Hard') NOT NULL DEFAULT 'Medium',
    co_mapping VARCHAR(50) NOT NULL COMMENT 'Course Outcome mapping e.g. CO1, CO2',
    po_mapping VARCHAR(50) NOT NULL COMMENT 'Program Outcome mapping e.g. PO1, PO3',
    last_used_date DATE DEFAULT NULL,
    added_by INT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (added_by) REFERENCES Faculty(faculty_id) ON DELETE SET NULL,

    INDEX idx_qb_subject (subject_id),
    INDEX idx_qb_module (module_number),
    INDEX idx_qb_difficulty (difficulty_level),
    INDEX idx_qb_last_used (last_used_date),
    INDEX idx_qb_marks (marks)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Table: ExamPaper
-- Stores metadata for each generated question paper.
-- ============================================================
CREATE TABLE IF NOT EXISTS ExamPaper (
    paper_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    faculty_id INT NOT NULL,
    total_marks INT NOT NULL CHECK (total_marks > 0),
    exam_type VARCHAR(50) NOT NULL DEFAULT 'Internal Assessment',
    exam_date DATE NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id) ON DELETE CASCADE,

    INDEX idx_ep_subject (subject_id),
    INDEX idx_ep_faculty (faculty_id),
    INDEX idx_ep_date (exam_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- Table: PaperQuestions
-- Junction table linking papers to their selected questions.
-- ============================================================
CREATE TABLE IF NOT EXISTS PaperQuestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    question_id INT NOT NULL,
    question_order INT NOT NULL DEFAULT 1,

    FOREIGN KEY (paper_id) REFERENCES ExamPaper(paper_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES QuestionBank(question_id) ON DELETE CASCADE,

    UNIQUE KEY uk_paper_question (paper_id, question_id),
    INDEX idx_pq_paper (paper_id),
    INDEX idx_pq_question (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
