import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pymysql
from config import Config
from database import execute_query, init_db

app = Flask(__name__)
app.config.from_object(Config)

# Helper function to compute age from DOB
def calculate_age(dob_str):
    if not dob_str:
        return None
    try:
        born = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = datetime.date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except Exception:
        return None

# Helper function to compute grade from marks
def compute_grade(marks):
    try:
        m = float(marks)
        if m >= 90: return 'A+'
        if m >= 80: return 'A'
        if m >= 70: return 'B+'
        if m >= 60: return 'B'
        if m >= 50: return 'C'
        if m >= 40: return 'D'
        return 'F'
    except Exception:
        return 'N/A'

# Helper function to extract user-friendly error messages from MySQL exceptions
def parse_db_error(e):
    msg = str(e)
    if 'Duplicate entry' in msg:
        if 'email' in msg:
            return 'A record with this email address already exists. Please use a unique email.'
        if 'dept_name' in msg:
            return 'A department with this name already exists.'
        if 'PRIMARY' in msg:
            return 'A record with this primary key or combination already exists.'
        return 'Duplicate record detected. Please verify your input.'
    if 'a foreign key constraint fails' in msg:
        if 'DELETE' in msg.upper() or 'REFERENCE' in msg.upper():
            return 'Cannot delete this record because other records depend on it (Referential Integrity Constraint).'
        return 'The selected related record (Foreign Key) does not exist.'
    if 'CHECK' in msg.upper() or 'CONSTRAINT' in msg.upper():
        return 'Input value violated database check constraint (e.g. salary > 0 or marks between 0 and 100).'
    return f'Database Error: {msg}'

# =============================================================================
# 1. DASHBOARD ROUTE
# =============================================================================
@app.route('/')
def dashboard():
    stats = {
        'students': execute_query("SELECT COUNT(*) AS c FROM student;", fetch='value') or 0,
        'departments': execute_query("SELECT COUNT(*) AS c FROM department;", fetch='value') or 0,
        'instructors': execute_query("SELECT COUNT(*) AS c FROM instructor;", fetch='value') or 0,
        'courses': execute_query("SELECT COUNT(*) AS c FROM course;", fetch='value') or 0,
        'sections': execute_query("SELECT COUNT(*) AS c FROM section;", fetch='value') or 0,
        'exams': execute_query("SELECT COUNT(*) AS c FROM exam;", fetch='value') or 0,
        'enrollments': execute_query("SELECT COUNT(*) AS c FROM enrollment;", fetch='value') or 0,
        'results': execute_query("SELECT COUNT(*) AS c FROM result;", fetch='value') or 0,
    }

    # Department distribution for chart/summary
    dept_distribution = execute_query("""
        SELECT d.dept_name, COUNT(s.student_id) AS student_count
        FROM department d
        LEFT JOIN student s ON d.dept_id = s.dept_id
        GROUP BY d.dept_id, d.dept_name
        ORDER BY student_count DESC;
    """, fetch='all')

    # Top performing students
    top_students = execute_query("""
        SELECT s.student_id, s.name, d.dept_name, 
               ROUND(AVG(r.marks), 2) AS avg_marks,
               COUNT(r.exam_id) AS exams_taken
        FROM student s
        INNER JOIN department d ON s.dept_id = d.dept_id
        INNER JOIN result r ON s.student_id = r.student_id
        GROUP BY s.student_id, s.name, d.dept_name
        ORDER BY avg_marks DESC
        LIMIT 5;
    """, fetch='all')

    # Recent enrollments
    recent_enrollments = execute_query("""
        SELECT s.name AS student_name, c.course_id, c.course_name, sec.semester, sec.year, e.enroll_date
        FROM enrollment e
        INNER JOIN student s ON e.student_id = s.student_id
        INNER JOIN section sec ON e.sec_id = sec.sec_id
        INNER JOIN course c ON sec.course_id = c.course_id
        ORDER BY e.enroll_date DESC, e.created_at DESC
        LIMIT 5;
    """, fetch='all')

    return render_template(
        'dashboard.html',
        stats=stats,
        dept_distribution=dept_distribution,
        top_students=top_students,
        recent_enrollments=recent_enrollments
    )

# =============================================================================
# 2. DEPARTMENTS MODULE
# =============================================================================
@app.route('/departments')
def list_departments():
    departments = execute_query("""
        SELECT 
            d.dept_id,
            d.dept_name,
            d.building,
            (SELECT COUNT(*) FROM student s WHERE s.dept_id = d.dept_id) AS student_count,
            (SELECT COUNT(*) FROM instructor i WHERE i.dept_id = d.dept_id) AS instructor_count,
            (SELECT COUNT(*) FROM course c WHERE c.dept_id = d.dept_id) AS course_count
        FROM department d
        ORDER BY d.dept_id ASC;
    """, fetch='all')
    return render_template('departments.html', departments=departments)

