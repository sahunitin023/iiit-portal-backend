from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Branch, Dept, Program, User

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

admin.site.register(User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(Program, ProgramAdmin)
