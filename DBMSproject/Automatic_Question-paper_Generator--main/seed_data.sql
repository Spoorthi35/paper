-- ============================================================
-- SmartQGen Sample Data
-- Run this AFTER schema.sql to populate tables with test data.
-- ============================================================

USE smartqgen;

-- ============================================================
-- Faculty (password for both: "password123")
-- Hash generated using werkzeug.security.generate_password_hash
-- ============================================================
INSERT INTO Faculty (name, email, password_hash, department) VALUES
('Dr. Anil Kumar', 'anil.kumar@university.edu',
 'scrypt:32768:8:1$SEEDHASH$abc123fakehashwillbereplacedbyapp', 'Computer Science'),
('Prof. Meera Sharma', 'meera.sharma@university.edu',
 'scrypt:32768:8:1$SEEDHASH$abc123fakehashwillbereplacedbyapp', 'Computer Science');

-- ============================================================
-- Subjects
-- ============================================================
INSERT INTO Subject (subject_code, subject_name, semester, department) VALUES
('CS301', 'Database Management Systems', 3, 'Computer Science'),
('CS302', 'Operating Systems', 3, 'Computer Science'),
('CS401', 'Computer Networks', 4, 'Computer Science'),
('CS402', 'Software Engineering', 4, 'Computer Science');

-- ============================================================
-- QuestionBank – DBMS (subject_id = 1)
-- ============================================================
INSERT INTO QuestionBank (subject_id, question_text, module_number, marks, difficulty_level, co_mapping, po_mapping, added_by) VALUES
-- Module 1: Introduction to DBMS
(1, 'Define a Database Management System. Explain the advantages of DBMS over traditional file systems.', 1, 5, 'Easy', 'CO1', 'PO1', 1),
(1, 'Explain the three-level architecture of DBMS (External, Conceptual, Internal) with a suitable diagram.', 1, 10, 'Medium', 'CO1', 'PO1,PO2', 1),
(1, 'Differentiate between data independence and data abstraction. Explain logical and physical data independence.', 1, 5, 'Medium', 'CO1', 'PO1', 1),
(1, 'List and explain different types of database users with examples.', 1, 5, 'Easy', 'CO1', 'PO1', 1),
(1, 'Discuss the role of a Database Administrator (DBA). What are the responsibilities of a DBA?', 1, 5, 'Easy', 'CO1', 'PO1,PO3', 1),

-- Module 2: ER Model & Relational Model
(1, 'Draw an ER diagram for a University Database with entities: Student, Course, Instructor, and Department.', 2, 10, 'Medium', 'CO2', 'PO1,PO2', 1),
(1, 'Explain the concepts of Entity, Attribute, and Relationship in ER modeling with examples.', 2, 5, 'Easy', 'CO2', 'PO1', 1),
(1, 'Define the following with examples: (a) Candidate Key (b) Primary Key (c) Foreign Key (d) Super Key.', 2, 10, 'Medium', 'CO2', 'PO1,PO2', 1),
(1, 'Convert the given ER diagram into relational schema and identify all functional dependencies.', 2, 10, 'Hard', 'CO2', 'PO1,PO2,PO3', 1),
(1, 'Explain weak entity sets and partial keys with a suitable example.', 2, 5, 'Medium', 'CO2', 'PO1', 1),

-- Module 3: SQL
(1, 'Write SQL queries to: (a) Create a table with constraints (b) Insert data (c) Update records (d) Delete records.', 3, 10, 'Medium', 'CO3', 'PO1,PO3', 1),
(1, 'Explain different types of JOIN operations in SQL with examples: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN.', 3, 10, 'Medium', 'CO3', 'PO1,PO3', 1),
(1, 'Write SQL queries using aggregate functions (COUNT, SUM, AVG, MAX, MIN) with GROUP BY and HAVING clauses.', 3, 10, 'Hard', 'CO3', 'PO1,PO3', 1),
(1, 'Explain the concept of subqueries (nested queries). Write examples of correlated and non-correlated subqueries.', 3, 5, 'Hard', 'CO3', 'PO1,PO3', 1),
(1, 'Define views in SQL. Explain the advantages and limitations of views.', 3, 5, 'Easy', 'CO3', 'PO1', 1),

-- Module 4: Normalization
(1, 'Explain the concept of Normalization. Why is it necessary? Discuss 1NF, 2NF, and 3NF with examples.', 4, 10, 'Medium', 'CO4', 'PO1,PO2', 1),
(1, 'Define Boyce-Codd Normal Form (BCNF). How does it differ from 3NF? Provide an example.', 4, 10, 'Hard', 'CO4', 'PO1,PO2', 1),
(1, 'What is functional dependency? Explain full, partial, and transitive functional dependencies.', 4, 5, 'Medium', 'CO4', 'PO1', 1),
(1, 'Explain the concept of lossless join decomposition and dependency preservation with examples.', 4, 10, 'Hard', 'CO4', 'PO1,PO2,PO3', 1),
(1, 'What are the anomalies in unnormalized relations? Explain insertion, deletion, and update anomalies.', 4, 5, 'Easy', 'CO4', 'PO1', 1),

-- Module 5: Transaction Management
(1, 'Explain the ACID properties of a transaction with suitable examples.', 5, 5, 'Easy', 'CO5', 'PO1', 1),
(1, 'Describe different concurrency control protocols: Lock-based, Timestamp-based, and Optimistic protocols.', 5, 10, 'Hard', 'CO5', 'PO1,PO2,PO3', 1),
(1, 'What is a deadlock? Explain deadlock prevention and detection techniques in DBMS.', 5, 10, 'Medium', 'CO5', 'PO1,PO2', 1),
(1, 'Explain the Two-Phase Locking (2PL) protocol. What are its variants?', 5, 5, 'Medium', 'CO5', 'PO1,PO2', 1),
(1, 'Define serializability. Explain conflict serializability and view serializability.', 5, 10, 'Hard', 'CO5', 'PO1,PO2,PO3', 1);

