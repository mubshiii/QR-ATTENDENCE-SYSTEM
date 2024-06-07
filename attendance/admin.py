
# Register your models here.
from django.contrib import admin
from .models import Student, Class, Attendance,Course

admin.site.register(Student)
admin.site.register(Class)
admin.site.register(Attendance)
admin.site.register(Course)
