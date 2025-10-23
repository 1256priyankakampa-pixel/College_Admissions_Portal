from django.db import models

# -------------------------
# COURSE MODEL
# -------------------------
class Course(models.Model):
    course_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    duration = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.course_name


# -------------------------
# STUDENT MODEL
# -------------------------
class Student(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


# -------------------------
# APPLICATION MODEL
# -------------------------
class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    dob = models.DateField()
    transcript = models.FileField(upload_to='transcripts/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.course.course_name}"

    


# -------------------------
# COURSE SCHEDULE MODEL
# -------------------------
class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    instructor_name = models.CharField(max_length=100)

    def __str__(self):
         return f"{self.course.course_name} - {self.instructor_name}"
