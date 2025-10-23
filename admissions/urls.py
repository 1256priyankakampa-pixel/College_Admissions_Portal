from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Admin panel
    path('admin-login/', views.login_admin, name='login_admin'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    # Admin actions for applications
    path('portal-admin/approve_application/<int:application_id>/', views.approve_application, name='approve_application'),
    path('portal-admin/reject_application/<int:application_id>/', views.reject_application, name='reject_application'),
    path('portal-admin/delete_rejected/', views.delete_rejected, name='delete_rejected'),

    path('add-course/', views.add_course, name='add_course'),
    path('add-schedule/', views.add_schedule, name='add_schedule'),
    
    # Course edit/delete
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),

    # Schedule edit/delete
    path('edit-schedule/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),


    # Student routes
    path('student-register/', views.student_register, name='student_register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('student-login/', views.student_login, name='student_login'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('apply-admission/', views.apply_admission, name='apply_admission'),
    path('check-status/', views.check_status, name='check_status'),
    path('view-schedule/', views.view_schedule, name='view_schedule'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),


    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
