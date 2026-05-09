# SmartQGen – Intelligent Internal Assessment Question Paper Generator

A full-stack DBMS mini project for faculty to generate Internal Assessment question papers using a structured question bank with academic constraints.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Database**: MySQL
- **PDF**: fpdf2

## Features

- Faculty login/logout with session management
- Modern dashboard with statistics
- Question bank CRUD (Add, Edit, Delete, Search, Filter)
- Semi-automatic paper generation with difficulty balancing
- Duplicate question prevention (last 2 years)
- CO/PO mapping support
- PDF export with professional formatting
- Previous papers archive
- Responsive, mobile-friendly design

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MySQL Server
- pip

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Database

Run in MySQL:

```sql
source schema.sql;
source seed_data.sql;
```

### 4. Seed Faculty Passwords

```bash
python app.py --seed-passwords
```

### 5. Configure Database

Edit `config.py` with your MySQL credentials:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''      # your MySQL password
MYSQL_DATABASE = 'smartqgen'
```

### 6. Run the Application

```bash
python app.py
```

Visit: http://localhost:5000

### Demo Login

- **Email**: anil.kumar@university.edu
- **Password**: password123

## Database Schema

| Table | Description |
|-------|-------------|
| Faculty | Faculty member credentials and profile |
| Subject | Subject/course information |
| QuestionBank | Central question repository with metadata |
| ExamPaper | Generated question paper metadata |
| PaperQuestions | Junction table linking papers to questions |

## Project Structure

```
├── app.py                  # Flask application entry point
├── config.py               # Configuration settings
├── schema.sql              # Database schema
├── seed_data.sql           # Sample data
├── requirements.txt        # Python dependencies
├── routes/                 # Flask route blueprints
│   ├── auth.py             # Authentication routes
│   ├── dashboard.py        # Dashboard route
│   ├── questions.py        # Question bank CRUD
│   └── papers.py           # Paper generation & archive
├── utils/                  # Utility modules
│   ├── db.py               # Database helper
│   ├── paper_generator.py  # Paper generation algorithm
│   └── pdf_export.py       # PDF generation
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, images
└── README.md
```
