from django.db import models
    
class Student(models.Model):
    student_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    
class Course(models.Model):
    code = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
   # class_id = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, default="127.0.0.1")

    def __str__(self):
        return f"{self.student.name} - {self.course_code.name} - {self.date}"