@app.route('/departments/add', methods=['POST'])
def add_department():
    dept_name = request.form.get('dept_name', '').strip()
    building = request.form.get('building', '').strip()

    if not dept_name or not building:
        flash('Department Name and Building are required.', 'danger')
        return redirect(url_for('list_departments'))

    try:
        execute_query(
            "INSERT INTO department (dept_name, building) VALUES (%s, %s);",
            (dept_name, building),
            commit=True
        )
        flash(f'Department "{dept_name}" added successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_departments'))

@app.route('/departments/edit/<int:dept_id>', methods=['POST'])
def edit_department(dept_id):
    dept_name = request.form.get('dept_name', '').strip()
    building = request.form.get('building', '').strip()

    if not dept_name or not building:
        flash('Department Name and Building are required.', 'danger')
        return redirect(url_for('list_departments'))

    try:
        execute_query(
            "UPDATE department SET dept_name = %s, building = %s WHERE dept_id = %s;",
            (dept_name, building, dept_id),
            commit=True
        )
        flash(f'Department #{dept_id} updated successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_departments'))

@app.route('/departments/delete/<int:dept_id>', methods=['POST'])
def delete_department(dept_id):
    try:
        execute_query("DELETE FROM department WHERE dept_id = %s;", (dept_id,), commit=True)
        flash(f'Department #{dept_id} deleted successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')
    return redirect(url_for('list_departments'))

# =============================================================================
# 3. STUDENTS MODULE
# =============================================================================
@app.route('/students')
def list_students():
    search = request.args.get('search', '').strip()
    dept_filter = request.args.get('dept_id', '').strip()

    query = """
        SELECT s.*, d.dept_name, d.building
        FROM student s
        INNER JOIN department d ON s.dept_id = d.dept_id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (s.name LIKE %s OR s.email LIKE %s OR CAST(s.student_id AS CHAR) LIKE %s)"
        like_term = f"%{search}%"
        params.extend([like_term, like_term, like_term])

    if dept_filter:
        query += " AND s.dept_id = %s"
        params.append(dept_filter)

    query += " ORDER BY s.student_id ASC;"

    students = execute_query(query, tuple(params), fetch='all')
    departments = execute_query("SELECT dept_id, dept_name FROM department ORDER BY dept_name ASC;", fetch='all')
    return render_template('students.html', students=students, departments=departments, search=search, selected_dept=dept_filter)

@app.route('/students/add', methods=['POST'])
def add_student():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    dept_id = request.form.get('dept_id', '').strip()
    phone = request.form.get('phone', '').strip() or None
    dob = request.form.get('dob', '').strip() or None
    age_input = request.form.get('age', '').strip()

    if not name or not email or not dept_id:
        flash('Name, Email, and Department are required.', 'danger')
        return redirect(url_for('list_students'))

    # Derive age from DOB or use manual input
    age = calculate_age(dob) if dob else (int(age_input) if age_input.isdigit() else None)

    try:
        execute_query(
            """
            INSERT INTO student (name, email, dept_id, phone, dob, age)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (name, email, dept_id, phone, dob, age),
            commit=True
        )
        flash(f'Student "{name}" registered successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_students'))

@app.route('/students/edit/<int:student_id>', methods=['POST'])
def edit_student(student_id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    dept_id = request.form.get('dept_id', '').strip()
    phone = request.form.get('phone', '').strip() or None
    dob = request.form.get('dob', '').strip() or None
    age_input = request.form.get('age', '').strip()

    if not name or not email or not dept_id:
        flash('Name, Email, and Department are required.', 'danger')
        return redirect(url_for('list_students'))

    age = calculate_age(dob) if dob else (int(age_input) if age_input.isdigit() else None)

    try:
        execute_query(
            """
            UPDATE student
            SET name = %s, email = %s, dept_id = %s, phone = %s, dob = %s, age = %s
            WHERE student_id = %s;
            """,
            (name, email, dept_id, phone, dob, age, student_id),
            commit=True
        )
        flash(f'Student #{student_id} updated successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_students'))

@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        execute_query("DELETE FROM student WHERE student_id = %s;", (student_id,), commit=True)
        flash(f'Student #{student_id} deleted successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')
    return redirect(url_for('list_students'))

