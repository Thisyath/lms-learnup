import sqlite3
from models.teacher import Teacher

class TeacherController:
    def __init__(self, db_path='database.db'):
        self.db_path = db_path

    def create_teacher(self, user_id, departemen, spesialisasi):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Teacher (user_id) VALUES (?, ?, ?)",
            (user_id, departemen, spesialisasi)
        )
        conn.commit()
        teacher_id = cur.lastrowid
        conn.close()
        return Teacher(teacher_id, user_id, departemen, spesialisasi)

    def get_teacher_by_user_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Teacher WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Teacher(*row)
        return None