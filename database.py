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
        kelas TEXT,
        tahun TEXT,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
    ''')

    # Teacher Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Teacher (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        departemen TEXT,
        spesialisasi TEXT,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
    ''')

    # Course Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Course (
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        deskripsi TEXT,
        teacher_id INTEGER NOT NULL,
        FOREIGN KEY (teacher_id) REFERENCES Teacher(teacher_id)
    );
    ''')

    # Enrollment Table (Student - Course Many-to-Many)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Enrollment (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (student_id) REFERENCES Student(student_id),
        FOREIGN KEY (course_id) REFERENCES Course(course_id),
        UNIQUE(student_id, course_id)
    );
    ''')

    # Assignment Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Assignment (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        due_date TEXT,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES Course(course_id)
    );
    ''')

    # Submission Table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Submission (
        submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        file_url TEXT,
        nilai REAL,
        timestamp TEXT,
        FOREIGN KEY (assignment_id) REFERENCES Assignment(assignment_id),
        FOREIGN KEY (student_id) REFERENCES Student(student_id),
        UNIQUE(assignment_id, student_id)
    );
    ''')

    # Material Table (optional, can be removed if not needed)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Material (
        material_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        file_url TEXT,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES Course(course_id)
    );
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database and tables created successfully.")