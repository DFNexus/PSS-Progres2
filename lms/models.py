from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User dengan Role
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# 2. Category (Self-referencing untuk Hierarchy)
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',  
        on_delete=models.SET_NULL,  
        null=True,  
        blank=True,  
        related_name='subcategories'
    )

    def __str__(self):
        return self.name

# --- Custom Model Managers untuk Optimasi ---
class CourseQuerySet(models.QuerySet):
    def for_listing(self):
        # Menggunakan select_related untuk JOIN ke instructor dan category (1 Query)
        return self.select_related('instructor', 'category')

class EnrollmentQuerySet(models.QuerySet):
    def for_student_dashboard(self, student):
        # Menggunakan prefetch_related untuk mengambil lessons (Reverse FK) secara efisien
        return self.filter(student=student).select_related('course').prefetch_related('course__lessons')

# 3. Course Model
class Course(models.Model):
    title = models.CharField(max_length=255)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'instructor'})
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    objects = CourseQuerySet.as_manager() # Hubungkan Manager

    def __str__(self):
        return self.title

# 4. Lesson Model (dengan Ordering)
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order'] # Kriteria: Implementasi ordering

    def __str__(self):
        return f"{self.course.title} - {self.title}"

# 5. Enrollment (dengan Unique Constraint)
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    objects = EnrollmentQuerySet.as_manager()

    class Meta:
        unique_together = ('student', 'course') # Kriteria: Unique constraint

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

# 6. Progress (Tracking)
class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.enrollment.student.username} - {self.lesson.title} ({status})"
