
# Register your models here.
from django.contrib import admin
from .models import Student, Attendance,Course,Branch,Year,RollNumber
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Course)
admin.site.register(Branch)
admin.site.register(Year)
admin.site.register(RollNumber)
