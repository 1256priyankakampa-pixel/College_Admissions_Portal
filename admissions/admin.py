from django.contrib import admin
from .models import Student, Course, Application


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'is_verified')
    search_fields = ('full_name', 'email')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'department', 'duration')
    search_fields = ('course_name', 'department')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'course', 'status', 'transcript')
    list_filter = ('status',)
    search_fields = ('student__full_name', 'course__course_name')
    actions = ['approve_applications', 'reject_applications', 'delete_rejected']

    # ✅ Custom display for student name
    def get_student_name(self, obj):
        return obj.student.full_name
    get_student_name.short_description = 'Student'

    # ✅ Approve selected applications
    def approve_applications(self, request, queryset):
        updated = queryset.update(status='Approved')
        self.message_user(request, f"{updated} application(s) approved successfully.")

    approve_applications.short_description = "Approve selected applications"

    # ❌ Reject selected applications
    def reject_applications(self, request, queryset):
        updated = queryset.update(status='Rejected')
        self.message_user(request, f"{updated} application(s) rejected successfully.")

    reject_applications.short_description = "Reject selected applications"

    # 🗑️ Delete all rejected applications
    def delete_rejected(self, request, queryset):
        rejected = queryset.filter(status='Rejected')
        count = rejected.count()
        rejected.delete()
        self.message_user(request, f"Deleted {count} rejected application(s).")

    delete_rejected.short_description = "Delete rejected applications"
