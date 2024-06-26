from django.db import models
from django.contrib.auth.models import AbstractUser
from .constants import degree_choices, degree_in_short, sex_choice


# Create your models here.
class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, "student"):
            return True
        return False

    @property
    def is_teacher(self):
        if hasattr(self, "teacher"):
            return True
        return False


class Dept(models.Model):
    id = models.CharField(primary_key="True", max_length=10)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


class Branch(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


class Program(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    degree = models.CharField(choices=degree_choices)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return f"{degree_in_short[self.degree]} in {self.branch}"


class Course(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=10)
    credits = models.IntegerField()

    def __str__(self):
        return self.name


class Class(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    batch = models.CharField(help_text="E.g 2021-25")

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.program.branch.short_name} {self.batch}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=15)
    class_id = models.ForeignKey(
        Class, on_delete=models.CASCADE, db_column="class", verbose_name="Class"
    )
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=50, choices=sex_choice, default="Male")
    DOB = models.DateField(default="2000-01-01")
    phone_number = models.CharField(
        max_length=13, help_text="Include Country Code (+91)", unique=True, blank=True
    )
    email = models.EmailField(null=True)

    def __str__(self):
        return self.id


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=50, choices=sex_choice, default="Male")
    DOB = models.DateField(default="1980-01-01")

    def __str__(self):
        return self.name


# Assigning to teachers with course and class(Branches)
class Assign(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column="class", verbose_name="Class")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("course", "class_id", "teacher"),)

    def __str__(self):
        cl = Class.objects.get(id=self.class_id_id)
        cr = Course.objects.get(id=self.course_id)
        te = Teacher.objects.get(id=self.teacher_id)
        return "%s : %s : %s" % (te.name, cr.shortname, cl)
