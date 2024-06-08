
# Register your models here.
from django.contrib import admin
from .models import Student, Attendance,Course
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Course)
