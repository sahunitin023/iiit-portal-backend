from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from .constants import (
    ATTENDANCE_STATUS_CHOICES,
    degree_choices,
    degree_in_short,
    sex_choice,
    time_slots,
    DAYS_OF_WEEK,
)


# Create your models here.
class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, "student"):
            return True
        return False

    @property
    def is_faculty(self):
        if hasattr(self, "faculty"):
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

    def save(self, *args, **kwargs):
        self.id = self.user.username.upper()
        return super(Student, self).save(*args, **kwargs)


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    id = models.CharField(primary_key=True, max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=50, choices=sex_choice, default="Male")
    DOB = models.DateField(default="1980-01-01")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Faculties"


# Assigning to faculties with course and class(Branches)
class Assign(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_id = models.ForeignKey(
        Class, on_delete=models.CASCADE, db_column="class", verbose_name="Class"
    )
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("course", "class_id", "faculty"),)

    def __str__(self):
        cl = Class.objects.get(id=self.class_id_id)
        cr = Course.objects.get(id=self.course_id)
        te = Faculty.objects.get(id=self.faculty_id)
        return "%s : %s : %s" % (te.name, cr.shortname, cl)


# useful for getting timetable for faculties
class AssignTime(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    period = models.CharField(
        max_length=50, choices=time_slots, default="09:00 - 10:00"
    )
    day = models.CharField(max_length=15, choices=DAYS_OF_WEEK)

    def clean(self):
        super().clean()
        is_occupied = (
            AssignTime.objects.filter(
                assign__teacher=self.assign.teacher, day=self.day, period=self.period
            )
            .exclude(id=self.id)
            .exists()
        )
        if is_occupied:
            raise ValidationError(
                f"The teacher {self.assign.teacher} is already assigned to another class on {self.day} during {self.period}."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(AssignTime, self).save(*args, **kwargs)
        

# Class Attendance
class AttendanceClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.IntegerField(choices=ATTENDANCE_STATUS_CHOICES, default=0)

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendance"


# Student's Attendance
class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendanceclass = models.ForeignKey(AttendanceClass, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.name} : {self.course.shortname}"

    def save(self, *args, **kwargs):
        self.date = self.attendanceclass.date
        self.course = self.attendanceclass.assign.course
        return super(Attendance, self).save(*args, **kwargs)


class AttendanceTotal(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("student", "course"),)

    @property
    def attd_class(self) -> int:
        att_class = Attendance.objects.filter(
            course=self.course, student=self.student, status=True
        ).count()
        return att_class

    @property
    def total_class(self) -> int:
        att_class = Attendance.objects.filter(
            course=self.course, student=self.student
        ).count()
        return att_class

    @property
    def classes_to_attend(self):
        total_class = Attendance.objects.filter(course=self.course, student=self.student).count()
        att_class = Attendance.objects.filter(course=self.course, student=self.student, status=True).count()
        cta = 3 * total_class - 4 * att_class
        if cta < 0:
            return 0
        return cta
