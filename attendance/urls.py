from django.urls import path
from .views import generate_qr_code, mark_attendance, view_attendance, faculty_login, faculty_logout,faculty_home, attendance_submitted

urlpatterns = [
    path('', faculty_login, name='faculty_login'),
    path('faculty_home/', faculty_home, name='faculty_home'),
    path('generate_qr/', generate_qr_code, name='generate_qr_code'),
    path('mark_attendance/', mark_attendance, name='mark_attendance'),
    path('view_attendance/', view_attendance, name='view_attendance'),
    path('faculty/logout/', faculty_logout, name='faculty_logout'),  # URL for logout
    path('submitted/', attendance_submitted, name='submitted'),  # URL for logout
]
