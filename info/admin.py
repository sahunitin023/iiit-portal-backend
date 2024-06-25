from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Branch, Class, Dept, Program, User, Course
from .constants import degree_in_short

# Register your models here.


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
    search_fields = ["branch", "degree"]
    ordering = ["id"]


class CourseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "dept"]
    search_fields = ["id", "name", "dept"]
    raw_id_fields = ["dept"]


class ClassAdmin(admin.ModelAdmin):
    list_display = ("branch", "batch", "degree")
    search_fields = ("program__degree", "program__branch__name", "batch")
    ordering = ["batch"]

    def degree(self, obj):
        return degree_in_short[obj.program.degree]

    def branch(self, obj):
        return obj.program.branch.name


admin.site.register(User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Class, ClassAdmin)
