import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # User Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    ''')

    # Student Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Student (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
    ''')

    # Teacher Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Teacher (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
    ''')

    # Course Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Course (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        teacher_id INTEGER,
        created_at TEXT,
        FOREIGN KEY (teacher_id) REFERENCES Teacher (teacher_id)
    );
    ''')

    # Enrollment Table (Student - Course Many-to-Many)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Enrollment (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        enrolled_at TEXT NOT NULL,
        FOREIGN KEY (course_id) REFERENCES Course(course_id),
        FOREIGN KEY (student_id) REFERENCES Student(student_id),
        UNIQUE(course_id, student_id) -- Tidak boleh double enroll
    );
    ''')

    # CourseMaterial
    cur.execute('''
    CREATE TABLE IF NOT EXISTS CourseMaterial (
        material_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        pdf_file TEXT NOT NULL,
        youtube_url TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (course_id) REFERENCES Course(course_id)
    ); 
    ''')

    # Assignment Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Assignment (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        pdf_file TEXT NOT NULL,
        due_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
    );
    ''')

    # Submission Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Submission (
        submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        pdf_file TEXT,
        submission_time TEXT,
        grade TEXT,
        FOREIGN KEY (assignment_id) REFERENCES Assignment(assignment_id),
        FOREIGN KEY (student_id) REFERENCES Student(student_id)
    );
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database and tables created successfully.")