from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Branch, Class, Dept, Program, Student, User, Course
from .constants import degree_in_short

# Register your models here.


# Admin Inlines
class ClassInLine(admin.TabularInline):
    model = Class
    extra = 0


# Admin Panels
class DeptAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]
    search_fields = ["name", "id"]
    ordering = ["name"]


class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "dept"]
    search_fields = ["name", "dept"]
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
    list_display = ("id", "branch", "batch", "degree")
    search_fields = ("program__degree", "program__branch__name", "batch")
    ordering = ["batch"]

    def degree(self, obj):
        return degree_in_short[obj.program.degree]

    def branch(self, obj):
        return obj.program.branch.name


class StudentAdmin(admin.ModelAdmin):
    list_display=["student_id", "name", "class_id", "phone_number"]
    search_fields=["student_id", "name", "class_id"]
    raw_id_fields=["class_id"]

#Register of Admin Site
admin.site.register(User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
