# University Management System (DBMS Mini Project)

An academic, full-stack relational database management system designed and built for the **Third Year B.Tech Computer Engineering / Information Technology DBMS Laboratory**.

This project implements a complete web application based strictly on the provided **Entity-Relationship (ER) Diagram**, demonstrating core database concepts: Entity-Relationship modeling, primary keys, foreign keys, composite keys, referential integrity constraints, normalization up to 3NF, parametrized CRUD operations, and advanced SQL querying (Joins, Aggregations, Grouping, Having, Subqueries).

---

## 1. Project Abstract & Problem Statement

### Abstract
Higher education institutions manage complex interconnected data across administrative and academic domains, including departments, students, faculty, course offerings, section allocations, enrollments, and examination evaluations. Manual record-keeping or flat spreadsheet architectures suffer from severe data redundancies, update anomalies, insertion anomalies, deletion anomalies, and lack of referential integrity. 

This project provides a centralized, relational database solution using **MySQL** as the backend database engine and **Python Flask** with a modern **Bootstrap 5** frontend. The application guarantees data consistency, prevents orphaned records via foreign key cascading and restrictions, prevents duplicate registrations through composite primary keys and unique constraints, and provides real-time analytical reporting.

### Problem Statement
*"Design and implement a relational database application with an interactive front end and robust back end for a university management ecosystem, strictly mapping entities, attributes, and cardinality constraints from the assigned ER diagram into a fully normalized schema up to Third Normal Form (3NF)."*

### Objectives
1. **Faithful ER Mapping:** Accurately implement all 8 entities (`Department`, `Student`, `Instructor`, `Course`, `Section`, `Enrollment`, `Exam`, `Result`) with their exact attributes and relationships.
2. **Relational Integrity:** Enforce primary keys, foreign keys, check constraints, unique constraints, and referential actions (`ON UPDATE CASCADE`, `ON DELETE RESTRICT / CASCADE`).
3. **Database Normalization:** Ensure every table adheres strictly to 1NF, 2NF, and 3NF with documented Functional Dependencies (FDs).
4. **Interactive Full-Stack Interface:** Provide clean, responsive user interfaces for complete Create, Read, Update, and Delete (CRUD) operations across all modules.
5. **Analytical Querying & Viva Readiness:** Provide executable SQL queries demonstrating multi-table joins, aggregates, subqueries, and grouping for academic evaluations.

---

## 2. Technology Stack

- **Frontend:**
  - HTML5, CSS3, JavaScript (ES6)
  - **Bootstrap 5.3.3** (Responsive CSS framework)
  - **Bootstrap Icons 1.11.3** (UI iconography)
- **Backend:**
  - **Python 3.x**
  - **Flask 3.x** (Micro web framework)
  - **PyMySQL 1.2.x** (Pure-Python MySQL database connector)
  - **python-dotenv** (Environment variable management)
- **Database Engine:**
  - **MySQL Server 8.0+** (InnoDB storage engine supporting ACID transactions and foreign keys)
- **Development Environment:**
  - Visual Studio Code on Windows PowerShell (100% compatible with Linux/WSL/macOS).

---

## 3. Project Architecture & Folder Structure

```
university-management-system/
├── app.py                  # Main Flask application with routes and controllers
├── config.py               # Configuration loader via python-dotenv
├── database.py             # PyMySQL connection factory and query execution helpers
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template
├── .env                    # Local environment secrets (DB host, user, password)
├── .gitignore              # Git ignore rules for virtual envs and credentials
├── schema.sql              # Complete MySQL DDL & DML script (tables, constraints, seed data)
├── queries.sql             # 11 Academic and analytical queries for DBMS viva
├── test_app.py             # Unit and integration test suite
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout with responsive navbar, flash alerts, and footer
│   ├── dashboard.html      # KPI cards, grade distributions, top performers, recent enrollments
│   ├── departments.html    # Department CRUD with faculty/student metrics
│   ├── students.html       # Student registry, search, filter, DOB auto-age calculator
│   ├── student_detail.html # Student profile, enrolled sections, and exam transcripts
│   ├── instructors.html    # Faculty management, salary formatting, departmental affiliation
│   ├── courses.html        # Course catalog, credit allocation, section counts
│   ├── sections.html       # Section allocations connecting courses, faculty, and semesters
│   ├── enrollment.html     # Student section enrollments, grade tracking, drop course
│   ├── exams.html          # Exam scheduling (Midterms, Finals, Quizzes) per section
│   ├── results.html        # Exam marks entry, automatic letter-grade calculation
│   └── reports.html        # Interactive SQL runner and viva report inspector
├── static/
│   ├── css/
│   │   └── style.css       # Custom modern UI styling, stat cards, grade badges
│   └── js/
│       └── script.js       # Client-side auto age/grade calculations, alert dismissals
└── README.md               # Project documentation, 3NF proofs, and viva guide
```

