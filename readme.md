QR Attendance System

Overview
The QR Attendance System is a Django-based web application designed to streamline the process of marking attendance using QR codes. Faculty can generate unique QR codes for each class session, which students scan to mark their attendance. The system automates the attendance tracking process, making it more efficient and error-free.

Features
    -Faculty Authentication: Secure login for faculty members to manage attendance.
    -QR Code Generation: Faculty can generate QR codes for each class session.
    -Student Attendance Marking: Students scan the QR code to mark their attendance.
    -Attendance Tracking: Faculty can view attendance records by date, student, or course.
    -Error Handling: Proper feedback for invalid QR codes or unregistered students.

Project Structure
    -QR_Attendance_System/: Main project directory containing the Django settings and URLs configuration.
    -attendance/: Application directory with views, models, and templates for managing attendance.
    -templates/: HTML templates for rendering the web pages.
    -static/: Static files such as CSS, JavaScript, and images.
    -db.sqlite3: SQLite database file containing the project’s data.
    -manage.py: Django's command-line utility for administrative tasks.
    -requirements.txt: List of Python dependencies needed to run the project.

Installation

1.Clone the repository:
    git clone https://github.com/your-username/QR-ATTENDENCE-SYSTEM.git
    cd QR-ATTENDENCE-SYSTEM

2.Create and activate a virtual environment:
    python -m venv venv
# On Windows use `venv\Scripts\activate`

3.Install the required dependencies:
    pip install -r requirements.txt

4.Apply migrations:
    python manage.py migrate

5.Run the development server:
    python manage.py runserver

6.Access the application:
    Open your web browser and go to http://127.0.0.1:8000/.

Usage
    -Faculty Login: Access the faculty dashboard to generate QR codes and view attendance.
    -Student Attendance: Students can scan the QR code using their mobile devices to mark attendance.
    -View Attendance: Faculty can view and manage attendance records by selecting different options.

License
    This project is licensed under the MIT License. See the LICENSE file for more details.

Contributing
    Contributions are welcome! Please open an issue or submit a pull request for any improvements.