@app.route('/students/<int:student_id>')
def student_detail(student_id):
    student = execute_query("""
        SELECT s.*, d.dept_name, d.building
        FROM student s
        INNER JOIN department d ON s.dept_id = d.dept_id
        WHERE s.student_id = %s;
    """, (student_id,), fetch='one')

    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('list_students'))

    enrollments = execute_query("""
        SELECT e.*, c.course_id, c.course_name, c.credits, i.name AS instructor_name, sec.semester, sec.year
        FROM enrollment e
        INNER JOIN section sec ON e.sec_id = sec.sec_id
        INNER JOIN course c ON sec.course_id = c.course_id
        INNER JOIN instructor i ON sec.instructor_id = i.instr_id
        WHERE e.student_id = %s
        ORDER BY sec.year DESC, sec.semester ASC;
    """, (student_id,), fetch='all')

    results = execute_query("""
        SELECT r.*, e.exam_date, e.exam_type, c.course_id, c.course_name
        FROM result r
        INNER JOIN exam e ON r.exam_id = e.exam_id
        INNER JOIN section sec ON e.sec_id = sec.sec_id
        INNER JOIN course c ON sec.course_id = c.course_id
        WHERE r.student_id = %s
        ORDER BY e.exam_date DESC;
    """, (student_id,), fetch='all')

    return render_template('student_detail.html', student=student, enrollments=enrollments, results=results)

# =============================================================================
# 4. INSTRUCTORS MODULE
# =============================================================================
@app.route('/instructors')
def list_instructors():
    search = request.args.get('search', '').strip()
    dept_filter = request.args.get('dept_id', '').strip()

    query = """
        SELECT i.*, d.dept_name, d.building,
               (SELECT COUNT(*) FROM section s WHERE s.instructor_id = i.instr_id) AS sections_taught
        FROM instructor i
        INNER JOIN department d ON i.dept_id = d.dept_id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (i.name LIKE %s OR i.email LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if dept_filter:
        query += " AND i.dept_id = %s"
        params.append(dept_filter)

    query += " ORDER BY i.instr_id ASC;"

    instructors = execute_query(query, tuple(params), fetch='all')
    departments = execute_query("SELECT dept_id, dept_name FROM department ORDER BY dept_name ASC;", fetch='all')
    return render_template('instructors.html', instructors=instructors, departments=departments, search=search, selected_dept=dept_filter)

@app.route('/instructors/add', methods=['POST'])
def add_instructor():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    salary = request.form.get('salary', '').strip()
    dept_id = request.form.get('dept_id', '').strip()

    if not name or not email or not salary or not dept_id:
        flash('All fields are required.', 'danger')
        return redirect(url_for('list_instructors'))

    try:
        execute_query(
            "INSERT INTO instructor (name, email, salary, dept_id) VALUES (%s, %s, %s, %s);",
            (name, email, float(salary), dept_id),
            commit=True
        )
        flash(f'Instructor "{name}" added successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_instructors'))

@app.route('/instructors/edit/<int:instr_id>', methods=['POST'])
def edit_instructor(instr_id):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    salary = request.form.get('salary', '').strip()
    dept_id = request.form.get('dept_id', '').strip()

    if not name or not email or not salary or not dept_id:
        flash('All fields are required.', 'danger')
        return redirect(url_for('list_instructors'))

    try:
        execute_query(
            "UPDATE instructor SET name = %s, email = %s, salary = %s, dept_id = %s WHERE instr_id = %s;",
            (name, email, float(salary), dept_id, instr_id),
            commit=True
        )
        flash(f'Instructor #{instr_id} updated successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_instructors'))

@app.route('/instructors/delete/<int:instr_id>', methods=['POST'])
def delete_instructor(instr_id):
    try:
        execute_query("DELETE FROM instructor WHERE instr_id = %s;", (instr_id,), commit=True)
        flash(f'Instructor #{instr_id} deleted successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')
    return redirect(url_for('list_instructors'))

# =============================================================================
# 5. COURSES MODULE
# =============================================================================
@app.route('/courses')
def list_courses():
    search = request.args.get('search', '').strip()
    dept_filter = request.args.get('dept_id', '').strip()

    query = """
        SELECT c.*, d.dept_name,
               (SELECT COUNT(*) FROM section s WHERE s.course_id = c.course_id) AS section_count
        FROM course c
        INNER JOIN department d ON c.dept_id = d.dept_id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (c.course_id LIKE %s OR c.course_name LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if dept_filter:
        query += " AND c.dept_id = %s"
        params.append(dept_filter)

    query += " ORDER BY c.course_id ASC;"

    courses = execute_query(query, tuple(params), fetch='all')
    departments = execute_query("SELECT dept_id, dept_name FROM department ORDER BY dept_name ASC;", fetch='all')
    return render_template('courses.html', courses=courses, departments=departments, search=search, selected_dept=dept_filter)

@app.route('/courses/add', methods=['POST'])
def add_course():
    course_id = request.form.get('course_id', '').strip().upper()
    course_name = request.form.get('course_name', '').strip()
    credits = request.form.get('credits', '').strip()
    dept_id = request.form.get('dept_id', '').strip()

    if not course_id or not course_name or not credits or not dept_id:
        flash('Course Code, Name, Credits, and Department are required.', 'danger')
        return redirect(url_for('list_courses'))

    try:
        execute_query(
            "INSERT INTO course (course_id, course_name, credits, dept_id) VALUES (%s, %s, %s, %s);",
            (course_id, course_name, int(credits), dept_id),
            commit=True
        )
        flash(f'Course "{course_id}: {course_name}" created successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_courses'))

