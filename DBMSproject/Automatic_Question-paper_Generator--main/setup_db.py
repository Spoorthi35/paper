"""
Database Setup Script (SQLite version)
---------------------------------------
Creates the SmartQGen database and seeds sample data.
Usage: python setup_db.py
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'smartqgen.db')


def setup():
    """Create tables and seed data."""
    print("=" * 50)
    print("SmartQGen Database Setup (SQLite)")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # ── Create Tables ──
    c.execute("""CREATE TABLE IF NOT EXISTS Faculty (
        faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        department TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS Subject (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL UNIQUE,
        subject_name TEXT NOT NULL,
        semester INTEGER NOT NULL,
        department TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS QuestionBank (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        module_number INTEGER NOT NULL,
        marks INTEGER NOT NULL,
        difficulty_level TEXT NOT NULL DEFAULT 'Medium',
        co_mapping TEXT NOT NULL,
        po_mapping TEXT NOT NULL,
        last_used_date DATE DEFAULT NULL,
        added_by INTEGER DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
        FOREIGN KEY (added_by) REFERENCES Faculty(faculty_id) ON DELETE SET NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS ExamPaper (
        paper_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        faculty_id INTEGER NOT NULL,
        total_marks INTEGER NOT NULL,
        exam_type TEXT NOT NULL DEFAULT 'Internal Assessment',
        exam_date DATE NOT NULL,
        generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
        FOREIGN KEY (faculty_id) REFERENCES Faculty(faculty_id) ON DELETE CASCADE
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS PaperQuestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paper_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        question_order INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (paper_id) REFERENCES ExamPaper(paper_id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES QuestionBank(question_id) ON DELETE CASCADE,
        UNIQUE(paper_id, question_id)
    )""")
    print("[OK] Tables created.")

    # ── Seed Data ──
    c.execute("SELECT COUNT(*) FROM Faculty")
    if c.fetchone()[0] == 0:
        pwd = generate_password_hash('password123')
        c.executemany("INSERT INTO Faculty (name,email,password_hash,department) VALUES (?,?,?,?)", [
            ('Dr. Anil Kumar', 'anil.kumar@university.edu', pwd, 'Computer Science'),
            ('Prof. Meera Sharma', 'meera.sharma@university.edu', pwd, 'Computer Science'),
        ])
        print("[OK] Faculty seeded.")

    c.execute("SELECT COUNT(*) FROM Subject")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO Subject (subject_code,subject_name,semester,department) VALUES (?,?,?,?)", [
            ('CS301','Database Management Systems',3,'Computer Science'),
            ('CS302','Operating Systems',3,'Computer Science'),
            ('CS401','Computer Networks',4,'Computer Science'),
            ('CS402','Software Engineering',4,'Computer Science'),
        ])
        print("[OK] Subjects seeded.")

    c.execute("SELECT COUNT(*) FROM QuestionBank")
    if c.fetchone()[0] == 0:
        qs = [
            (1,'Define a Database Management System. Explain the advantages of DBMS over traditional file systems.',1,5,'Easy','CO1','PO1',1),
            (1,'Explain the three-level architecture of DBMS with a suitable diagram.',1,10,'Medium','CO1','PO1,PO2',1),
            (1,'Differentiate between data independence and data abstraction.',1,5,'Medium','CO1','PO1',1),
            (1,'List and explain different types of database users with examples.',1,5,'Easy','CO1','PO1',1),
            (1,'Discuss the role and responsibilities of a Database Administrator.',1,5,'Easy','CO1','PO1,PO3',1),
            (1,'Draw an ER diagram for a University Database with Student, Course, Instructor, Department.',2,10,'Medium','CO2','PO1,PO2',1),
            (1,'Explain Entity, Attribute, and Relationship in ER modeling with examples.',2,5,'Easy','CO2','PO1',1),
            (1,'Define Candidate Key, Primary Key, Foreign Key, and Super Key with examples.',2,10,'Medium','CO2','PO1,PO2',1),
            (1,'Convert the given ER diagram into relational schema and identify functional dependencies.',2,10,'Hard','CO2','PO1,PO2,PO3',1),
            (1,'Explain weak entity sets and partial keys with a suitable example.',2,5,'Medium','CO2','PO1',1),
            (1,'Write SQL queries to: Create a table, Insert data, Update records, Delete records.',3,10,'Medium','CO3','PO1,PO3',1),
            (1,'Explain JOIN operations in SQL: INNER, LEFT, RIGHT, FULL JOIN with examples.',3,10,'Medium','CO3','PO1,PO3',1),
            (1,'Write SQL queries using aggregate functions with GROUP BY and HAVING clauses.',3,10,'Hard','CO3','PO1,PO3',1),
            (1,'Explain subqueries. Write examples of correlated and non-correlated subqueries.',3,5,'Hard','CO3','PO1,PO3',1),
            (1,'Define views in SQL. Explain advantages and limitations of views.',3,5,'Easy','CO3','PO1',1),
            (1,'Explain Normalization: 1NF, 2NF, and 3NF with examples.',4,10,'Medium','CO4','PO1,PO2',1),
            (1,'Define BCNF. How does it differ from 3NF? Provide an example.',4,10,'Hard','CO4','PO1,PO2',1),
            (1,'What is functional dependency? Explain full, partial, and transitive FDs.',4,5,'Medium','CO4','PO1',1),
            (1,'Explain lossless join decomposition and dependency preservation.',4,10,'Hard','CO4','PO1,PO2,PO3',1),
            (1,'What are anomalies in unnormalized relations? Explain insertion, deletion, update anomalies.',4,5,'Easy','CO4','PO1',1),
            (1,'Explain the ACID properties of a transaction with examples.',5,5,'Easy','CO5','PO1',1),
            (1,'Describe concurrency control protocols: Lock-based, Timestamp-based, Optimistic.',5,10,'Hard','CO5','PO1,PO2,PO3',1),
            (1,'What is a deadlock? Explain deadlock prevention and detection techniques.',5,10,'Medium','CO5','PO1,PO2',1),
            (1,'Explain the Two-Phase Locking (2PL) protocol and its variants.',5,5,'Medium','CO5','PO1,PO2',1),
            (1,'Define serializability. Explain conflict and view serializability.',5,10,'Hard','CO5','PO1,PO2,PO3',1),
            (2,'Define an Operating System. Explain different types with examples.',1,5,'Easy','CO1','PO1',1),
            (2,'Explain process and process states. Draw the state transition diagram.',1,10,'Medium','CO1','PO1,PO2',1),
            (2,'Compare preemptive and non-preemptive scheduling algorithms.',2,5,'Medium','CO2','PO1,PO2',1),
            (2,'Explain Round Robin scheduling with a numerical example.',2,10,'Medium','CO2','PO1,PO2,PO3',1),
            (2,'What is a critical section problem? Explain Petersons solution.',3,10,'Hard','CO3','PO1,PO2,PO3',1),
            (2,'Explain virtual memory and demand paging with examples.',4,10,'Medium','CO4','PO1,PO2',1),
            (2,'Describe page replacement algorithms: FIFO, LRU, Optimal.',4,10,'Hard','CO4','PO1,PO2,PO3',1),
            (2,'Explain disk scheduling algorithms: FCFS, SSTF, SCAN, C-SCAN.',5,10,'Hard','CO5','PO1,PO2,PO3',1),
            (3,'Explain the OSI reference model with functions of each layer.',1,10,'Medium','CO1','PO1,PO2',2),
            (3,'Compare OSI and TCP/IP reference models.',1,5,'Easy','CO1','PO1',2),
            (3,'Explain different types of network topologies.',1,5,'Easy','CO1','PO1',2),
            (3,'Describe the sliding window protocol: Go-Back-N and Selective Repeat.',2,10,'Hard','CO2','PO1,PO2,PO3',2),
            (3,'Explain subnetting. Given IP 192.168.1.0/24, create 4 subnets.',3,10,'Hard','CO3','PO1,PO3',2),
            (3,'Describe the working of DNS with iterative and recursive queries.',4,5,'Medium','CO4','PO1,PO2',2),
            (3,'Explain the TCP three-way handshake mechanism with a diagram.',3,5,'Medium','CO3','PO1,PO2',2),
            (4,'Explain SDLC. Describe different SDLC models.',1,10,'Medium','CO1','PO1,PO2',2),
            (4,'Compare Waterfall and Agile development methodologies.',1,5,'Medium','CO1','PO1,PO2',2),
            (4,'Explain functional and non-functional requirements with examples.',2,10,'Medium','CO2','PO1,PO2',2),
            (4,'Draw and explain a Use Case diagram for an Online Shopping System.',2,10,'Medium','CO2','PO1,PO2,PO3',2),
            (4,'Explain Black-box and White-box testing techniques.',4,10,'Medium','CO4','PO1,PO2',2),
            (4,'Explain levels of testing: Unit, Integration, System, Acceptance.',4,5,'Easy','CO4','PO1',2),
        ]
        c.executemany(
            "INSERT INTO QuestionBank (subject_id,question_text,module_number,marks,difficulty_level,co_mapping,po_mapping,added_by) VALUES (?,?,?,?,?,?,?,?)",
            qs
        )
        print(f"[OK] {len(qs)} questions seeded.")

    c.execute("SELECT COUNT(*) FROM ExamPaper")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO ExamPaper (subject_id,faculty_id,total_marks,exam_type,exam_date) VALUES (?,?,?,?,?)",
                  (1,1,30,'Internal Assessment 1','2024-09-15'))
        p1 = c.lastrowid
        c.execute("INSERT INTO ExamPaper (subject_id,faculty_id,total_marks,exam_type,exam_date) VALUES (?,?,?,?,?)",
                  (1,1,20,'Internal Assessment 2','2024-10-20'))
        p2 = c.lastrowid
        for qid, order in [(1,1),(6,2),(11,3),(18,4)]:
            c.execute("INSERT INTO PaperQuestions (paper_id,question_id,question_order) VALUES (?,?,?)", (p1,qid,order))
        for qid, order in [(21,1),(15,2),(16,3)]:
            c.execute("INSERT INTO PaperQuestions (paper_id,question_id,question_order) VALUES (?,?,?)", (p2,qid,order))
        c.execute("UPDATE QuestionBank SET last_used_date='2024-09-15' WHERE question_id IN (1,6,11,18)")
        c.execute("UPDATE QuestionBank SET last_used_date='2024-10-20' WHERE question_id IN (21,15,16)")
        print("[OK] Sample papers seeded.")

    conn.commit()
    conn.close()

    print()
    print("=" * 50)
    print("Setup complete!")
    print(f"Database: {DB_PATH}")
    print()
    print("Demo Login Credentials:")
    print("  Email:    anil.kumar@university.edu")
    print("  Password: password123")
    print()
    print("Run the app: python app.py")
    print("=" * 50)


if __name__ == '__main__':
    setup()
