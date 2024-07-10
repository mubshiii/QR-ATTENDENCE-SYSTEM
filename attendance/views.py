import base64
import qrcode
import datetime
import pandas as pd
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Student,  Attendance, Course
from io import BytesIO
import socket
from django.db.models import Count, F, ExpressionWrapper, FloatField

@login_required
def faculty_home(request):
    user = request.user
    courses = Course.objects.filter(faculty=user)
    return render(request, 'attendance/faculty_home.html', {'courses': courses})


def attendance_submitted(request):
    return render(request, 'attendance/submitted.html')

@login_required
def generate_qr_code(request):
    course_code = request.GET.get('course_code')
    qr_code_url = None

    if course_code:
        course = get_object_or_404(Course, code=course_code, faculty=request.user)  # Filter by faculty

        ip_address = socket.gethostbyname(socket.gethostname())

        current_date = datetime.date.today().strftime("%Y-%m-%d")
        attendance_url = f"http://{ip_address}:8000/mark_attendance/?course_code={course_code}&date={current_date}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(attendance_url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{img_str}"

    return render(request, 'attendance/generate_qr.html', {'qr_code_url': qr_code_url})


@csrf_exempt
def mark_attendance(request):
    if request.method == "GET":
        course_code = request.GET.get("course_code")
        return render(request, 'attendance/mark_attendance.html', {'course_code': course_code})

    if request.method == "POST":
        client_ip = request.META.get('REMOTE_ADDR')

        course_code_value = request.POST.get("course_code")
        course_code = get_object_or_404(Course, code=course_code_value)
        date_str = request.POST.get('date')

        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.date.today()
        except ValueError:
            return render(request, 'attendance/mark_attendance.html', {'course_code': course_code_value, 'error': 'Invalid date format'})

        existing_record = Attendance.objects.filter(
            ip_address=client_ip,
            course_code=course_code,
            date=selected_date
        ).first()

        if existing_record:
            return render(request, 'attendance/attendance_already_marked.html', {'ip_address': client_ip})

        student_id = request.POST.get("student_id")
        
        try:
            student = Student.objects.get(student_id=student_id)
            if student.year != course_code.year:
                raise Student.DoesNotExist
        except Student.DoesNotExist:
            return render(request, 'attendance/error.html', {'student_id': student_id, 'course_code': course_code_value})

        Attendance.objects.create(
            student=student,
            course_code=course_code,
            date=selected_date,
            ip_address=client_ip
        )

        return redirect('submitted')

    return render(request, 'attendance/mark_attendance.html')

@login_required
def view_attendance(request):
    user = request.user
    courses = Course.objects.filter(faculty=user)
    if request.method == "POST":
        course_code = request.POST.get('course_code')
        date_str = request.POST.get('date')
        course = get_object_or_404(Course, code=course_code, faculty=user)  # Filter by faculty

        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'attendance/view_options.html', {'courses': courses, 'error': 'Invalid date format'})

        students = Student.objects.filter(branch=course.branch, year=course.year).order_by('roll_no__number') 
        attendance_data = []
        
        for student in students:
            is_present = Attendance.objects.filter(course_code=course, student=student, date=selected_date).exists()
            attendance_data.append({
                'student': student,
                'status': 'Present' if is_present else 'Absent'
            })

        return render(request, 'attendance/view_attendance.html', {'attendance_data': attendance_data, 'course': course, 'date': selected_date})
    return render(request, 'attendance/view_options.html', {'courses': courses})


def faculty_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('faculty_home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'attendance/faculty_login.html')

def faculty_logout(request):
    logout(request)
    return redirect('faculty_login')

@login_required
def add_attendance(request):
    user = request.user
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        course_code = request.POST.get("course_code")
        date_str = request.POST.get("date")

        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('add_attendance')

        student = get_object_or_404(Student, student_id=student_id)
        course = get_object_or_404(Course, code=course_code, faculty=user)  # Filter by faculty

        attendance, created = Attendance.objects.get_or_create(
            student=student,
            course_code=course,
            date=date
        )

        if created:
            messages.success(request, "Attendance marked successfully.")
        else:
            messages.warning(request, "Attendance already marked for this student on this date.")

        return redirect('faculty_home')

    courses = Course.objects.filter(faculty=user)  # Filter by faculty
    return render(request, 'attendance/add_attendance.html', {'courses': courses})


def view_options(request):
    current_faculty = request.user  # Assuming request.user is the logged-in user
    # Filter courses based on the current faculty
    courses = Course.objects.filter(faculty=current_faculty)
    return render(request, 'attendance/view_options.html', {'courses': courses})

@login_required
def view_monthly_attendance(request):
    user = request.user

    if request.method == "POST":
        month_str = request.POST.get('month')
        course_code = request.POST.get('course_code')

        if not month_str:
            courses = Course.objects.filter(faculty=user)
            return render(request, 'attendance/view_options.html', {'error': 'Invalid month format', 'courses': courses})

        try:
            month = datetime.datetime.strptime(month_str, '%Y-%m').date()
        except ValueError:
            courses = Course.objects.all()
            return render(request, 'attendance/view_options.html', {'error': 'Invalid month format', 'courses': courses})

        first_day = month.replace(day=1)
        last_day = (first_day + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)

        course = get_object_or_404(Course, code=course_code)
        attendance_records = Attendance.objects.filter(course_code=course, date__range=(first_day, last_day))

        if not attendance_records.exists():
            return render(request, 'attendance/no_attendance.html', {
                'error': 'No attendance records found for the selected month and course.',
                'course': course,
                'month': month
            })

        unique_dates = attendance_records.values('date').annotate(total=Count('date')).order_by()

        students = Student.objects.filter(branch=course.branch, year=course.year).order_by('roll_no__number')
        attendance_data = []

        for student in students:
            total_days = unique_dates.count()  
            present_days = unique_dates.filter(student=student).count()
            attendance_percentage = (present_days / total_days) * 100
            attendance_data.append({
                'student': student,
                'total_days': total_days,
                'present_days': present_days,
                'attendance_percentage': attendance_percentage,
                'status': 'Below 75%' if attendance_percentage < 75 else 'Above 75%'
            })
              
        if 'export_pdf' in request.POST:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="monthly_attendance_{course.code}_{month.strftime("%Y_%m")}.pdf"'

          
            p = canvas.Canvas(response, pagesize=letter)
            width, height = letter

           
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 100, f"Monthly Attendance for {course.name} - {month.strftime('%B %Y')}")

            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(15, height - 150, "Roll Number")
            p.drawString(100, height - 150, "Student Name")
            p.drawString(260, height - 150, "Total Days")
            p.drawString(330, height - 150, "Present Days")
            p.drawString(410, height - 150, "Attendance Percentage")
            p.drawString(550, height - 150, "Status")

            
            y = height - 170
            p.setFont("Helvetica", 12)
            for record in attendance_data:
                p.drawString(50, y, str(record['student'].roll_no.number))
                p.drawString(100, y, record['student'].name)
                p.drawString(290, y, str(record['total_days']))
                p.drawString(350, y, str(record['present_days']))
                p.drawString(430, y, f"{record['attendance_percentage']:.2f}%")
                p.drawString(550, y, record['status'])
                y -= 20

                if y < 50:
                    p.showPage()
                    y = height - 50
                    p.setFont("Helvetica", 12)

            p.showPage()
            p.save()
            return response

        return render(request, 'attendance/view_monthly_attendance.html', {
            'attendance_data': attendance_data,
            'course': course,
            'month': month
        })
    else:
        courses = Course.objects.filter(faculty=user)
        return render(request, 'attendance/view_options.html', {'courses': courses})
    
