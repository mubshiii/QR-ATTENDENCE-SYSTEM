import qrcode
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Student, Class, Attendance
from io import BytesIO
import datetime

@csrf_exempt
def mark_attendance(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        class_id = request.POST.get("class_id")
        
        student = get_object_or_404(Student, student_id=student_id)
        class_attended = get_object_or_404(Class, id=class_id)
        
        attendance_record, created = Attendance.objects.get_or_create(
            student=student,
            class_attended=class_attended,
            date=datetime.date.today()
        )
        
        if created:
            return JsonResponse({"status": "success", "message": "Attendance marked"})
        else:
            return JsonResponse({"status": "success", "message": "Attendance already marked"})
    return JsonResponse({"status": "error", "message": "Invalid request"})


def generate_qr_code(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(student.student_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, 'PNG')
    return HttpResponse(buffer.getvalue(), content_type="image/png")
