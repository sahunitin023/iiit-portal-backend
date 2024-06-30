from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .mixins import ReadOnlyInLine
from .models import Assign, AssignTime, Branch, Class, Dept, Program, Student, Teacher, User, Course
from .constants import degree_in_short

# Register your models here.


# ---------------------------Admin Inlines---------------------------
class ClassInLine(admin.TabularInline):
    model = Class
    extra = 0


class StudentInline(ReadOnlyInLine, admin.TabularInline):
    model = Student
    extra = 0

class AssignTimeInline(admin.TabularInline):
    model = AssignTime
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


class ProgramAdmin(admin.ModelAdmin):
    # list_display = ["name"]
    inlines = [ClassInLine]
    search_fields = ["branch", "degree"]
    ordering = ["id"]


class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "dept"]
    search_fields = ["id", "name", "dept"]


class ClassAdmin(admin.ModelAdmin):
    inlines = [StudentInline]
    list_display = ("id", "branch", "batch", "degree")
    search_fields = ("program__degree", "program__branch__name", "batch")
    ordering = ["batch"]

    def degree(self, obj):
        return degree_in_short[obj.program.degree]

    def branch(self, obj):
        return obj.program.branch.name


class StudentAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "class_id", "phone_number"]
    search_fields = ["id", "name", "class_id"]
    raw_id_fields = ["class_id"]


class TeacherAdmin(admin.ModelAdmin):
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
    inlines=[AssignTimeInline]
    list_display = ["course", "class_id", "teacher"]
    search_fields = ["course", "class_id", "teacher"]


# Register of Admin Site
admin.site.register(User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Assign, AssignAdmin)
