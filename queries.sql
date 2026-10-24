-- =============================================================================
-- University Management System - Analytical & Viva SQL Queries
-- Demonstrating Relational Algebra, Joins, Aggregation, Subqueries & Reports
-- =============================================================================

USE university_db;

-- -----------------------------------------------------------------------------
-- Query 1: Display all students with their department names (INNER JOIN)
-- Concept: Basic 2-table INNER JOIN on foreign key
-- -----------------------------------------------------------------------------
SELECT 
    s.student_id,
    s.name AS student_name,
    s.email,
    s.phone,
    s.dob,
    s.age,
    d.dept_name,
    d.building
FROM student s
INNER JOIN department d ON s.dept_id = d.dept_id
ORDER BY s.student_id ASC;


-- -----------------------------------------------------------------------------
-- Query 2: Display all courses offered by each department (INNER JOIN & ORDER)
-- Concept: Categorical grouping/listing via JOIN
-- -----------------------------------------------------------------------------
SELECT 
    d.dept_name,
    c.course_id,
    c.course_name,
    c.credits
FROM course c
INNER JOIN department d ON c.dept_id = d.dept_id
ORDER BY d.dept_name ASC, c.course_id ASC;


-- -----------------------------------------------------------------------------
-- Query 3: List instructors and their departments with salary details
-- Concept: Formatted numeric values with JOIN
-- -----------------------------------------------------------------------------
SELECT 
    i.instr_id,
    i.name AS instructor_name,
    i.email,
    CONCAT('$', FORMAT(i.salary, 2)) AS formatted_salary,
    d.dept_name,
    d.building
FROM instructor i
INNER JOIN department d ON i.dept_id = d.dept_id
ORDER BY i.salary DESC;


-- -----------------------------------------------------------------------------
-- Query 4: Show students enrolled in a particular section (e.g., Section 1: CS101)
-- Concept: Multi-table JOIN (student -> enrollment -> section -> course)
-- -----------------------------------------------------------------------------
SELECT 
    e.sec_id,
    c.course_id,
    c.course_name,
    s.student_id,
    s.name AS student_name,
    s.email,
    e.enroll_date,
    COALESCE(e.grade, 'In Progress') AS current_grade
FROM enrollment e
INNER JOIN student s ON e.student_id = s.student_id
INNER JOIN section sec ON e.sec_id = sec.sec_id
INNER JOIN course c ON sec.course_id = c.course_id
WHERE e.sec_id = 1
ORDER BY s.name ASC;


-- -----------------------------------------------------------------------------
-- Query 5: Count total students in each department (LEFT JOIN, GROUP BY, COUNT)
-- Concept: LEFT JOIN to ensure departments with 0 students are still included
-- -----------------------------------------------------------------------------
SELECT 
    d.dept_id,
    d.dept_name,
    d.building,
    COUNT(s.student_id) AS total_students
FROM department d
LEFT JOIN student s ON d.dept_id = s.dept_id
GROUP BY d.dept_id, d.dept_name, d.building
ORDER BY total_students DESC, d.dept_name ASC;


-- -----------------------------------------------------------------------------
-- Query 6: Display course sections with instructor and course details
-- Concept: 3-table JOIN (section -> course -> instructor)
-- -----------------------------------------------------------------------------
SELECT 
    sec.sec_id,
    sec.course_id,
    c.course_name,
    c.credits,
    i.name AS instructor_name,
    i.email AS instructor_email,
    sec.semester,
    sec.year
FROM section sec
INNER JOIN course c ON sec.course_id = c.course_id
INNER JOIN instructor i ON sec.instructor_id = i.instr_id
ORDER BY sec.year DESC, sec.semester ASC, c.course_id ASC;


-- -----------------------------------------------------------------------------
-- Query 7: Retrieve all examination results for a particular student (e.g., Student 1)
-- Concept: 4-table JOIN (result -> exam -> section -> course)
-- -----------------------------------------------------------------------------
SELECT 
    s.student_id,
    s.name AS student_name,
    c.course_id,
    c.course_name,
    e.exam_type,
    e.exam_date,
    r.marks,
    r.grade
FROM result r
INNER JOIN student s ON r.student_id = s.student_id
INNER JOIN exam e ON r.exam_id = e.exam_id
INNER JOIN section sec ON e.sec_id = sec.sec_id
INNER JOIN course c ON sec.course_id = c.course_id
WHERE s.student_id = 1
ORDER BY e.exam_date ASC;


-- -----------------------------------------------------------------------------
-- Query 8: Calculate average, minimum, and maximum marks for each examination
-- Concept: Aggregate functions (AVG, MIN, MAX, COUNT) with multi-table GROUP BY
-- -----------------------------------------------------------------------------
SELECT 
    e.exam_id,
    c.course_name,
    e.exam_type,
    e.exam_date,
    COUNT(r.student_id) AS students_evaluated,
    ROUND(AVG(r.marks), 2) AS average_marks,
    MIN(r.marks) AS lowest_marks,
    MAX(r.marks) AS highest_marks
FROM exam e
INNER JOIN section sec ON e.sec_id = sec.sec_id
INNER JOIN course c ON sec.course_id = c.course_id
LEFT JOIN result r ON e.exam_id = r.exam_id
GROUP BY e.exam_id, c.course_name, e.exam_type, e.exam_date
ORDER BY e.exam_id ASC;


-- -----------------------------------------------------------------------------
-- Query 9: Find students who have NOT enrolled in any course section
-- Concept: Outer Join with NULL check / Anti-Join (demonstrating NOT EXISTS / LEFT JOIN)
-- -----------------------------------------------------------------------------
-- Method A: Using LEFT JOIN & IS NULL
SELECT 
    s.student_id,
    s.name AS student_name,
    s.email,
    d.dept_name
FROM student s
INNER JOIN department d ON s.dept_id = d.dept_id
LEFT JOIN enrollment e ON s.student_id = e.student_id
WHERE e.student_id IS NULL;

-- Method B: Using NOT EXISTS subquery (equivalent relational division logic)
SELECT 
    s.student_id,
    s.name AS student_name,
    s.email
FROM student s
WHERE NOT EXISTS (
    SELECT 1 FROM enrollment e WHERE e.student_id = s.student_id
);


-- -----------------------------------------------------------------------------
-- Query 10: Find the highest-scoring student in each examination
-- Concept: Correlated subquery or subquery join for maximum score per group
-- -----------------------------------------------------------------------------
SELECT 
    e.exam_id,
    c.course_name,
    e.exam_type,
    s.student_id,
    s.name AS top_student,
    r.marks AS score
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
ORDER BY e.exam_id ASC;


-- -----------------------------------------------------------------------------
-- Query 11: Complex Analytical Query Demonstrating JOIN, GROUP BY, HAVING,
-- Subquery, and Aggregate Functions
-- Description: Find departments that have at least 2 instructors, calculate
-- their average instructor salary, and only show departments where the average
-- salary exceeds $88,000.
-- -----------------------------------------------------------------------------
SELECT 
    d.dept_id,
    d.dept_name,
    COUNT(i.instr_id) AS total_instructors,
    ROUND(AVG(i.salary), 2) AS avg_salary,
    MAX(i.salary) AS highest_salary,
    (SELECT COUNT(*) FROM student s WHERE s.dept_id = d.dept_id) AS dept_student_count
FROM department d
INNER JOIN instructor i ON d.dept_id = i.dept_id
GROUP BY d.dept_id, d.dept_name
HAVING COUNT(i.instr_id) >= 2 AND AVG(i.salary) > 88000.00
ORDER BY avg_salary DESC;
