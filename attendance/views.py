import base64
import qrcode
import datetime
import pandas as pd
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
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
from django.db.models import Count

@login_required
def faculty_home(request):
    return render(request, 'attendance/faculty_home.html')

def attendance_submitted(request):
    return render(request, 'attendance/submitted.html')

@login_required
def generate_qr_code(request):
    course_code = request.GET.get('course_code')
    qr_code_url = None

    if course_code:
        # Validate course code against the database
        course = get_object_or_404(Course, code=course_code)

        # Get the computer's IP address dynamically
        ip_address = socket.gethostbyname(socket.gethostname())

        # Construct the attendance URL with the computer's IP address
        attendance_url = f"http://{ip_address}:8000/mark_attendance/?course_code={course_code}"

        # Generate QR code using the attendance URL
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(attendance_url)
        qr.make(fit=True)

        # Convert QR code image to base64 string
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
        # Get the client's IP address from the request
        client_ip = request.META.get('REMOTE_ADDR')

        # Check if the IP has already marked attendance for this class today
        course_code_value = request.POST.get("course_code")
        course_code = get_object_or_404(Course, code=course_code_value)
        today_date = datetime.date.today()

        # Check if there is an attendance record for this IP, class, and date
        existing_record = Attendance.objects.filter(
            ip_address=client_ip,
            course_code=course_code,
            date=today_date
        ).first()

        if existing_record:
            return HttpResponseForbidden("Attendance already marked for this IP address")

        student_id = request.POST.get("student_id")

        # Create an attendance record for the IP, student, class, and date
        student = get_object_or_404(Student, student_id=student_id)

        attendance_record = Attendance.objects.create(
            student=student,
            course_code=course_code,
            date=today_date,
            ip_address=client_ip  # Store the IP address with the attendance record
        )

        return redirect('submitted')

    return render(request, 'attendance/mark_attendance.html')

@login_required
def view_attendance(request):
    if request.method == "GET":
        return render(request, 'attendance/select_date.html')

    if request.method == "POST":
        date_str = request.POST.get('date')
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                date = datetime.datetime.strptime(date_str, '%B %d, %Y').date()
            except ValueError:
                return render(request, 'attendance/select_date.html', {'error': 'Invalid date format'})

        if 'course_code' not in request.POST:
            courses = Course.objects.all()
            return render(request, 'attendance/list_course.html', {'courses': courses, 'date': date})

        course_code = request.POST.get('course_code')
        course = get_object_or_404(Course, code=course_code)
        attendance_records = Attendance.objects.filter(course_code=course, date=date).order_by('student__roll_no__number')
        
        # Prepare attendance data
        students = Student.objects.filter(branch=course.branch, year=course.year).order_by('roll_no__number')
        attendance_data = []
        for student in students:
            status = "Present" if attendance_records.filter(student=student).exists() else "Absent"
            attendance_data.append({
                'student': student,
                'status': status
            })

         # Check if the user wants to export the data as PDF
        if 'export_pdf' in request.POST:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="attendance_{course.code}_{date}.pdf"'

            # Create the PDF object, using the response object as its "file."
            p = canvas.Canvas(response, pagesize=letter)
            width, height = letter

            # Title
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 100, f"Attendance for {course.name} on {date}")

            # Table header
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, height - 150, "Roll Number")
            p.drawString(150, height - 150, "Student Name")
            p.drawString(600, height - 150, "Status")

            # Table rows
            y = height - 170
            p.setFont("Helvetica", 12)
            for record in attendance_data:
                p.drawString(50, y, str(record['student'].roll_no.number))
                p.drawString(150, y, record['student'].name)
                p.drawString(600, y, record['status'])
                y -= 20

                # Check if we need to create a new page
                if y < 50:
                    p.showPage()
                    y = height - 50
                    p.setFont("Helvetica", 12)

            # Close the PDF object cleanly, and return the response.
            p.showPage()
            p.save()
            return response

        return render(request, 'attendance/view_attendance.html', {'attendance_data': attendance_data, 'course': course, 'date': date})

def faculty_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('faculty_home')  # Redirect to QR code generation page
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'attendance/faculty_login.html')

def faculty_logout(request):
    logout(request)
    return redirect('faculty_login')

@login_required
def add_attendance(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        course_code = request.POST.get("course_code")
        date = request.POST.get("date")

        student = get_object_or_404(Student, student_id=student_id)
        course = get_object_or_404(Course, code=course_code)

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

    courses = Course.objects.all()
    return render(request, 'attendance/add_attendance.html', {'courses': courses})

def  select_date(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        return redirect('list_course', date=date)
    return render(request, 'select_date.html')

def list_course(request, date):
    courses = Course.objects.all()
    return render(request, 'list_course.html', {'date': date, 'courses': courses})