@app.route('/courses/edit/<course_id>', methods=['POST'])
def edit_course(course_id):
    course_name = request.form.get('course_name', '').strip()
    credits = request.form.get('credits', '').strip()
    dept_id = request.form.get('dept_id', '').strip()

    if not course_name or not credits or not dept_id:
        flash('All fields are required.', 'danger')
        return redirect(url_for('list_courses'))

    try:
        execute_query(
            "UPDATE course SET course_name = %s, credits = %s, dept_id = %s WHERE course_id = %s;",
            (course_name, int(credits), dept_id, course_id),
            commit=True
        )
        flash(f'Course {course_id} updated successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_courses'))

@app.route('/courses/delete/<course_id>', methods=['POST'])
def delete_course(course_id):
    try:
        execute_query("DELETE FROM course WHERE course_id = %s;", (course_id,), commit=True)
        flash(f'Course {course_id} deleted successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')
    return redirect(url_for('list_courses'))

# =============================================================================
# 6. SECTIONS MODULE
# =============================================================================
@app.route('/sections')
def list_sections():
    sections = execute_query("""
        SELECT 
            sec.sec_id,
            sec.course_id,
            c.course_name,
            c.credits,
            sec.instructor_id,
            i.name AS instructor_name,
            sec.semester,
            sec.year,
            (SELECT COUNT(*) FROM enrollment e WHERE e.sec_id = sec.sec_id) AS enrolled_students,
            (SELECT COUNT(*) FROM exam ex WHERE ex.sec_id = sec.sec_id) AS exam_count
        FROM section sec
        INNER JOIN course c ON sec.course_id = c.course_id
        INNER JOIN instructor i ON sec.instructor_id = i.instr_id
        ORDER BY sec.year DESC, sec.semester ASC, sec.sec_id ASC;
    """, fetch='all')

    courses = execute_query("SELECT course_id, course_name FROM course ORDER BY course_id ASC;", fetch='all')
    instructors = execute_query("SELECT instr_id, name FROM instructor ORDER BY name ASC;", fetch='all')
    return render_template('sections.html', sections=sections, courses=courses, instructors=instructors)

@app.route('/sections/add', methods=['POST'])
def add_section():
    course_id = request.form.get('course_id', '').strip()
    instructor_id = request.form.get('instructor_id', '').strip()
    semester = request.form.get('semester', '').strip()
    year = request.form.get('year', '').strip()

    if not course_id or not instructor_id or not semester or not year:
        flash('All fields are required to create a section.', 'danger')
        return redirect(url_for('list_sections'))

    try:
        execute_query(
            "INSERT INTO section (course_id, instructor_id, semester, year) VALUES (%s, %s, %s, %s);",
            (course_id, instructor_id, semester, int(year)),
            commit=True
        )
        flash(f'Section for {course_id} ({semester} {year}) created successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_sections'))

@app.route('/sections/edit/<int:sec_id>', methods=['POST'])
def edit_section(sec_id):
    course_id = request.form.get('course_id', '').strip()
    instructor_id = request.form.get('instructor_id', '').strip()
    semester = request.form.get('semester', '').strip()
    year = request.form.get('year', '').strip()

    if not course_id or not instructor_id or not semester or not year:
        flash('All fields are required.', 'danger')
        return redirect(url_for('list_sections'))

    try:
        execute_query(
            """
            UPDATE section
            SET course_id = %s, instructor_id = %s, semester = %s, year = %s
            WHERE sec_id = %s;
            """,
            (course_id, instructor_id, semester, int(year), sec_id),
            commit=True
        )
        flash(f'Section #{sec_id} updated successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_sections'))

@app.route('/sections/delete/<int:sec_id>', methods=['POST'])
def delete_section(sec_id):
    try:
        execute_query("DELETE FROM section WHERE sec_id = %s;", (sec_id,), commit=True)
        flash(f'Section #{sec_id} deleted successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')
    return redirect(url_for('list_sections'))

