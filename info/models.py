from django.db import models
from django.contrib.auth.models import AbstractUser

degree_choices = (
    ("Bachelor of Technology", "Bachelor of Technology"),
    ("Master of Technology", "Master of Technology"),
    ("Doctor of Philosophy", "Doctor of Philosophy"),
)

degree_in_short = {
    "Bachelor of Technology": "B. Tech",
    "Master of Technology": "M. Tech",
    "Doctor of Philosophy": "PHD",
}


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