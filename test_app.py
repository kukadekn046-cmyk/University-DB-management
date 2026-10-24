import unittest
from app import app
from database import execute_query

class UniversityManagementSystemTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_01_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'University Dashboard', response.data)
        self.assertIn(b'Total Students', response.data)

    def test_02_departments(self):
        # List departments
        response = self.client.get('/departments')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Computer Science &amp; Engineering', response.data)

        # Add a department
        response = self.client.post('/departments/add', data={
            'dept_name': 'Aerospace Engineering',
            'building': 'Kalpana Chawla Block'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aerospace Engineering', response.data)

        # Retrieve ID
        dept = execute_query("SELECT dept_id FROM department WHERE dept_name = %s;", ('Aerospace Engineering',), fetch='one')
        self.assertIsNotNone(dept)
        dept_id = dept['dept_id']

        # Edit department
        response = self.client.post(f'/departments/edit/{dept_id}', data={
            'dept_name': 'Aerospace & Avionics',
            'building': 'Kalpana Chawla Block B'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aerospace &amp; Avionics', response.data)

        # Delete department
        response = self.client.post(f'/departments/delete/{dept_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_03_students_crud(self):
        # List students
        response = self.client.get('/students')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aarav Sharma', response.data)

        # Add a new student
        response = self.client.post('/students/add', data={
            'name': 'Test Student',
            'email': 'test.student@univ.edu',
            'dept_id': 1,
            'phone': '+91-9999999999',
            'dob': '2004-01-01',
            'age': 22
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Student', response.data)

        # Fetch student ID
        st = execute_query("SELECT student_id FROM student WHERE email = %s;", ('test.student@univ.edu',), fetch='one')
        self.assertIsNotNone(st)
        sid = st['student_id']

        # View student profile
        response = self.client.get(f'/students/{sid}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Student', response.data)

        # Delete student
        response = self.client.post(f'/students/delete/{sid}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_04_instructors_crud(self):
        response = self.client.get('/instructors')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dr. Alan Turing', response.data)

    def test_05_courses_crud(self):
        response = self.client.get('/courses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CS101', response.data)

    def test_06_sections_crud(self):
        response = self.client.get('/sections')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CS101', response.data)

    def test_07_enrollment_crud(self):
        response = self.client.get('/enrollment')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Aarav Sharma', response.data)

    def test_08_exams_crud(self):
        response = self.client.get('/exams')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Midterm', response.data)

    def test_09_results_crud(self):
        response = self.client.get('/results')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'94.50', response.data)

    def test_10_all_11_viva_reports(self):
        for qid in range(1, 12):
            response = self.client.get(f'/reports?qid={qid}')
            self.assertEqual(response.status_code, 200, f"Query #{qid} failed with status {response.status_code}")
            self.assertNotIn(b'Query Error', response.data)

if __name__ == '__main__':
    unittest.main()
