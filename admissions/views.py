from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse, Http404
from .models import Student, Application, Course, CourseSchedule
from django.contrib.auth import logout
import random
from django.utils.dateparse import parse_date
from datetime import timedelta
from django.contrib.auth import logout


# ==========================
# HOME, ABOUT, CONTACT
# ==========================

def home(request):
    return render(request, 'admissions/home.html')

def about(request):
    return render(request, 'admissions/about.html')

def contact(request):
    return render(request, 'admissions/contact.html')

#===========================
#ADMIN LOGIN 
#===========================
def login_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')  # redirect to admin dashboard
        else:
            messages.error(request, 'Invalid credentials or not an admin user.')
            storage = messages.get_messages(request)
            storage.used = True

    return render(request, 'admissions/login_admin.html')

def admin_logout(request):
    request.session.flush()  # clears admin session
    logout(request)  # clears Django auth session
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

# ==========================
# ADMIN PANEL
# ==========================
def admin_dashboard(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    applications = Application.objects.all().order_by('-applied_date')

    # ✅ Apply date filter if provided
    if start_date and end_date:
        start = parse_date(start_date)
        end = parse_date(end_date)
        if start and end:
            applications = applications.filter(applied_date__range=[start, end + timedelta(days=1)])

    courses = Course.objects.all()
    schedules = CourseSchedule.objects.all()

    context = {
        'applications': applications,
        'courses': courses,
        'schedules': schedules,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }

    return render(request, 'admissions/admin_dashboard.html', context)

def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        department = request.POST.get('department')
        duration = request.POST.get('duration')
        description = request.POST.get('description')

        if not course_name or not department or not duration:
            messages.error(request, 'All fields except description are required!')
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('add_course')

        Course.objects.create(
            course_name=course_name,
            department=department,
            duration=duration,
            description=description
        )
        messages.success(request, '✅ Course added successfully!')
        storage = messages.get_messages(request)
        storage.used = True
        return redirect('admin_dashboard')

    return render(request, 'admissions/add_course.html')


def add_schedule(request):
    courses = Course.objects.all()
    if request.method == 'POST':
        course_id = request.POST.get('course')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        instructor_name = request.POST.get('instructor_name')

        if not course_id or not start_date or not end_date or not instructor_name:
            messages.error(request, 'All fields are required!')
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('add_schedule')

        course = get_object_or_404(Course, id=course_id)
        CourseSchedule.objects.create(
            course=course,
            start_date=start_date,
            end_date=end_date,
            instructor_name=instructor_name
        )
        messages.success(request, '✅ Course schedule added successfully!')
        storage = messages.get_messages(request)
        storage.used = True
        return redirect('admin_dashboard')

    return render(request, 'admissions/add_schedule.html', {'courses': courses})


# ✅ Approve application (AJAX)
def approve_application(request, application_id):
        app = get_object_or_404(Application, id=application_id)
        app.status = 'Approved'
        app.save()
        return JsonResponse({'message': f'{app.student.full_name} application approved successfully!'})
    
# ❌ Reject application (AJAX)
def reject_application(request, application_id):
    
        app = get_object_or_404(Application, id=application_id)
        app.status = 'Rejected'
        app.save()
        return JsonResponse({'message': f'{app.student.full_name} application rejected.'})
   

# 🗑️ Delete all rejected applications (AJAX)
def delete_rejected(request):
    rejected = Application.objects.filter(status='Rejected')
    count = rejected.count()
    rejected.delete()
    return JsonResponse({'message': f'{count} rejected application(s) deleted successfully.'})


# ==========================
# STUDENT REGISTRATION & OTP
# ==========================
otp_storage = {}  # temporary store {email: otp}

def student_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone_number')

        if Student.objects.filter(email=email).exists():
            messages.warning(request, 'Email already registered.')
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('student_register')

        otp = str(random.randint(1000, 9999))
        otp_storage[email] = {'otp': otp, 'data': {'full_name': full_name, 'address': address, 'phone_number': phone}}

         # ✅ Send real OTP email (paste this part exactly here)
        subject = "Your College Admission Portal OTP"
        message = f"Dear {full_name},\n\nYour OTP for registration is: {otp}\n\nPlease use this OTP to verify your email address.\n\nRegards,\nAdmissions Team"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.info(request, f"OTP sent successfully to {email}.")
        except Exception as e:
            print("❌ Email sending failed:", e)
            messages.error(request, f"OTP email could not be sent. Please check your email settings.")
            storage = messages.get_messages(request)
            storage.used = True 
        return redirect(f'/verify-otp/?email={email}')

    return render(request, 'admissions/student_register.html')

def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email') or request.POST.get('email')
        otp = request.POST.get('otp')
        password = request.POST.get('password')

        if email not in otp_storage:
            return render(request, 'admissions/verify_otp.html', {'error': 'No OTP request found for this email.'})

        if otp_storage[email]['otp'] == otp:
            data = otp_storage[email]['data']
            Student.objects.create(full_name=data['full_name'], email=email, address=data['address'],
                                   phone_number=data['phone_number'], password=password)
            del otp_storage[email]
            messages.success(request, 'Registration successful! You can now log in.')
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('student_login')
        else:
            return render(request, 'admissions/verify_otp.html', {'error': 'Invalid OTP. Try again.'})

    return render(request, 'admissions/verify_otp.html')


# ==========================
# STUDENT LOGIN / LOGOUT
# ==========================
def student_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            student = Student.objects.get(email=email, password=password)
            request.session['student_id'] = student.id
            return redirect('apply_admission')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid login credentials.')
            storage = messages.get_messages(request)
            storage.used = True
    return render(request, 'admissions/login_student.html')

def student_logout(request):
    request.session.flush()  # clears student session
    logout(request)  # clears Django auth session
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

# ==========================
# FORGOT PASSWORD FLOW
# ==========================
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not Student.objects.filter(email=email).exists():
            messages.error(request, 'No account found with that email.')
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('forgot_password')

        # generate OTP and send email
        otp = str(random.randint(1000, 9999))
        otp_storage[email] = {'otp': otp}  # reuse your existing otp_storage

        subject = "Password Reset OTP - College Admissions Portal"
        message = f"Your OTP for password reset is: {otp}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, f"OTP sent successfully to {email}.")
            storage = messages.get_messages(request)
            storage.used = True
            return redirect(f'/reset-password/?email={email}')
        except Exception as e:
            print("❌ Email sending failed:", e)
            messages.error(request, 'Failed to send OTP. Try again later.')
            storage = messages.get_messages(request)
            storage.used = True
    return render(request, 'admissions/forgot_password.html')


def reset_password(request):
    email = request.GET.get('email') or request.POST.get('email')
    if request.method == 'POST':
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        if email not in otp_storage:
            messages.error(request, 'No OTP request found. Please retry.')
            storage = messages.get_messages(request)
            storage.used = True
            return redirect('forgot_password')

        if otp_storage[email]['otp'] == otp:
            student = Student.objects.filter(email=email).first()
            if student:
                student.password = new_password
                student.save()
                del otp_storage[email]
                messages.success(request, 'Password reset successful! You can now log in.')
                storage = messages.get_messages(request)
                storage.used = True
                return redirect('student_login')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            storage = messages.get_messages(request)
            storage.used = True
    return render(request, 'admissions/reset_password.html', {'email': email})

# ==========================
# STUDENT APPLICATION FLOW
# ==========================
def apply_admission(request):
    if 'student_id' not in request.session:
        return redirect('student_login')

    student = Student.objects.get(id=request.session['student_id'])
    courses = Course.objects.all()

    if request.method == 'POST':
        course_id = request.POST.get('course')
        dob = request.POST.get('dob')
        transcript = request.FILES.get('transcript')

        course = get_object_or_404(Course, id=course_id)
        Application.objects.create(
            student=student,
            course=course,
            name=student.full_name,
            email=student.email,
            dob=dob,
            transcript=transcript,
            status='Pending'
        )
        messages.success(request, 'Application submitted successfully!')
        storage = messages.get_messages(request)
        storage.used = True
        return redirect('check_status')

    return render(request, 'admissions/apply_admission.html', {'student': student, 'courses': courses})


def check_status(request):
    if 'student_id' not in request.session:
        return redirect('student_login')

    student = Student.objects.get(id=request.session['student_id'])
    application = Application.objects.filter(student=student).last()

    return render(request, 'admissions/check_status.html', {
        'student': student,
        'application': application
    })


def view_schedule(request):
    if 'student_id' not in request.session:
        return redirect('student_login')

    student = Student.objects.get(id=request.session['student_id'])
    application = Application.objects.filter(student=student, status='Approved').last()

    if not application:
        return render(request, 'admissions/view_schedule.html', {'error': 'No records due to rejection or pending status.'})

    course = application.course
    schedules = CourseSchedule.objects.filter(course=course)
    return render(request, 'admissions/view_schedule.html', {'course': course, 'schedules': schedules})

# ======================================================
# COURSE MANAGEMENT (EDIT / DELETE)
# ======================================================

def edit_course(request, course_id):
    """Edit an existing course"""
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.course_name = request.POST.get('course_name')
        course.department = request.POST.get('department')
        course.duration = request.POST.get('duration')
        course.description = request.POST.get('description')
        course.save()
        messages.success(request, '✅ Course updated successfully!')
        storage = messages.get_messages(request)
        storage.used = True
        return redirect('admin_dashboard')
    return render(request, 'admissions/edit_course.html', {'course': course})


def delete_course(request, course_id):
    """Delete a course"""
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.info(request, '🗑️ Course deleted successfully!')
    storage = messages.get_messages(request)
    storage.used = True
    return redirect('admin_dashboard')


# ======================================================
# SCHEDULE MANAGEMENT (EDIT / DELETE)
# ======================================================

def edit_schedule(request, schedule_id):
    """Edit a course schedule"""
    schedule = get_object_or_404(CourseSchedule, id=schedule_id)
    courses = Course.objects.all()
    if request.method == 'POST':
        course_id = request.POST.get('course')
        schedule.course = get_object_or_404(Course, id=course_id)
        schedule.start_date = request.POST.get('start_date')
        schedule.end_date = request.POST.get('end_date')
        schedule.instructor_name = request.POST.get('instructor_name')
        schedule.save()
        messages.success(request, '✅ Schedule updated successfully!')
        storage = messages.get_messages(request)
        storage.used = True
        return redirect('admin_dashboard')
    return render(request, 'admissions/edit_schedule.html', {'schedule': schedule, 'courses': courses})


def delete_schedule(request, schedule_id):
    """Delete a course schedule"""
    schedule = get_object_or_404(CourseSchedule, id=schedule_id)
    schedule.delete()
    messages.info(request, '🗑️ Schedule deleted successfully!')
    storage = messages.get_messages(request)
    storage.used = True
    return redirect('admin_dashboard')