# =============================================================================
# 7. ENROLLMENT MODULE (Composite PK: student_id, sec_id)
# =============================================================================
@app.route('/enrollment')
def list_enrollments():
    sec_filter = request.args.get('sec_id', '').strip()
    student_filter = request.args.get('student_id', '').strip()

    query = """
        SELECT 
            e.student_id,
            s.name AS student_name,
            s.email AS student_email,
            e.sec_id,
            c.course_id,
            c.course_name,
            i.name AS instructor_name,
            sec.semester,
            sec.year,
            e.enroll_date,
            e.grade
        FROM enrollment e
        INNER JOIN student s ON e.student_id = s.student_id
        INNER JOIN section sec ON e.sec_id = sec.sec_id
        INNER JOIN course c ON sec.course_id = c.course_id
        INNER JOIN instructor i ON sec.instructor_id = i.instr_id
        WHERE 1=1
    """
    params = []
    if sec_filter:
        query += " AND e.sec_id = %s"
        params.append(sec_filter)
    if student_filter:
        query += " AND e.student_id = %s"
        params.append(student_filter)

    query += " ORDER BY e.enroll_date DESC, s.name ASC;"

    enrollments = execute_query(query, tuple(params), fetch='all')
    students = execute_query("SELECT student_id, name, email FROM student ORDER BY name ASC;", fetch='all')
    sections = execute_query("""
        SELECT sec.sec_id, c.course_id, c.course_name, sec.semester, sec.year, i.name AS instructor_name
        FROM section sec
        INNER JOIN course c ON sec.course_id = c.course_id
        INNER JOIN instructor i ON sec.instructor_id = i.instr_id
        ORDER BY sec.year DESC, c.course_id ASC;
    """, fetch='all')

    return render_template(
        'enrollment.html',
        enrollments=enrollments,
        students=students,
        sections=sections,
        selected_sec=sec_filter,
        selected_student=student_filter
    )

@app.route('/enrollment/add', methods=['POST'])
def add_enrollment():
    student_id = request.form.get('student_id', '').strip()
    sec_id = request.form.get('sec_id', '').strip()
    enroll_date = request.form.get('enroll_date', '').strip() or datetime.date.today().strftime('%Y-%m-%d')
    grade = request.form.get('grade', '').strip() or None

    if not student_id or not sec_id:
        flash('Student and Section selection are required.', 'danger')
        return redirect(url_for('list_enrollments'))

    try:
        execute_query(
            "INSERT INTO enrollment (student_id, sec_id, enroll_date, grade) VALUES (%s, %s, %s, %s);",
            (student_id, sec_id, enroll_date, grade),
            commit=True
        )
        flash('Student enrolled successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_enrollments'))

@app.route('/enrollment/update_grade', methods=['POST'])
def update_enrollment_grade():
    student_id = request.form.get('student_id', '').strip()
    sec_id = request.form.get('sec_id', '').strip()
    grade = request.form.get('grade', '').strip() or None

    try:
        execute_query(
            "UPDATE enrollment SET grade = %s WHERE student_id = %s AND sec_id = %s;",
            (grade, student_id, sec_id),
            commit=True
        )
        flash('Enrollment grade updated successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_enrollments'))

@app.route('/enrollment/delete', methods=['POST'])
def delete_enrollment():
    student_id = request.form.get('student_id', '').strip()
    sec_id = request.form.get('sec_id', '').strip()

    try:
        execute_query(
            "DELETE FROM enrollment WHERE student_id = %s AND sec_id = %s;",
            (student_id, sec_id),
            commit=True
        )
        flash('Student dropped from section successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_enrollments'))

# =============================================================================
# 8. EXAMINATIONS MODULE
# =============================================================================
@app.route('/exams')
def list_exams():
    exams = execute_query("""
        SELECT 
            e.exam_id,
            e.sec_id,
            e.exam_date,
            e.exam_type,
            c.course_id,
            c.course_name,
            sec.semester,
            sec.year,
            i.name AS instructor_name,
            (SELECT COUNT(*) FROM result r WHERE r.exam_id = e.exam_id) AS evaluated_students,
            (SELECT COUNT(*) FROM enrollment en WHERE en.sec_id = e.sec_id) AS enrolled_candidates
        FROM exam e
        INNER JOIN section sec ON e.sec_id = sec.sec_id
        INNER JOIN course c ON sec.course_id = c.course_id
        INNER JOIN instructor i ON sec.instructor_id = i.instr_id
        ORDER BY e.exam_date DESC, e.exam_id DESC;
    """, fetch='all')

    sections = execute_query("""
        SELECT sec.sec_id, c.course_id, c.course_name, sec.semester, sec.year, i.name AS instructor_name
        FROM section sec
        INNER JOIN course c ON sec.course_id = c.course_id
        INNER JOIN instructor i ON sec.instructor_id = i.instr_id
        ORDER BY sec.year DESC, c.course_id ASC;
    """, fetch='all')

    return render_template('exams.html', exams=exams, sections=sections)

