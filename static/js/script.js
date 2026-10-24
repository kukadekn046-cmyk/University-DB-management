// =============================================================================
// University Management System - Client-side Helper Scripts
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-calculate age from DOB in Student modal
    const dobInput = document.getElementById('student_dob');
    const ageInput = document.getElementById('student_age');

    if (dobInput && ageInput) {
        dobInput.addEventListener('change', function () {
            if (this.value) {
                const birthDate = new Date(this.value);
                const today = new Date();
                let age = today.getFullYear() - birthDate.getFullYear();
                const m = today.getMonth() - birthDate.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                    age--;
                }
                if (age >= 10 && age <= 100) {
                    ageInput.value = age;
                }
            }
        });
    }

    // 2. Auto-suggest letter grade based on marks in Result modal
    function calculateGrade(marks) {
        const m = parseFloat(marks);
        if (isNaN(m)) return '';
        if (m >= 90) return 'A+';
        if (m >= 80) return 'A';
        if (m >= 70) return 'B+';
        if (m >= 60) return 'B';
        if (m >= 50) return 'C';
        if (m >= 40) return 'D';
        return 'F';
    }

    const marksInput = document.getElementById('result_marks');
    const gradeInput = document.getElementById('result_grade');

    if (marksInput && gradeInput) {
        marksInput.addEventListener('input', function () {
            const grade = calculateGrade(this.value);
            if (grade) {
                gradeInput.value = grade;
            }
        });
    }

    // 3. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});
