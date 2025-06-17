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

        self.page4.dashboardBtn.clicked.connect(self.show_dashboard)
        self.page4.createCourseBtn.clicked.connect(self.show_create_course)
        self.page4.managementBtn.clicked.connect(self.show_management)
        self.page4.logoutBtn.clicked.connect(self.logout_action)

    def setup_create_course(self):
        """Setup create course page"""
        self.page5.addCourseBtn.clicked.connect(self.add_course_action)
        self.page5.cancelBtn.clicked.connect(lambda: self.setCurrentIndex(3))
        self.page5.previousBtn.clicked.connect(lambda: self.setCurrentIndex(3))

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

    def show_dashboard(self):
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

    def show_management(self):
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
                self.show_dashboard()
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
            self.show_dashboard()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            QMessageBox.warning(self, "Create Course Failed", "Failed to create course. Please try again.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec_())