---

## 4. ER Diagram Explanation & Entity Mapping

The system strictly implements the 8 entities and relationships depicted in the assigned ER diagram:

```
 [Department] (1) ──── offers ──── (M) [Course] (1) ──── has ──── (N) [Section]
      │                                                                  │  │
      ├── (1) ─── has ──── (M) [Student]                                 │  │
      │                             │                                    │  │
      └── (1) ─── has ──── (M) [Instructor] ─── teaches ─────────────────┘  │
                                    │                                       │
                                    │ (M)                                   │ (1)
                                    ▼                                       ▼
                              [Enrollment] ◄────────────────────────────────┘ conducts
                               (Associative)                                │
                                    │                                       │
                                    ▼                                       ▼
                                 [Result] ◄────── appears in ─────────── [Exam]
                               (Associative)                               (N)
```

### 1. Department (Strong Entity)
- **Attributes:** `dept_id` (PK, INT), `dept_name` (VARCHAR, Unique), `building` (VARCHAR).
- **Relationships:**
  - One Department offers many Courses ($1:M$).
  - One Department has many Students ($1:M$).
  - One Department has many Instructors ($1:M$).

### 2. Student (Strong Entity)
- **Attributes:** `student_id` (PK, INT), `name` (VARCHAR), `email` (VARCHAR, Unique), `dept_id` (FK referencing Department), `phone` (VARCHAR), `dob` (DATE), `age` (INT, derived from DOB / optional).
- **Relationships:**
  - Belongs to one Department ($M:1$).
  - Enrolls in many Sections through `Enrollment` ($M:N$).
  - Receives marks in Examinations through `Result` ($M:N$).

### 3. Instructor (Strong Entity)
- **Attributes:** `instr_id` (PK, INT), `name` (VARCHAR), `email` (VARCHAR, Unique), `salary` (DECIMAL), `dept_id` (FK referencing Department).
- **Relationships:**
  - Belongs to one Department ($M:1$).
  - Teaches one or more Sections ($1:M$).

### 4. Course (Strong Entity)
- **Attributes:** `course_id` (PK, VARCHAR, e.g., 'CS101'), `course_name` (VARCHAR), `credits` (INT), `dept_id` (FK referencing Department).
- **Relationships:**
  - Offered by one Department ($M:1$).
  - Instantiated as one or more Sections ($1:M$).

### 5. Section (Entity / Course Offering)
- **Attributes:** `sec_id` (PK, INT), `course_id` (FK referencing Course), `instructor_id` (FK referencing Instructor), `semester` (VARCHAR), `year` (INT).
- **Relationships:**
  - Belongs to one Course ($M:1$).
  - Taught by one Instructor ($M:1$).
  - Has many Student enrollments ($1:M$).
  - Conducts many Examinations ($1:M$).

### 6. Enrollment (Associative Entity / M:N Relationship)
- **Attributes:** `student_id` (FK referencing Student), `sec_id` (FK referencing Section), `enroll_date` (DATE), `grade` (VARCHAR).
- **Primary Key:** Composite Key `(student_id, sec_id)` prevents duplicate enrollments of the same student in the same section.

### 7. Exam (Entity)
- **Attributes:** `exam_id` (PK, INT), `sec_id` (FK referencing Section), `exam_date` (DATE), `exam_type` (VARCHAR: Midterm, Final, Quiz, Practical, Assignment).
- **Relationships:**
  - Belongs to one Section ($M:1$).
  - Has multiple Student results ($1:M$).