@app.route('/exams/add', methods=['POST'])
def add_exam():
    sec_id = request.form.get('sec_id', '').strip()
    exam_date = request.form.get('exam_date', '').strip()
    exam_type = request.form.get('exam_type', '').strip()

    if not sec_id or not exam_date or not exam_type:
        flash('Section, Exam Date, and Exam Type are required.', 'danger')
        return redirect(url_for('list_exams'))

    try:
        execute_query(
            "INSERT INTO exam (sec_id, exam_date, exam_type) VALUES (%s, %s, %s);",
            (sec_id, exam_date, exam_type),
            commit=True
        )
        flash(f'{exam_type} scheduled successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_exams'))

@app.route('/exams/edit/<int:exam_id>', methods=['POST'])
def edit_exam(exam_id):
    sec_id = request.form.get('sec_id', '').strip()
    exam_date = request.form.get('exam_date', '').strip()
    exam_type = request.form.get('exam_type', '').strip()

    if not sec_id or not exam_date or not exam_type:
        flash('All fields are required.', 'danger')
        return redirect(url_for('list_exams'))

    try:
        execute_query(
            "UPDATE exam SET sec_id = %s, exam_date = %s, exam_type = %s WHERE exam_id = %s;",
            (sec_id, exam_date, exam_type, exam_id),
            commit=True
        )
        flash(f'Exam #{exam_id} updated successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_exams'))

@app.route('/exams/delete/<int:exam_id>', methods=['POST'])
def delete_exam(exam_id):
    try:
        execute_query("DELETE FROM exam WHERE exam_id = %s;", (exam_id,), commit=True)
        flash(f'Exam #{exam_id} deleted successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')
    return redirect(url_for('list_exams'))

# =============================================================================
# 9. RESULTS MODULE (Composite PK: student_id, exam_id)
# =============================================================================
@app.route('/results')
def list_results():
    exam_filter = request.args.get('exam_id', '').strip()
    student_filter = request.args.get('student_id', '').strip()

    query = """
        SELECT 
            r.student_id,
            s.name AS student_name,
            s.email AS student_email,
            r.exam_id,
            e.exam_type,
            e.exam_date,
            c.course_id,
            c.course_name,
            sec.sec_id,
            sec.semester,
            sec.year,
            r.marks,
            r.grade
        FROM result r
        INNER JOIN student s ON r.student_id = s.student_id
        INNER JOIN exam e ON r.exam_id = e.exam_id
        INNER JOIN section sec ON e.sec_id = sec.sec_id
        INNER JOIN course c ON sec.course_id = c.course_id
        WHERE 1=1
    """
    params = []
    if exam_filter:
        query += " AND r.exam_id = %s"
        params.append(exam_filter)
    if student_filter:
        query += " AND r.student_id = %s"
        params.append(student_filter)

    query += " ORDER BY e.exam_date DESC, r.marks DESC;"

    results = execute_query(query, tuple(params), fetch='all')

    exams = execute_query("""
        SELECT e.exam_id, e.exam_type, e.exam_date, c.course_id, c.course_name, sec.sec_id
        FROM exam e
        INNER JOIN section sec ON e.sec_id = sec.sec_id
        INNER JOIN course c ON sec.course_id = c.course_id
        ORDER BY e.exam_date DESC;
    """, fetch='all')

    students = execute_query("SELECT student_id, name, email FROM student ORDER BY name ASC;", fetch='all')

    return render_template(
        'results.html',
        results=results,
        exams=exams,
        students=students,
        selected_exam=exam_filter,
        selected_student=student_filter
    )

@app.route('/results/add', methods=['POST'])
def add_result():
    student_id = request.form.get('student_id', '').strip()
    exam_id = request.form.get('exam_id', '').strip()
    marks_str = request.form.get('marks', '').strip()
    grade = request.form.get('grade', '').strip()

    if not student_id or not exam_id or not marks_str:
        flash('Student, Exam, and Marks are required.', 'danger')
        return redirect(url_for('list_results'))

    try:
        marks = float(marks_str)
        if marks < 0 or marks > 100:
            flash('Marks must be between 0 and 100.', 'danger')
            return redirect(url_for('list_results'))
    except ValueError:
        flash('Invalid numeric value for marks.', 'danger')
        return redirect(url_for('list_results'))

    # If grade not explicitly provided, calculate automatically
    if not grade:
        grade = compute_grade(marks)

    try:
        execute_query(
            "INSERT INTO result (student_id, exam_id, marks, grade) VALUES (%s, %s, %s, %s);",
            (student_id, exam_id, marks, grade),
            commit=True
        )
        flash('Result recorded successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_results'))

