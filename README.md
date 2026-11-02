# University Management System

A full-stack university administration system built with Python, Flask, MySQL, HTML, CSS, and Bootstrap.

The application manages the core academic records of a university, including departments, students, instructors, courses, sections, enrollments, examinations, and results.

## Features

- Complete CRUD operations for academic records
- Department-wise student, instructor, and course information
- Student profiles and academic examination records
- Course section and instructor allocation
- Duplicate enrollment prevention
- Examination scheduling and result management
- Automatic student age and letter-grade calculation
- Responsive university portal-inspired interface
- Parameterized database queries to help prevent SQL injection

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons
- **Backend:** Python 3, Flask
- **Database:** MySQL 8 or MariaDB
- **Database Driver:** PyMySQL
- **Configuration:** python-dotenv

## Database Design

The database is based on the project Entity-Relationship diagram and implements the following entities:

- Department
- Student
- Instructor
- Course
- Section
- Enrollment
- Exam
- Result

### Relationships

- A department manages multiple students, instructors, and courses.
- A course can have multiple sections.
- An instructor can teach multiple sections.
- Students and sections are connected through the `Enrollment` associative entity.
- Students and exams are connected through the `Result` associative entity.
- Composite primary keys are used for `Enrollment(student_id, sec_id)` and `Result(student_id, exam_id)`.

Foreign keys and cascading rules enforce referential integrity throughout the application.

## Project Structure

```text
.
├── app.py              # Flask application and routes
├── config.py           # Environment configuration
├── database.py         # Database connection and query helpers
├── schema.sql          # Database schema and seed data
├── queries.sql         # Supporting academic SQL queries
├── requirements.txt    # Python dependencies
├── test_app.py         # Flask application tests
├── static/
│   ├── css/style.css   # Custom application styles
│   └── js/script.js    # Client-side calculations and helpers
└── templates/          # Jinja2 templates
```

## Prerequisites

- Python 3.10 or newer
- MySQL Server 8.0 or compatible database server
- Git

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/kukadekn046-cmyk/University-DB-management.git
cd University-DB-management
```

### 2. Create and activate a virtual environment

**Windows**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
FLASK_APP=app.py
FLASK_DEBUG=1
SECRET_KEY=replace-with-a-random-secret-key

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=university_db
```

Do not commit the `.env` file or database credentials to GitHub.

### 5. Create and initialize the database

Create the database first if it does not exist:

```sql
CREATE DATABASE university_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Import the schema and sample data:

```bash
mysql -u root -p university_db < schema.sql
```

Alternatively, start the Flask application and allow its database initialization routine to prepare the schema.

### 6. Run the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Running Tests

```bash
python -m unittest test_app.py
```

The test suite checks the main application routes and CRUD workflows.

## Application Modules

| Module | Description |
| --- | --- |
| Dashboard | Academic statistics, top performers, department distribution, and recent enrollments |
| Departments | Department records and related academic counts |
| Students | Student registration, searching, editing, and profiles |
| Instructors | Faculty records and section assignments |
| Courses | Course catalog and credit information |
| Sections | Course offerings, instructors, semesters, and years |
| Enrollment | Student section registrations and grades |
| Examinations | Examination scheduling and course-section information |
| Results | Marks and letter-grade records |

## Database Tables

```text
department(dept_id, dept_name, building)
student(student_id, name, email, dept_id, phone, dob, age)
instructor(instr_id, name, email, salary, dept_id)
course(course_id, course_name, credits, dept_id)
section(sec_id, course_id, instructor_id, semester, year)
enrollment(student_id, sec_id, enroll_date, grade)
exam(exam_id, sec_id, exam_date, exam_type)
result(student_id, exam_id, marks, grade)
```

## Normalization

The schema follows Third Normal Form (3NF):

- All table attributes are atomic.
- Each table has a clearly defined primary key.
- Composite entities use full composite keys.
- Department attributes are not duplicated in student, instructor, or course records.
- Calculated or repeated relationship data is stored in its appropriate entity.

## Security Notes

- Keep database passwords in `.env`, not in source code.
- Use a unique random value for `SECRET_KEY`.
- Do not enable debug mode in production.
- Database operations should use parameterized queries.
- Configure HTTPS, access controls, and session management before public deployment.

## Available Documents

- [DBMS Project.docx](DBMS%20Project.docx) — project report
- [schema.sql](schema.sql) — database schema and seed data
- [queries.sql](queries.sql) — supporting SQL queries
- [University management ER diagram](university%20management%20ER%20%281%29.pdf) — ER diagram

## License

This project was developed for educational and academic purposes.
