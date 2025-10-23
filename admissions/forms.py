from django import forms
from .models import Course, CourseSchedule

# Form to add new Course
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'department', 'duration', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

# Form to add Course Schedule
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = CourseSchedule
        fields = ['course', 'start_date', 'end_date', 'instructor_name']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
