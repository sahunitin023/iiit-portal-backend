from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .constants import (
    ATTENDANCE_STATUS_CHOICES,
    degree_choices,
    degree_in_short,
    sex_choice,
    time_slots,
    DAYS_OF_WEEK,
    test_name,
    test_total_mark,
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


class Course(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    shortname = models.CharField(max_length=10)
    credits = models.IntegerField()

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


class Class(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    degree = models.CharField(choices=degree_choices)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    batch = models.CharField(help_text="E.g 2021-25")
    sem = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.branch} {self.batch}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.CharField(primary_key=True, max_length=15)
    class_id = models.ForeignKey(
        Class, on_delete=models.CASCADE, db_column="class", verbose_name="Class"
    )
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=50, choices=sex_choice, default="Male")
    DOB = models.DateField(default="2000-01-01")
    phone_number = models.CharField(
        max_length=13, help_text="Include Country Code (+91)", unique=True
    )
    email = models.EmailField(null=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        self.id = self.user.username.upper()
        return super(Student, self).save(*args, **kwargs)


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.CharField(primary_key=True, max_length=100)
    dept = models.ForeignKey(Dept, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    sex = models.CharField(max_length=50, choices=sex_choice, default="Male")
    DOB = models.DateField(default="1980-01-01")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Faculties"

    def save(self, *args, **kwargs):
        self.id = self.id.upper()
        return super(Faculty, self).save(*args, **kwargs)


# Assigning to faculties with course and class(Branches)
class Assign(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_id = models.ForeignKey(
        Class, on_delete=models.CASCADE, db_column="class", verbose_name="Class"
    )
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            (
                "course",
                "class_id",
            ),
        )

    def __str__(self):
        return f"{self.course} : {self.class_id.id}"


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
                assign__faculty=self.assign.faculty, day=self.day, period=self.period
            )
            .exclude(id=self.id)
            .exists()
        )
        if is_occupied:
            raise ValidationError(
                f"The faculty {self.assign.faculty} is already assigned to another class on {self.day} during {self.period}."
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
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendanceclass = models.ForeignKey(AttendanceClass, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)  # remove
    date = models.DateField(null=True)  # remove

    def __str__(self):
        return f"{self.student.name} : {self.course.shortname}"



class AttendanceRange(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    max_rows = 1

    def save(self, *args, **kwargs):
        if not self.pk and AttendanceRange.objects.count() == self.max_rows:
            raise ValidationError(f"Cannot have multiple semester start and end dates.")
        super(AttendanceRange, self).save(*args, **kwargs)


class MarkClass(models.Model):
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=50, choices=test_name)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = (("assign", "test_name"),)
        
    def __str__(self):
        return f"{self.assign.class_id} : {self.assign.course} : {self.test_name}"

    @property
    def total_mark(self):
        return test_total_mark[self.test_name]


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    mark_class = models.ForeignKey(MarkClass, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0)

    class Meta:
        unique_together = (("student", "mark_class"),)
        verbose_name_plural = "Marks"
        verbose_name = "Mark"

    @property
    def total_mark(self):
        return test_total_mark[self.mark_class.test_name]

    def clean(self):
        max_value = self.total_mark
        validators = [MinValueValidator(0), MaxValueValidator(max_value)]

        for validator in validators:
            validator(self.mark)

        if self.mark_class.assign.class_id != self.student.class_id:
            raise ValidationError(
                f"The student {self.student.name} is not a student of class {self.mark_class.assign.class_id.id}"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super(Marks, self).save(*args, **kwargs)


class StudentCourse(models.Model):
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
        total_class = Attendance.objects.filter(
            course=self.course, student=self.student
        ).count()
        att_class = Attendance.objects.filter(
            course=self.course, student=self.student, status=True
        ).count()
        cta = 3 * total_class - 4 * att_class
        if cta < 0:
            return 0
        return cta
    
    @property
    def course_marks(self):
        return Marks.objects.filter(
            mark_class__assign__course=self.course, student=self.student
        )