-- ============================================================
-- QuestionBank – Operating Systems (subject_id = 2)
-- ============================================================
INSERT INTO QuestionBank (subject_id, question_text, module_number, marks, difficulty_level, co_mapping, po_mapping, added_by) VALUES
(2, 'Define an Operating System. Explain the different types of operating systems with examples.', 1, 5, 'Easy', 'CO1', 'PO1', 1),
(2, 'Explain the concept of process and process states. Draw and explain the process state transition diagram.', 1, 10, 'Medium', 'CO1', 'PO1,PO2', 1),
(2, 'Compare and contrast preemptive and non-preemptive scheduling algorithms.', 2, 5, 'Medium', 'CO2', 'PO1,PO2', 1),
(2, 'Explain the Round Robin scheduling algorithm with a numerical example. Discuss its advantages and disadvantages.', 2, 10, 'Medium', 'CO2', 'PO1,PO2,PO3', 1),
(2, 'What is a critical section problem? Explain Peterson''s solution for the critical section problem.', 3, 10, 'Hard', 'CO3', 'PO1,PO2,PO3', 1),
(2, 'Explain the concept of virtual memory. Discuss demand paging with suitable examples.', 4, 10, 'Medium', 'CO4', 'PO1,PO2', 1),
(2, 'Describe different page replacement algorithms: FIFO, LRU, and Optimal. Compare their performance.', 4, 10, 'Hard', 'CO4', 'PO1,PO2,PO3', 1),
(2, 'Explain different disk scheduling algorithms: FCFS, SSTF, SCAN, and C-SCAN with numerical examples.', 5, 10, 'Hard', 'CO5', 'PO1,PO2,PO3', 1);

-- ============================================================
-- QuestionBank – Computer Networks (subject_id = 3)
-- ============================================================
INSERT INTO QuestionBank (subject_id, question_text, module_number, marks, difficulty_level, co_mapping, po_mapping, added_by) VALUES
(3, 'Explain the OSI reference model with the functions of each layer.', 1, 10, 'Medium', 'CO1', 'PO1,PO2', 2),
(3, 'Compare OSI and TCP/IP reference models. List the similarities and differences.', 1, 5, 'Easy', 'CO1', 'PO1', 2),
(3, 'Explain different types of network topologies with their advantages and disadvantages.', 1, 5, 'Easy', 'CO1', 'PO1', 2),
(3, 'Describe the sliding window protocol. Explain Go-Back-N and Selective Repeat protocols.', 2, 10, 'Hard', 'CO2', 'PO1,PO2,PO3', 2),
(3, 'Explain the concept of subnetting. Solve: Given IP 192.168.1.0/24, create 4 subnets.', 3, 10, 'Hard', 'CO3', 'PO1,PO3', 2),
(3, 'Describe the working of DNS. Explain iterative and recursive DNS queries.', 4, 5, 'Medium', 'CO4', 'PO1,PO2', 2),
(3, 'Explain the TCP three-way handshake mechanism with a diagram.', 3, 5, 'Medium', 'CO3', 'PO1,PO2', 2);

-- ============================================================
-- QuestionBank – Software Engineering (subject_id = 4)
-- ============================================================
INSERT INTO QuestionBank (subject_id, question_text, module_number, marks, difficulty_level, co_mapping, po_mapping, added_by) VALUES
(4, 'Explain the Software Development Life Cycle (SDLC). Describe different SDLC models.', 1, 10, 'Medium', 'CO1', 'PO1,PO2', 2),
(4, 'Compare Waterfall and Agile development methodologies. When would you prefer one over the other?', 1, 5, 'Medium', 'CO1', 'PO1,PO2', 2),
(4, 'Explain functional and non-functional requirements with examples. How do you document requirements?', 2, 10, 'Medium', 'CO2', 'PO1,PO2', 2),
(4, 'Draw and explain a Use Case diagram for an Online Shopping System.', 2, 10, 'Medium', 'CO2', 'PO1,PO2,PO3', 2),
(4, 'What is software testing? Explain Black-box and White-box testing techniques.', 4, 10, 'Medium', 'CO4', 'PO1,PO2', 2),
(4, 'Explain different levels of software testing: Unit, Integration, System, and Acceptance testing.', 4, 5, 'Easy', 'CO4', 'PO1', 2);

-- ============================================================
-- Sample Exam Papers
-- ============================================================
INSERT INTO ExamPaper (subject_id, faculty_id, total_marks, exam_type, exam_date) VALUES
(1, 1, 30, 'Internal Assessment 1', '2024-09-15'),
(1, 1, 20, 'Internal Assessment 2', '2024-10-20');

-- Link questions to Paper 1 (30 marks from DBMS)
INSERT INTO PaperQuestions (paper_id, question_id, question_order) VALUES
(1, 1, 1),   -- 5 marks
(1, 6, 2),   -- 10 marks
(1, 11, 3),  -- 10 marks
(1, 18, 4);  -- 5 marks
-- Total = 30 marks

-- Link questions to Paper 2 (20 marks from DBMS)
INSERT INTO PaperQuestions (paper_id, question_id, question_order) VALUES
(2, 21, 1),  -- 5 marks
(2, 15, 2),  -- 5 marks
(2, 16, 3);  -- 10 marks
-- Total = 20 marks

-- Update last_used_date for questions used in papers
UPDATE QuestionBank SET last_used_date = '2024-09-15' WHERE question_id IN (1, 6, 11, 18);
UPDATE QuestionBank SET last_used_date = '2024-10-20' WHERE question_id IN (21, 15, 16);
