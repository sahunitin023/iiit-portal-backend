from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *
from .constants import degree_in_short

# Register your models here.


# ---------------------------Admin Inlines---------------------------
class ClassInLine(admin.TabularInline):
    model = Class
    extra = 0


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0


class AssignTimeInline(admin.TabularInline):
    model = AssignTime
    extra = 0


class AttendanceInline(admin.TabularInline):
    # can_delete = False
    # readonly_fields = ["course", "date"]
    raw_id_fields = ["student"]
    model = Attendance
    extra = 0


# ---------------------------Admin Panels---------------------------
class DeptAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]
    search_fields = ["name", "id"]
    ordering = ["name"]


class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "dept"]
    search_fields = ["name", "dept", "short_name"]
    ordering = ["id"]


class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "dept"]
    search_fields = ["id", "name", "dept"]


class ClassAdmin(admin.ModelAdmin):
    inlines = [StudentInline]
    list_display = ("id", "branch", "batch", "degree", "sem")
    search_fields = ("degree", "branch__name", "batch")
    ordering = ["batch"]

    def degree(self, obj):
        return degree_in_short[obj.degree]


class StudentAdmin(admin.ModelAdmin):
    exclude = ["id"]
    list_display = ["id", "name", "class_id", "phone_number"]
    search_fields = ["id", "name", "class_id"]
    raw_id_fields = ["class_id"]


class FacultyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "dept",
    ]
    search_fields = [
        "id",
        "name",
    ]


class AssignAdmin(admin.ModelAdmin):
    inlines = [AssignTimeInline]
    list_display = ["course", "class_id", "faculty"]
    search_fields = ["course", "class_id", "faculty"]


class AttendanceClassAdmin(admin.ModelAdmin):
    inlines = [AttendanceInline]
    list_display = ("assign", "date", "status")
    ordering = ["assign", "date"]


# class AttendanceAdmin(admin.ModelAdmin):
# exclude =['course', 'date']

# def get_exclude(self, request, obj=None):
#     if request.method == 'GET':
#         return self.exclude


# Register of Admin Site
admin.site.register(User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Assign, AssignAdmin)
# admin.site.register(MarkClass)
# admin.site.register(Marks)
# admin.site.register(AttendanceClass, AttendanceClassAdmin)
# admin.site.register(AttendanceRange)
# admin.site.register(Attendance)
