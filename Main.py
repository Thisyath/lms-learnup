import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from datetime import datetime

DB_FILENAME = "database.db"

class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        # Load UI files
        self.page1 = uic.loadUi("ui/page1.ui")  # Welcome
        self.page2 = uic.loadUi("ui/page2.ui")  # Register
        self.page3 = uic.loadUi("ui/page3.ui")  # Login
        self.page4 = uic.loadUi("ui/page4.ui")  # Teacher Dashboard
        self.page5 = uic.loadUi("ui/page5.ui")  # Create Course
        self.page6 = uic.loadUi("ui/page6.ui")  # Course Management
        self.page7 = uic.loadUi("ui/page7.ui")  # Student Dashboard

        # Add pages to stacked widget
        self.addWidget(self.page1)  # index 0: Welcome
        self.addWidget(self.page2)  # index 1: Register
        self.addWidget(self.page3)  # index 2: Login
        self.addWidget(self.page4)  # index 3: Teacher Dashboard
        self.addWidget(self.page5)  # index 4: Create Course
        self.addWidget(self.page6)  # index 5: Course Management
        self.addWidget(self.page7)  # index 6: Student Dashboard

        # Initialize current user
        self.current_user = None
        self.current_role = None

        # Setup all page connections
        self.setup_welcome_page()
        self.setup_register_page()
        self.setup_login_page()
        self.setup_teacher_dashboard()
        self.setup_create_course()
        self.setup_course_management()
        self.setup_student_dashboard()

        # Set window properties
        self.setWindowTitle("Learn Up App")
        self.setCurrentIndex(0)

    def setup_welcome_page(self):
        """Setup connections for welcome page"""
        self.page1.btnRegister.clicked.connect(self.goto_register)
        self.page1.btnLogin.clicked.connect(self.goto_login)

    def setup_register_page(self):
        """Setup connections for register page"""
        self.selected_role = None
        self.page2.btnSignIn.clicked.connect(self.register_action)
        self.page2.teacherRadio.clicked.connect(lambda: self.select_role("teacher"))
        self.page2.studentRadio.clicked.connect(lambda: self.select_role("student"))
        self.page2.linkLogin.mousePressEvent = lambda event: self.goto_login()

    def setup_login_page(self):
        """Setup connections for login page"""
        self.page3.btnLogin.clicked.connect(self.login_action)

    def setup_teacher_dashboard(self):
        """Setup teacher dashboard page"""
        pixmap = QPixmap("assets/profilTeacher.png")
        self.page4.profilTeacher.setPixmap(pixmap)

        self.page4.dashboardBtn.clicked.connect(self.show_teacher_dashboard)
        self.page4.createCourseBtn.clicked.connect(self.show_create_course)
        self.page4.managementBtn.clicked.connect(self.show_course_management)
        self.page4.logoutBtn.clicked.connect(self.logout_action)

    def setup_create_course(self):
        """Setup create course page"""
        self.page5.addCourseBtn.clicked.connect(self.add_course_action)
        self.page5.cancelBtn.clicked.connect(lambda: self.setCurrentIndex(3))
        self.page5.previousBtn.clicked.connect(lambda: self.setCurrentIndex(3))

    def setup_course_management(self):
        """Setup course management page"""
        # Course Content
        self.page6.btnSelectFile1.clicked.connect(self.select_content_file)
        self.page6.btnAddContent.clicked.connect(self.add_content)

        # Assignment
        self.page6.btnSelectFile2.clicked.connect(self.select_assignment_file)
        self.page6.btnAddAssignment.clicked.connect(self.add_assignment)
        self.page6.dateEdit.setCalendarPopup(True)  # Enable calendar popup

        # Enrollment
        self.page6.btnAddEnroll.clicked.connect(self.add_enrollment)

        # Navigation
        self.page6.btnPrevious.clicked.connect(lambda: self.setCurrentIndex(3))

        # Course selection
        self.page6.comboSelectCourse.currentIndexChanged.connect(self.load_course_data)

    def select_content_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.selected_content_file = path
            self.page6.btnSelectFile1.setText(os.path.basename(path))

    def add_content(self):
        if not hasattr(self, 'selected_content_file'):
            QMessageBox.warning(self, "Error", "Please select a file first!")
            return
        course_id = self.page6.comboSelectCourse.currentData()
        youtube_url = self.page6.lineYoutube.text().strip()

        if not os.path.exists("materials"):
            os.makedirs("materials")

        pdf_filename = f"{course_id}_{int(datetime.now().timestamp())}_{os.path.basename(self.selected_content_file)}"
        dest_path = os.path.join("materials", pdf_filename)

        with open(self.selected_content_file, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())

        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO CourseMaterial (assignment_id)
                    VALUES (?, ?, ?, datetime('now'))
                    """, (course_id, pdf_filename, youtube_url))
        conn.commit()
        conn.close()

        self.load_content_history(course_id)
        QMessageBox.information(self, "Success", "Content added successfully!")

    def select_assignment_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if path:
            self.selected_assignment_file = path
            self.page6.btnSelectFile2.setText(os.path.basename(path))

    def add_assignment(self):
        if not hasattr(self, 'selected_assignment_file'):
            QMessageBox.warning(self, "Error", "Please select a file first!")
            return

        course_id = self.page6.comboSelectCourse.currentData()
        deadline = self.page6.dateEdit.date().toString("yyyy-MM-dd")

        if not os.path.exists("assignments"):
            os.makedirs("assignments")

        pdf_filename = f"{course_id}_{int(datetime.now().timestamp())}_{os.path.basename(self.selected_assignment_file)}"
        dest_path = os.path.join("assignments", pdf_filename)

        with open(self.selected_assignment_file, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())

        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO Assignment (course_id, pdf_file, due_date, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                    """, (course_id, pdf_filename, deadline))
        conn.commit()
        conn.close()

        self.load_assignment_history(course_id)
        QMessageBox.information(self, "Success", "Assignment added successfully!")

    def add_enrollment(self):
        course_id = self.page6.comboSelectCourse.currentData()
        email = self.page6.lineEmail.text().strip()

        if not email:
            QMessageBox.warning(self, "Error", "Please enter student email!")
            return

        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()

        # Check if email exists and is a student
        cur.execute("""
                    SELECT s.student_id
                    FROM Student s
                             JOIN User u ON s.user_id = u.user_id
                    WHERE u.email = ?
                    """, (email,))

        result = cur.fetchone()
        if not result:
            QMessageBox.warning(self, "Error", "Email not found or not a student!")
            conn.close()
            return

        student_id = result[0]

        # Check if already enrolled
        cur.execute("SELECT * FROM Enrollment WHERE course_id=? AND student_id=?",
                    (course_id, student_id))
        if cur.fetchone():
            QMessageBox.warning(self, "Error", "Student already enrolled!")
            conn.close()
            return

        # Enroll student
        cur.execute("""
                    INSERT INTO Enrollment (course_id, student_id, enrolled_at)
                    VALUES (?, ?, datetime('now'))
                    """, (course_id, student_id))

        conn.commit()
        conn.close()

        self.load_enrollments(course_id)
        QMessageBox.information(self, "Success", "Student enrolled successfully!")

    def load_course_data(self):
        course_id = self.page6.comboSelectCourse.currentData()
        if course_id:
            self.load_content_history(course_id)
            self.load_assignment_history(course_id)
            self.load_enrollments(course_id)
            self.load_submissions(course_id)

    def load_content_history(self, course_id):
        self.page6.listContent.clear()
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("""
                    SELECT pdf_file, youtube_url, created_at
                    FROM CourseMaterial
                    WHERE course_id = ?
                    ORDER BY created_at DESC
                    """, (course_id,))
        for row in cur.fetchall():
            self.page6.listContent.addItem(f"PDF: {row[0]} | YouTube: {row[1]} | Added: {row[2]}")
        conn.close()

    def load_assignment_history(self, course_id):
        self.page6.listAssignment.clear()
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("""
                    SELECT pdf_file, due_date, created_at
                    FROM Assignment
                    WHERE course_id = ?
                    ORDER BY created_at DESC
                    """, (course_id,))
        for row in cur.fetchall():
            self.page6.listAssignment.addItem(f"File: {row[0]} | Due: {row[1]} | Added: {row[2]}")
        conn.close()

    def load_submissions(self, course_id):
        table = self.page6.tableSubmission
        table.setRowCount(0)
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("""
                    SELECT u.username, a.pdf_file, s.submission_time, s.grade
                    FROM AssignmentSubmission s
                             JOIN Assignment a ON s.assignment_id = a.assignment_id
                             JOIN Student st ON s.student_id = st.student_id
                             JOIN User u ON st.user_id = u.user_id
                    WHERE a.course_id = ?
                    ORDER BY s.submission_time DESC
                    """, (course_id,))
        for row in cur.fetchall():
            pos = table.rowCount()
            table.insertRow(pos)
            for i, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val is not None else "")
                if i == 4:  # Grade column
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                table.setItem(pos, i, item)
        conn.close()

    def load_enrollments(self, course_id):
        table = self.page6.tableEnrollment
        table.setRowCount(0)
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("""
                    SELECT u.username, u.email
                    FROM Enrollment e
                             JOIN Student s ON e.student_id = s.student_id
                             JOIN User u ON s.user_id = u.user_id
                    WHERE e.course_id = ?
                    """, (course_id,))
        for row in cur.fetchall():
            pos = table.rowCount()
            table.insertRow(pos)
            for i, val in enumerate(row):
                table.setItem(pos, i, QTableWidgetItem(str(val)))
        conn.close()


    def setup_student_dashboard(self):
        """Setup student dashboard page"""
        pixmap = QPixmap("assets/profilTeacher.png")
        self.page7.profilTeacher.setPixmap(pixmap)

        self.page7.dashboardBtn.clicked.connect(self.show_student_dashboard)
        self.page7.myCourseBtn.clicked.connect(lambda: self.setCurrentIndex(6))
        self.page7.logoutBtn.clicked.connect(self.logout_action)

    def goto_register(self):
        """Navigate to register page"""
        self.setCurrentIndex(1)

    def goto_login(self):
        """Navigate to login page"""
        self.setCurrentIndex(2)

    def select_role(self, role):
        """Set selected role for registration"""
        self.selected_role = role

    def show_teacher_dashboard(self):
        """Show teacher dashboard"""
        self.setCurrentIndex(3)
        if self.current_user:
            self.load_teacher_stats(self.current_user)

    def show_student_dashboard(self):
        """Show student dashboard"""
        self.setCurrentIndex(6)
        if self.current_user:
            self.load_student_stats(self.current_user)

    def show_create_course(self):
        """Show create course page"""
        self.page5.courseTitleInput.clear()
        self.page5.descriptionInput.clear()
        self.setCurrentIndex(4)

    def show_course_management(self):
        """Show course management page"""
        self.setCurrentIndex(5)

    def logout_action(self):
        """Handle logout"""
        reply = QMessageBox.question(self, 'Logout',
                                     'Are you sure you want to logout?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.current_role = None
            self.setCurrentIndex(0)

    def load_student_stats(self, username):
        """Load statistics for student dashboard"""
        try:
            conn = sqlite3.connect(DB_FILENAME)
            cur = conn.cursor()

            # Get student_id
            cur.execute("""
                        SELECT s.student_id
                        FROM Student s
                                 JOIN User u ON s.user_id = u.user_id
                        WHERE u.username = ?
                        """, (username,))
            student_id = cur.fetchone()[0]

            # Get total enrolled courses
            cur.execute("""
                        SELECT COUNT(*)
                        FROM Enrollment
                        WHERE student_id = ?
                        """, (student_id,))
            total_courses = cur.fetchone()[0]

            # Get pending assignments
            cur.execute("""
                        SELECT COUNT(*)
                        FROM Assignment a
                                 JOIN Course c ON a.course_id = c.course_id
                                 JOIN Enrollment e ON c.course_id = e.course_id
                        WHERE e.student_id = ?
                          AND a.due_date > datetime('now')
                        """, (student_id,))
            pending_assignments = cur.fetchone()[0]

            conn.close()

            # Update dashboard stats
            self.page7.totalCoursesValue.setText(str(total_courses))
            self.page7.pendingAssignmentValue.setText(str(pending_assignments))
            self.page7.studentName.setText(self.current_user)

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.page7.totalCoursesValue.setText("0")
            self.page7.pendingAssignmentValue.setText("0")

    def load_teacher_stats(self, username):
        """Load statistics for teacher dashboard"""
        try:
            conn = sqlite3.connect(DB_FILENAME)
            cur = conn.cursor()

            # Get teacher_id
            cur.execute("""
                        SELECT t.teacher_id
                        FROM Teacher t
                                 JOIN User u ON t.user_id = u.user_id
                        WHERE u.username = ?
                        """, (username,))
            teacher_id = cur.fetchone()[0]

            # Get total courses
            cur.execute("""
                        SELECT COUNT(*)
                        FROM Course
                        WHERE teacher_id = ?
                        """, (teacher_id,))
            total_courses = cur.fetchone()[0]

            # Get total students
            cur.execute("""
                        SELECT COUNT(DISTINCT student_id)
                        FROM Enrollment
                        WHERE course_id IN (SELECT course_id FROM Course WHERE teacher_id = ?)
                        """, (teacher_id,))
            total_students = cur.fetchone()[0]

            conn.close()

            # Update dashboard stats
            self.page4.coursesValue.setText(str(total_courses))
            self.page4.studentsValue.setText(str(total_students))
            self.page4.teacherName.setText(self.current_user)

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            self.page4.coursesValue.setText("0")
            self.page4.studentsValue.setText("0")

    def register_action(self):
        """Handle user registration"""
        username = self.page2.lineUsername.text()
        email = self.page2.lineEmail.text()
        password = self.page2.linePassword.text()
        confirm = self.page2.lineConfirmPassword.text()
        role = self.selected_role

        if not username or not email or not password or not confirm or not role:
            QMessageBox.warning(self, "Register Failed", "All fields and role must be filled!")
            return
        if password != confirm:
            QMessageBox.warning(self, "Register Failed", "Passwords do not match!")
            return

        try:
            conn = sqlite3.connect(DB_FILENAME)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO User (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            user_id = cur.lastrowid
            if role == "student":
                cur.execute("INSERT INTO Student (user_id) VALUES (?)", (user_id,))
            elif role == "teacher":
                cur.execute("INSERT INTO Teacher (user_id) VALUES (?)", (user_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Register Success", "Registration successful, please login!")
            self.goto_login()
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                QMessageBox.warning(self, "Register Failed", "Username already exists!")
            elif "email" in str(e):
                QMessageBox.warning(self, "Register Failed", "Email already exists!")
            else:
                QMessageBox.warning(self, "Register Failed", "Registration failed, please try again.")

    def login_action(self):
        """Handle user login"""
        username = self.page3.lineUsername.text()
        password = self.page3.linePassword.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Username and password are required!")
            return

        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()

        cur.execute("""
                    SELECT u.user_id,
                           u.username,
                           CASE
                               WHEN t.teacher_id IS NOT NULL THEN 'teacher'
                               WHEN s.student_id IS NOT NULL THEN 'student'
                               END as role
                    FROM User u
                             LEFT JOIN Teacher t ON u.user_id = t.user_id
                             LEFT JOIN Student s ON u.user_id = s.user_id
                    WHERE u.username = ?
                      AND u.password = ?
                    """, (username, password))

        user = cur.fetchone()
        conn.close()

        if user:
            user_id, username, role = user
            self.current_user = username
            self.current_role = role
            QMessageBox.information(self, "Login Success", f"Welcome, {username}!")

            if role == 'teacher':
                self.page4.teacherName.setText(username)
                self.load_teacher_stats(username)
                self.show_teacher_dashboard()
            else:
                self.page7.studentName.setText(username)
                self.load_student_stats(username)
                self.show_student_dashboard()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password!")

    def add_course_action(self):
        """Handle course creation"""
        title = self.page5.courseTitleInput.text()
        description = self.page5.descriptionInput.toPlainText()

        if not title or not description:
            QMessageBox.warning(self, "Create Course Failed", "Title and description are required!")
            return

        try:
            conn = sqlite3.connect(DB_FILENAME)
            cur = conn.cursor()

            # Get current teacher_id
            cur.execute("""
                        SELECT t.teacher_id
                        FROM Teacher t
                                 JOIN User u ON t.user_id = u.user_id
                        WHERE u.username = ?
                        """, (self.current_user,))
            teacher_id = cur.fetchone()[0]

            # Insert new course
            cur.execute("""
                        INSERT INTO Course (title, description, teacher_id, created_at)
                        VALUES (?, ?, ?, datetime('now'))
                        """, (title, description, teacher_id))

            conn.commit()
            conn.close()

            # Update dashboard stats
            self.load_teacher_stats(self.current_user)

            QMessageBox.information(self, "Success", "Course created successfully!")
            self.show_teacher_dashboard()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            QMessageBox.warning(self, "Create Course Failed", "Failed to create course. Please try again.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())