class Student:
    def __init__(self, student_id, user_id, kelas, tahun):
        self.student_id = student_id
        self.user_id = user_id

    def __repr__(self):
        return f"<Student {self.student_id} user:{self.user_id}>"