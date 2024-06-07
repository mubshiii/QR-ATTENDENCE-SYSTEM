import base64
import qrcode
import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Student, Class, Attendance, Course
from io import BytesIO
import socket

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
    # Get the client's IP address from the request
    client_ip = request.META.get('REMOTE_ADDR')

    # Check if the IP has already marked attendance for this class today
    course_code_value  = request.POST.get("course_code")
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

    if request.method == "POST":
        student_id = request.POST.get("student_id")
        
        # Create an attendance record for the IP, student, class, and date
        student = get_object_or_404(Student, student_id=student_id)
        
        attendance_record = Attendance.objects.create(
            student=student,
            code=course_code,
            date=today_date,
            ip_address=client_ip  # Store the IP address with the attendance record
        )
        
        return JsonResponse({"status": "success", "message": "Attendance marked"})
    return render(request, 'attendance/mark_attendance.html')

@login_required
def view_attendance(request):
    if request.method == "GET":
        courses = Course.objects.all()
        return render(request, 'attendance/list_course.html', {'courses': courses})

    course_code = request.POST.get('course_code')
    # course_code = request.GET.get('course_code')
    course_code = get_object_or_404(course_code, code=course_code)
    attendance_records = Attendance.objects.filter(course_code=course_code, date=datetime.date.today())
    return render(request, 'attendance/view_attendance.html', {'attendance_records': attendance_records})

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