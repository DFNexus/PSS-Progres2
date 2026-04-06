from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Course, Lesson, Enrollment

class CustomUserAdmin(UserAdmin):
    # Menambahkan field 'role' ke dalam tampilan detail user di Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role',)}),
    )
    # Menambahkan field 'role' saat membuat user baru lewat Admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('role',)}),
    )
    # Menampilkan kolom role di daftar tabel user
    list_display = ['username', 'email', 'role', 'is_staff']

# Register model dengan class CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

# Sisanya tetap sama
admin.site.register(Category)
admin.site.register(Enrollment)

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category')
    inlines = [LessonInline]