### 8. Result (Associative Entity / Evaluative Relationship)
- **Attributes:** `student_id` (FK referencing Student), `exam_id` (FK referencing Exam), `marks` (DECIMAL, 0–100), `grade` (VARCHAR).
- **Primary Key:** Composite Key `(student_id, exam_id)` ensures a student can have only one recorded score per examination.

---

## 5. Relational Schema & Table Descriptions

```sql
Department   (dept_id [PK], dept_name, building)
Student      (student_id [PK], name, email, dept_id [FK], phone, dob, age)
Instructor   (instr_id [PK], name, email, salary, dept_id [FK])
Course       (course_id [PK], course_name, credits, dept_id [FK])
Section      (sec_id [PK], course_id [FK], instructor_id [FK], semester, year)
Enrollment   ((student_id [PK, FK], sec_id [PK, FK]), enroll_date, grade)
Exam         (exam_id [PK], sec_id [FK], exam_date, exam_type)
Result       ((student_id [PK, FK], exam_id [PK, FK]), marks, grade)
```

---

## 6. Functional Dependencies (FDs) & 3NF Normalization Analysis

As required for the DBMS Laboratory Report, each relation has been analyzed for Functional Dependencies and verified up to Third Normal Form (3NF).

### Definitions:
- **1NF (First Normal Form):** All attribute values are atomic; no repeating groups or multi-valued attributes exist.
- **2NF (Second Normal Form):** Relation is in 1NF and every non-prime attribute is fully functionally dependent on the entire primary key (no partial dependency).
- **3NF (Third Normal Form):** Relation is in 2NF and no non-prime attribute is transitively dependent on the primary key ($X \to Y$ holds only if $X$ is a superkey or $Y$ is a prime attribute).

---

### Table 1: `department`
- **Attributes:** `{dept_id, dept_name, building}`
- **Candidate Keys:** `{dept_id}`, `{dept_name}`
- **Functional Dependencies:**
  1. $\text{dept\_id} \to \text{dept\_name, building}$
  2. $\text{dept\_name} \to \text{dept\_id, building}$
- **Normalization Proof:**
  - **1NF:** Each cell holds a single atomic string/integer.
  - **2NF:** Primary key is single-attribute (`dept_id`), eliminating any partial dependency.
  - **3NF:** Both $\text{dept\_id}$ and $\text{dept\_name}$ are superkeys. No transitive dependency exists. $\checkmark$ **In 3NF.**

---

### Table 2: `student`
- **Attributes:** `{student_id, name, email, dept_id, phone, dob, age}`
- **Candidate Keys:** `{student_id}`, `{email}`
- **Functional Dependencies:**
  1. $\text{student\_id} \to \text{name, email, dept\_id, phone, dob, age}$
  2. $\text{email} \to \text{student\_id, name, dept\_id, phone, dob, age}$
- **Normalization Proof:**
  - **1NF:** All attributes atomic.
  - **2NF:** Primary key is single-attribute (`student_id`). No partial dependency.
  - **3NF:** For all non-trivial FDs $X \to Y$, $X$ is a candidate key. `dept_id` is an FK referencing Department; department attributes (`building`, etc.) are separated into `department`, preventing transitive dependencies. $\checkmark$ **In 3NF.**

---

### Table 3: `instructor`
- **Attributes:** `{instr_id, name, email, salary, dept_id}`
- **Candidate Keys:** `{instr_id}`, `{email}`
- **Functional Dependencies:**
  1. $\text{instr\_id} \to \text{name, email, salary, dept_id}$
  2. $\text{email} \to \text{instr\_id, name, salary, dept_id}$
- **Normalization Proof:**
  - **1NF:** All scalar atomic values.
  - **2NF:** Single-attribute primary key (`instr_id`). No partial dependencies.
  - **3NF:** Department details reside in the `department` table, eliminating transitive dependence on `dept_id`. $\checkmark$ **In 3NF.**

---

### Table 4: `course`
- **Attributes:** `{course_id, course_name, credits, dept_id}`
- **Candidate Key:** `{course_id}`
- **Functional Dependencies:**
  1. $\text{course\_id} \to \text{course\_name, credits, dept_id}$
