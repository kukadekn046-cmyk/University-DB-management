-- =============================================================================
-- University Management System - Database Schema (MySQL)
-- DBMS Mini Project based on Academic ER Diagram
-- =============================================================================

CREATE DATABASE IF NOT EXISTS university_db;
USE university_db;

-- Disable foreign key checks during table drop/re-creation
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS result;
DROP TABLE IF EXISTS exam;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS section;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS instructor;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS department;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. DEPARTMENT Table
-- -----------------------------------------------------------------------------
CREATE TABLE department (
    dept_id     INT AUTO_INCREMENT PRIMARY KEY,
    dept_name   VARCHAR(100) NOT NULL UNIQUE,
    building    VARCHAR(100) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2. STUDENT Table
-- Includes DOB and derived/optional Age from ER diagram
-- -----------------------------------------------------------------------------
CREATE TABLE student (
    student_id  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    dept_id     INT NOT NULL,
    phone       VARCHAR(20) DEFAULT NULL,
    dob         DATE DEFAULT NULL,
    age         INT DEFAULT NULL CHECK (age IS NULL OR (age >= 15 AND age <= 80)),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_department
        FOREIGN KEY (dept_id) REFERENCES department (dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. INSTRUCTOR Table (Entities labeled INSTRUCTORS in ER diagram)
-- -----------------------------------------------------------------------------
CREATE TABLE instructor (
    instr_id    INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    salary      DECIMAL(10,2) NOT NULL CHECK (salary > 0),
    dept_id     INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_instructor_department
        FOREIGN KEY (dept_id) REFERENCES department (dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. COURSE Table
-- -----------------------------------------------------------------------------
CREATE TABLE course (
    course_id   VARCHAR(10) PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    credits     INT NOT NULL CHECK (credits > 0 AND credits <= 8),
    dept_id     INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_course_department
        FOREIGN KEY (dept_id) REFERENCES department (dept_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. SECTION Table
-- Connects course and instructor to semester/year offering
-- -----------------------------------------------------------------------------
CREATE TABLE section (
    sec_id        INT AUTO_INCREMENT PRIMARY KEY,
    course_id     VARCHAR(10) NOT NULL,
    instructor_id INT NOT NULL,
    semester      VARCHAR(20) NOT NULL CHECK (semester IN ('Fall', 'Spring', 'Summer', 'Winter')),
    year          INT NOT NULL CHECK (year >= 2020 AND year <= 2035),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_section_course
        FOREIGN KEY (course_id) REFERENCES course (course_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_section_instructor
        FOREIGN KEY (instructor_id) REFERENCES instructor (instr_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uk_section_offering
        UNIQUE KEY (course_id, instructor_id, semester, year)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 6. ENROLLMENT Table (Associative Entity: Student - Section)
-- Composite Primary Key: (student_id, sec_id)
-- -----------------------------------------------------------------------------
CREATE TABLE enrollment (
    student_id  INT NOT NULL,
    sec_id      INT NOT NULL,
    enroll_date DATE NOT NULL,
    grade       VARCHAR(5) DEFAULT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, sec_id),
    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (student_id) REFERENCES student (student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_section
        FOREIGN KEY (sec_id) REFERENCES section (sec_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 7. EXAM Table
-- -----------------------------------------------------------------------------
CREATE TABLE exam (
    exam_id     INT AUTO_INCREMENT PRIMARY KEY,
    sec_id      INT NOT NULL,
    exam_date   DATE NOT NULL,
    exam_type   VARCHAR(50) NOT NULL CHECK (exam_type IN ('Midterm', 'Final', 'Quiz', 'Assignment', 'Practical')),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exam_section
        FOREIGN KEY (sec_id) REFERENCES section (sec_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 8. RESULT Table (Associative Entity: Student - Exam)
-- Composite Primary Key: (student_id, exam_id)
-- -----------------------------------------------------------------------------
CREATE TABLE result (
    student_id  INT NOT NULL,
    exam_id     INT NOT NULL,
    marks       DECIMAL(5,2) NOT NULL CHECK (marks >= 0 AND marks <= 100),
    grade       VARCHAR(5) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, exam_id),
    CONSTRAINT fk_result_student
        FOREIGN KEY (student_id) REFERENCES student (student_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_result_exam
        FOREIGN KEY (exam_id) REFERENCES exam (exam_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- =============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================================================
CREATE INDEX idx_student_dept ON student (dept_id);
CREATE INDEX idx_instructor_dept ON instructor (dept_id);
CREATE INDEX idx_course_dept ON course (dept_id);
CREATE INDEX idx_section_course ON section (course_id);
CREATE INDEX idx_section_instructor ON section (instructor_id);
CREATE INDEX idx_exam_section ON exam (sec_id);
CREATE INDEX idx_result_exam ON result (exam_id);

-- =============================================================================
-- SAMPLE DATA INSERTION (Realistic & Normalized)
-- =============================================================================

-- Departments
INSERT INTO department (dept_id, dept_name, building) VALUES
(1, 'Computer Science & Engineering', 'Turing Block'),
(2, 'Information Technology', 'Lovelace Hall'),
(3, 'Electronics & Telecommunication', 'Maxwell Complex'),
(4, 'Mechanical Engineering', 'Newton Hall'),
(5, 'Civil Engineering', 'Smeaton Wing');

-- Students (including DOB and age; Student 8 is deliberately un-enrolled for testing)
INSERT INTO student (student_id, name, email, dept_id, phone, dob, age) VALUES
(1, 'Aarav Sharma',     'aarav.sharma@univ.edu',    1, '+91-9876543210', '2004-05-14', 22),
(2, 'Ananya Iyer',      'ananya.iyer@univ.edu',     1, '+91-9876543211', '2004-08-21', 22),
(3, 'Rohan Kulkarni',   'rohan.k@univ.edu',         2, '+91-9876543212', '2003-11-30', 23),
(4, 'Priya Nair',       'priya.nair@univ.edu',      2, '+91-9876543213', '2004-02-18', 22),
(5, 'Vikram Deshmukh',  'vikram.d@univ.edu',        3, '+91-9876543214', '2003-09-10', 23),
(6, 'Sneha Patil',      'sneha.patil@univ.edu',     3, '+91-9876543215', '2005-01-25', 21),
(7, 'Aditya Joshi',     'aditya.joshi@univ.edu',    4, '+91-9876543216', '2004-04-05', 22),
(8, 'Tanvi Kulkarni',   'tanvi.k@univ.edu',         5, '+91-9876543217', '2004-07-19', 22);

-- Instructors
INSERT INTO instructor (instr_id, name, email, salary, dept_id) VALUES
(1, 'Dr. Alan Turing',       'a.turing@univ.edu',       95000.00, 1),
(2, 'Dr. Barbara Liskov',    'b.liskov@univ.edu',       92000.00, 1),
(3, 'Prof. Claude Shannon',  'c.shannon@univ.edu',      88000.00, 2),
(4, 'Dr. Grace Hopper',      'g.hopper@univ.edu',       90000.00, 2),
(5, 'Dr. James Maxwell',     'j.maxwell@univ.edu',      86000.00, 3),
(6, 'Prof. Nikola Tesla',    'n.tesla@univ.edu',        87000.00, 4);

-- Courses
INSERT INTO course (course_id, course_name, credits, dept_id) VALUES
('CS101', 'Data Structures & Algorithms',       4, 1),
('CS201', 'Database Management Systems',        4, 1),
('IT102', 'Web Application Development',        3, 2),
('IT205', 'Cloud Computing & DevOps',           3, 2),
('ET101', 'Digital Signal Processing',          4, 3),
('ME201', 'Thermodynamics & Fluid Mechanics',   4, 4),
('CE101', 'Structural Mechanics',               3, 5);

-- Sections (Offerings)
INSERT INTO section (sec_id, course_id, instructor_id, semester, year) VALUES
(1, 'CS101', 1, 'Fall',   2026),
(2, 'CS201', 2, 'Fall',   2026),
(3, 'IT102', 3, 'Fall',   2026),
(4, 'IT205', 4, 'Spring', 2026),
(5, 'ET101', 5, 'Fall',   2026),
(6, 'ME201', 6, 'Fall',   2026);

-- Enrollments (Composite PK: student_id, sec_id)
INSERT INTO enrollment (student_id, sec_id, enroll_date, grade) VALUES
(1, 1, '2026-08-01', 'A'),
(1, 2, '2026-08-01', 'A+'),
(2, 1, '2026-08-02', 'B+'),
(2, 2, '2026-08-02', 'A'),
(3, 2, '2026-08-03', 'A'),
(3, 3, '2026-08-03', 'B'),
(4, 3, '2026-08-04', 'A+'),
(4, 4, '2026-01-10', 'A'),
(5, 5, '2026-08-05', 'B+'),
(6, 5, '2026-08-06', 'A'),
(7, 6, '2026-08-07', 'B');

-- Exams
INSERT INTO exam (exam_id, sec_id, exam_date, exam_type) VALUES
(1, 1, '2026-10-15', 'Midterm'),
(2, 1, '2026-12-10', 'Final'),
(3, 2, '2026-10-18', 'Midterm'),
(4, 2, '2026-12-12', 'Final'),
(5, 3, '2026-10-20', 'Midterm'),
(6, 5, '2026-10-22', 'Midterm'),
(7, 6, '2026-10-25', 'Midterm');

-- Results (Composite PK: student_id, exam_id)
INSERT INTO result (student_id, exam_id, marks, grade) VALUES
-- Exam 1: CS101 Midterm (sec_id 1)
(1, 1, 94.50, 'A+'),
(2, 1, 82.00, 'B+'),

-- Exam 2: CS101 Final (sec_id 1)
(1, 2, 91.00, 'A'),
(2, 2, 85.50, 'A'),

-- Exam 3: CS201 Midterm (sec_id 2)
(1, 3, 98.00, 'A+'),
(2, 3, 88.00, 'A'),
(3, 3, 92.50, 'A'),

-- Exam 4: CS201 Final (sec_id 2)
(1, 4, 96.00, 'A+'),
(2, 4, 89.50, 'A'),
(3, 4, 90.00, 'A'),

-- Exam 5: IT102 Midterm (sec_id 3)
(3, 5, 78.50, 'B'),
(4, 5, 95.00, 'A+'),

-- Exam 6: ET101 Midterm (sec_id 5)
(5, 6, 84.00, 'B+'),
(6, 6, 91.50, 'A'),

-- Exam 7: ME201 Midterm (sec_id 6)
(7, 7, 76.00, 'B');
