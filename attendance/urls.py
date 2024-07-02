from django.urls import path
from .views import generate_qr_code, mark_attendance,add_attendance,view_options,view_monthly_attendance, view_attendance, faculty_login, faculty_logout,faculty_home, attendance_submitted

urlpatterns = [
    path('', faculty_login, name='faculty_login'),
    path('faculty_home/', faculty_home, name='faculty_home'),
    path('generate_qr/', generate_qr_code, name='generate_qr_code'),
    path('mark_attendance/', mark_attendance, name='mark_attendance'),
    path('view_attendance/', view_attendance, name='view_attendance'),
    path('add_attendance/', add_attendance, name='add_attendance'),
    path('faculty/logout/', faculty_logout, name='faculty_logout'),  
    path('submitted/', attendance_submitted, name='submitted'),  
    path('view_monthly_attendance/',view_monthly_attendance, name='view_monthly_attendance'),
    path('view_options/', view_options, name='view_options'),

]