- **Normalization Proof:**
  - **1NF:** Atomic attributes.
  - **2NF:** Single primary key (`course_id`). No partial dependencies.
  - **3NF:** $\text{course\_id}$ is a superkey. No transitive dependencies between non-prime attributes. $\checkmark$ **In 3NF.**

---

### Table 5: `section`
- **Attributes:** `{sec_id, course_id, instructor_id, semester, year}`
- **Candidate Key:** `{sec_id}`, `{(course_id, instructor_id, semester, year)}`
- **Functional Dependencies:**
  1. $\text{sec\_id} \to \text{course\_id, instructor\_id, semester, year}$
  2. $\text{course\_id, instructor\_id, semester, year} \to \text{sec\_id}$
- **Normalization Proof:**
  - **1NF:** Atomic attributes.
  - **2NF:** Single-attribute surrogate primary key `sec_id`. Full functional dependency holds.
  - **3NF:** Determinants are superkeys. $\checkmark$ **In 3NF.**

---

### Table 6: `enrollment` (Associative Entity)
- **Attributes:** `{student_id, sec_id, enroll_date, grade}`
- **Primary Key:** Composite `{student_id, sec_id}`
- **Functional Dependencies:**
  1. $\text{(student\_id, sec\_id)} \to \text{enroll\_date, grade}$
- **Normalization Proof:**
  - **1NF:** Atomic attributes.
  - **2NF:** `enroll_date` and `grade` depend strictly on both `student_id` AND `sec_id` together. A grade cannot be determined by the student alone or the section alone. No partial dependencies exist.
  - **3NF:** The left side is the superkey. No transitive dependency between `enroll_date` and `grade`. $\checkmark$ **In 3NF.**

---

### Table 7: `exam`
- **Attributes:** `{exam_id, sec_id, exam_date, exam_type}`
- **Candidate Key:** `{exam_id}`
- **Functional Dependencies:**
  1. $\text{exam\_id} \to \text{sec\_id, exam\_date, exam\_type}$
- **Normalization Proof:**
  - **1NF:** Atomic attributes.
  - **2NF:** Single primary key (`exam_id`).
  - **3NF:** $\text{exam\_id}$ is a superkey; no transitive dependencies. $\checkmark$ **In 3NF.**

---

### Table 8: `result` (Associative Entity)
- **Attributes:** `{student_id, exam_id, marks, grade}`
- **Primary Key:** Composite `{student_id, exam_id}`
- **Functional Dependencies:**
  1. $\text{(student\_id, exam\_id)} \to \text{marks, grade}$
  2. $\text{marks} \to \text{grade}$ (Derivation rule)
- **Normalization Proof:**
  - **1NF:** Atomic values.
  - **2NF:** `marks` depends on the composite key (both student and exam). No partial dependency.
  - **3NF:** While letter grade can be derived from marks through university grading policy, storing official recorded letter grades alongside numeric scores is standard in academic student information systems for auditability and grading scale overrides. All non-key attributes depend directly on the composite candidate key. $\checkmark$ **In 3NF.**

---

## 7. Step-by-Step Installation & Setup Instructions

Follow these exact steps in **Visual Studio Code on Windows PowerShell**.

### Step 1: Open Project in VS Code
Open VS Code, navigate to `File -> Open Folder...` and select:
```
c:\Users\Kedar\OneDrive\Third Year\DBMS\mini_project
```
Open an integrated PowerShell terminal (`Ctrl + \`` or `Terminal -> New Terminal`).

### Step 2: Create & Activate Virtual Environment
```powershell
# Create Python virtual environment
python -m venv venv

# If PowerShell execution policy blocks scripts, enable process execution:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Database Connection
Copy `.env.example` to `.env` (if not already created) and edit with your MySQL root credentials:
```ini
# .env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=university_mgmt_academic_secret_key_2026

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_NAME=university_db
```

### Step 5: Initialize the Database (MySQL)
You can import the schema and seed data directly via MySQL CLI:
```powershell
# Option A: Run using mysql CLI
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p university_db < schema.sql