@app.route('/results/edit', methods=['POST'])
def edit_result():
    student_id = request.form.get('student_id', '').strip()
    exam_id = request.form.get('exam_id', '').strip()
    marks_str = request.form.get('marks', '').strip()
    grade = request.form.get('grade', '').strip()

    if not marks_str:
        flash('Marks are required.', 'danger')
        return redirect(url_for('list_results'))

    try:
        marks = float(marks_str)
        if marks < 0 or marks > 100:
            flash('Marks must be between 0 and 100.', 'danger')
            return redirect(url_for('list_results'))
    except ValueError:
        flash('Invalid marks value.', 'danger')
        return redirect(url_for('list_results'))

    if not grade:
        grade = compute_grade(marks)

    try:
        execute_query(
            "UPDATE result SET marks = %s, grade = %s WHERE student_id = %s AND exam_id = %s;",
            (marks, grade, student_id, exam_id),
            commit=True
        )
        flash('Result updated successfully!', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_results'))

@app.route('/results/delete', methods=['POST'])
def delete_result():
    student_id = request.form.get('student_id', '').strip()
    exam_id = request.form.get('exam_id', '').strip()

    try:
        execute_query(
            "DELETE FROM result WHERE student_id = %s AND exam_id = %s;",
            (student_id, exam_id),
            commit=True
        )
        flash('Result record deleted successfully.', 'success')
    except Exception as e:
        flash(parse_db_error(e), 'danger')

    return redirect(url_for('list_results'))

# =============================================================================
# 10. INTERACTIVE ANALYTICAL REPORTS & VIVA QUERIES MODULE
# =============================================================================
QUERIES_CATALOG = [
    {
        'id': 1,
        'title': '1. Students with Department Information',
        'concept': 'INNER JOIN on Foreign Key',
        'description': 'Demonstrates a standard 2-table INNER JOIN connecting students to their respective department names and building details.',
        'sql': """SELECT 
    s.student_id, s.name AS student_name, s.email, s.phone, s.dob, s.age, d.dept_name, d.building
FROM student s
INNER JOIN department d ON s.dept_id = d.dept_id
ORDER BY s.student_id ASC;"""
    },
    {
        'id': 2,
        'title': '2. Courses Offered by Each Department',
        'concept': '1-to-Many Relationship Navigation & Ordering',
        'description': 'Retrieves all academic courses sorted by department, demonstrating relational association between departments and curriculum.',
        'sql': """SELECT 
    d.dept_name, c.course_id, c.course_name, c.credits
FROM course c
INNER JOIN department d ON c.dept_id = d.dept_id
ORDER BY d.dept_name ASC, c.course_id ASC;"""
    },
    {
        'id': 3,
        'title': '3. Instructors & Department Affiliation with Salaries',
        'concept': 'Relational Projection & SQL String/Currency Formatting',
        'description': 'Lists faculty members, departments, and formatted salaries ordered from highest to lowest compensation.',
        'sql': """SELECT 
    i.instr_id, i.name AS instructor_name, i.email, CONCAT('$', FORMAT(i.salary, 2)) AS formatted_salary, d.dept_name, d.building
FROM instructor i
INNER JOIN department d ON i.dept_id = d.dept_id
ORDER BY i.salary DESC;"""
    },
    {
        'id': 4,
        'title': '4. Students Enrolled in a Specific Section (Section 1)',
        'concept': 'Multi-Table Associative JOIN (4 Tables)',
        'description': 'Navigates from section to course, through enrollment associative entity to student table, filtering by sec_id = 1.',
        'sql': """SELECT 
    e.sec_id, c.course_id, c.course_name, s.student_id, s.name AS student_name, s.email, e.enroll_date, COALESCE(e.grade, 'In Progress') AS current_grade
FROM enrollment e
INNER JOIN student s ON e.student_id = s.student_id
INNER JOIN section sec ON e.sec_id = sec.sec_id
INNER JOIN course c ON sec.course_id = c.course_id
WHERE e.sec_id = 1
ORDER BY s.name ASC;"""
    },
    {
        'id': 5,
        'title': '5. Total Students Count by Department',
        'concept': 'LEFT OUTER JOIN & Aggregate COUNT with GROUP BY',
        'description': 'Uses a LEFT JOIN to ensure departments with 0 students are still included in the final aggregation rather than dropped.',
        'sql': """SELECT 
    d.dept_id, d.dept_name, d.building, COUNT(s.student_id) AS total_students
FROM department d
LEFT JOIN student s ON d.dept_id = s.dept_id
GROUP BY d.dept_id, d.dept_name, d.building
ORDER BY total_students DESC, d.dept_name ASC;"""
    },
    {
        'id': 6,
        'title': '6. Course Offerings with Instructor Details',
        'concept': '3-Table Entity Joining (Section, Course, Instructor)',
        'description': 'Displays active section allocations mapping courses to instructors along with academic semester and year.',
        'sql': """SELECT 
    sec.sec_id, sec.course_id, c.course_name, c.credits, i.name AS instructor_name, i.email AS instructor_email, sec.semester, sec.year
FROM section sec
INNER JOIN course c ON sec.course_id = c.course_id
INNER JOIN instructor i ON sec.instructor_id = i.instr_id
ORDER BY sec.year DESC, sec.semester ASC, c.course_id ASC;"""
    },
    {
        'id': 7,
        'title': '7. Examination Transcript for Student #1',
        'concept': 'Student Performance Traversal (Result -> Exam -> Section -> Course)',
        'description': 'Fetches all examination marks, dates, and calculated letter grades for a specific student.',
        'sql': """SELECT 
    s.student_id, s.name AS student_name, c.course_id, c.course_name, e.exam_type, e.exam_date, r.marks, r.grade
FROM result r
INNER JOIN student s ON r.student_id = s.student_id
INNER JOIN exam e ON r.exam_id = e.exam_id
INNER JOIN section sec ON e.sec_id = sec.sec_id
INNER JOIN course c ON sec.course_id = c.course_id
WHERE s.student_id = 1
ORDER BY e.exam_date ASC;"""
    },
    {
        'id': 8,
        'title': '8. Statistical Analysis per Examination (Avg, Min, Max)',
        'concept': 'Multiple Aggregation Functions (AVG, MIN, MAX, COUNT)',
        'description': 'Calculates the class average score, lowest score, highest score, and total candidate count evaluated per exam.',
        'sql': """SELECT 
    e.exam_id, c.course_name, e.exam_type, e.exam_date, COUNT(r.student_id) AS students_evaluated,
    ROUND(AVG(r.marks), 2) AS average_marks, MIN(r.marks) AS lowest_marks, MAX(r.marks) AS highest_marks
FROM exam e
INNER JOIN section sec ON e.sec_id = sec.sec_id
INNER JOIN course c ON sec.course_id = c.course_id
LEFT JOIN result r ON e.exam_id = r.exam_id
GROUP BY e.exam_id, c.course_name, e.exam_type, e.exam_date
ORDER BY e.exam_id ASC;"""
    },
    {
        'id': 9,
        'title': '9. Students with Zero Enrollments (Anti-Join / Relational Difference)',
        'concept': 'LEFT JOIN with NULL check and Subquery NOT EXISTS',
        'description': 'Identifies newly admitted or inactive students who have not yet registered in any course section.',
        'sql': """SELECT 
    s.student_id, s.name AS student_name, s.email, d.dept_name
FROM student s
INNER JOIN department d ON s.dept_id = d.dept_id
LEFT JOIN enrollment e ON s.student_id = e.student_id
WHERE e.student_id IS NULL;"""
    },
    {
        'id': 10,
        'title': '10. Highest-Scoring Student(s) in Each Examination',
        'concept': 'Tuple Subquery matching (exam_id, marks) IN (SELECT ... MAX(marks))',
        'description': 'Demonstrates advanced subquery filtering to extract the top-scoring candidate per examination.',
        'sql': """SELECT 
    e.exam_id, c.course_name, e.exam_type, s.student_id, s.name AS top_student, r.marks AS score
FROM result r
INNER JOIN exam e ON r.exam_id = e.exam_id
INNER JOIN section sec ON e.sec_id = sec.sec_id
INNER JOIN course c ON sec.course_id = c.course_id
INNER JOIN student s ON r.student_id = s.student_id
WHERE (r.exam_id, r.marks) IN (
    SELECT exam_id, MAX(marks)
    FROM result
    GROUP BY exam_id
)
ORDER BY e.exam_id ASC;"""
    },
    {
        'id': 11,
        'title': '11. High-Compensation Departments (JOIN, GROUP BY, HAVING, Subquery)',
        'concept': 'Comprehensive DBMS construct: JOIN + GROUP BY + HAVING + Scalar Subquery',
        'description': 'Filters departments having at least 2 instructors and an average salary > $88,000, while including a nested subquery for student count.',
        'sql': """SELECT 
    d.dept_id, d.dept_name, COUNT(i.instr_id) AS total_instructors,
    ROUND(AVG(i.salary), 2) AS avg_salary, MAX(i.salary) AS highest_salary,
    (SELECT COUNT(*) FROM student s WHERE s.dept_id = d.dept_id) AS dept_student_count
FROM department d
INNER JOIN instructor i ON d.dept_id = i.dept_id
GROUP BY d.dept_id, d.dept_name
HAVING COUNT(i.instr_id) >= 2 AND AVG(i.salary) > 88000.00
ORDER BY avg_salary DESC;"""
    }
]

# =============================================================================
# APPLICATION STARTUP
# =============================================================================
if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    # Run development server
    app.run(debug=True, host='127.0.0.1', port=5000)