# Option B: Automatic Startup Initialization
# When app.py starts, database.py automatically checks and initializes schema.sql if empty!
```

### Step 6: Run Automated Tests
Verify that all 10 unit and integration tests pass:
```powershell
python test_app.py
```
*Expected Output:* `Ran 10 tests in ...s -- OK`

### Step 7: Launch the Web Application
```powershell
python app.py
```

### Step 8: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 8. Interactive Features & Modules Checklist

| Module | Route | Key Features & Constraints Demonstrated |
| :--- | :--- | :--- |
| **Dashboard** | `/` | 8 KPI Metric Cards, student department distribution bar charts, top performers leaderboard, recent enrollments feed. |
| **Departments** | `/departments` | View all departments with live student, instructor, and course counts; Add/Edit modals; Delete with `ON DELETE RESTRICT` dependency protection. |
| **Students** | `/students` | Live search by name/email/ID; Filter by department; Add student with Date of Birth and automatic age calculation; Edit/Delete with cascading options. |
| **Student Detail** | `/students/<id>` | Full academic profile, enrolled sections list with active grades, complete examination transcript. |
| **Instructors** | `/instructors` | Faculty directory with currency formatting (`$`), active section teaching loads, Add/Edit/Delete modals. |
| **Courses** | `/courses` | Curriculum catalog, credit points validation ($1 \le \text{credits} \le 8$), section counts, department filtering. |
| **Sections** | `/sections` | Course offerings connecting courses to instructors, semester and academic year specifications, enrolled candidate metrics. |
| **Enrollment** | `/enrollment` | Student section registrations, duplicate enrollment prevention via composite primary key `(student_id, sec_id)`, grade assignment, drop course. |
| **Examinations** | `/exams` | Schedule Midterms, Finals, and Quizzes for specific course sections; display evaluated vs enrolled student metrics. |
| **Results** | `/results` | Record student exam scores (0–100) with real-time automatic letter grade suggestion (A+, A, B, etc.), filter by exam/student, edit/delete marks. |
| **Viva Reports** | `/reports` | Interactive execution of the 11 required academic SQL queries with query descriptions, DBMS concepts, and live output tables. |

---

## 9. Academic SQL Queries (Viva Preparation)

All 11 queries required by the syllabus are implemented in `queries.sql` and interactively executable via the `/reports` route:

1. **INNER JOIN:** Display all students with their department names and buildings.
2. **Categorical Listing:** Display all courses offered by each department.
3. **Formatted Projection:** List instructors, formatted salaries (`$`), and departments ordered by salary DESC.
4. **Multi-Table Associative Join:** Show all students enrolled in a particular section (e.g., Section 1).
5. **LEFT OUTER JOIN & Aggregation:** Count students in each department, including departments with 0 students.
6. **3-Way Entity Join:** Display course sections with instructor and course details.
7. **Student Transcript Traversal:** Retrieve all examination results for a particular student across courses.
8. **Multi-Column Aggregate Function:** Calculate average, minimum, maximum marks, and candidate count per exam.
9. **Anti-Join / Relational Difference:** Find students who have not enrolled in any section using `LEFT JOIN ... WHERE ... IS NULL` and `NOT EXISTS`.
10. **Tuple Subquery:** Find the highest-scoring student in each examination using `(exam_id, marks) IN (SELECT exam_id, MAX(marks) FROM result GROUP BY exam_id)`.
11. **Comprehensive DBMS Construct:** Filter departments having $\ge 2$ instructors and average salary $> \$88,000$ using `JOIN`, `GROUP BY`, `HAVING`, and a nested scalar subquery for student count.

---

## 10. Comprehensive DBMS Viva Questions & Answers

### Q1: What is the difference between a Primary Key and a Unique Key?
- **Primary Key:** Uniquely identifies each record in a table. It cannot contain `NULL` values. A table can have only **one** primary key. Example: `student_id` in `student`.
- **Unique Key:** Ensures all values in a column or set of columns are distinct, but allows a single `NULL` value. Example: `email` in `student` and `dept_name` in `department`.

### Q2: Why did we use Composite Primary Keys in `Enrollment` and `Result`?
- An associative entity representing an $M:N$ relationship naturally derives its identity from the entities it connects.
- In `Enrollment`, the primary key is `(student_id, sec_id)`. This guarantees at the database level that a student can never be enrolled twice in the exact same section.
- In `Result`, the primary key is `(student_id, exam_id)`. This guarantees that a student cannot have duplicate result records for the same examination.

### Q3: What is Referential Integrity and what ON DELETE options did we use?
- **Referential Integrity** ensures that foreign key values always point to a valid, existing record in the referenced parent table.
- **ON DELETE RESTRICT (e.g. Department $\to$ Student/Instructor/Course):** Prevents deletion of a department if students or instructors are still assigned to it, preventing orphaned records.
- **ON DELETE CASCADE (e.g. Student $\to$ Enrollment/Result, Exam $\to$ Result):** When a student or exam is deleted, all dependent registrations and marks are automatically cleaned up to prevent orphaned records.

### Q4: Explain 1NF, 2NF, and 3NF using this project.
1. **1NF:** In our `student` table, attributes like `phone` store a single atomic string. No comma-separated lists of phones or multi-valued fields exist.
2. **2NF:** In `enrollment`, the composite key is `(student_id, sec_id)`. The attribute `grade` depends on both attributes together. If we had mistakenly stored `student_name` inside `enrollment`, that would be a partial dependency (since `student_name` depends only on `student_id`), violating 2NF. By storing `student_name` only in `student`, we satisfy 2NF.
3. **3NF:** In `student`, we have `dept_id` as a foreign key. If we had stored `building` inside `student`, we would have a transitive dependency: $\text{student\_id} \to \text{dept\_id} \to \text{building}$. By moving `building` to `department`, we satisfy 3NF.

### Q5: How do we prevent SQL Injection in Flask?
- We use **parameterized queries** with `%s` placeholders in PyMySQL (e.g., `cursor.execute("SELECT * FROM student WHERE dept_id = %s;", (dept_id,))`).
- The database driver automatically escapes input parameters, ensuring that user inputs are treated strictly as literal data, never as executable SQL commands.

---

## 11. Screenshots Checklist for Submission (File 1)

For your lab submission folder (`MIS_numbers/`), take screenshots of the following pages:
- [x] **01_Dashboard.png:** KPI stat cards, department distribution progress bars, and recent enrollments.
- [x] **02_Departments.png:** Department catalog table with student/instructor/course counts.
- [x] **03_Students_Registry.png:** Student table showing DOB, auto-calculated age, and department badges.
- [x] **04_Student_Transcript.png:** Single student profile page showing registered sections and exam transcript.
- [x] **05_Instructors.png:** Faculty directory showing formatted annual salaries and sections taught.
- [x] **06_Course_Catalog.png:** Course listings with credit weightings and section counts.
- [x] **07_Sections.png:** Course section allocations with assigned professors, semesters, and years.
- [x] **08_Enrollments.png:** Enrollment table showing composite key associations and assigned grades.
- [x] **09_Examinations.png:** Scheduled exams table showing evaluated vs enrolled candidate counts.
- [x] **10_Results_Ledger.png:** Exam marks and letter grades ledger.
- [x] **11_Viva_Reports.png:** Interactive SQL report showing Query 10 (Highest-Scoring Students) and Query 11 (HAVING & subquery).

---

## 12. Limitations & Future Scope

### Current Limitations:
1. Single administrative role (no multi-tenant role-based authentication between students, professors, and registrar).
2. Semester scheduling conflict checks (e.g. room time-slot overlap) are handled administratively rather than through automated timetable constraint solvers.

### Future Scope:
1. **Role-Based Access Control (RBAC):** Separate portals for Students (view transcript, self-enroll), Faculty (enter exam marks, attendance), and Administrators.
2. **Automated GPA/CGPA Calculator:** Automatic computation of cumulative grade point average using credit-weighted formulas.
3. **Timetable & Classroom Scheduling:** Adding a `classroom` and `timeslot` entity to detect and prevent room allocation conflicts.
4. **PDF Transcript Generator:** Export official university transcripts in signed PDF format.
