from info.models import (
    Assign,
    AssignTime,
    Attendance,
    AttendanceRange,
    AttendanceClass,
    MarkClass,
    StudentCourse,
)
from .constants import test_name
from django.db.models.signals import post_save, post_delete
from datetime import timedelta
from .constants import days


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def create_attendance_class(sender, instance, **kwargs):
    if kwargs["created"]:
        start_date = AttendanceRange.objects.first().start_date
        end_date = AttendanceRange.objects.first().end_date
        for single_date in daterange(start_date, end_date):
            if single_date.isoweekday() == days[instance.day]:
                try:
                    AttendanceClass.objects.get(
                        date=single_date.strftime("%Y-%m-%d"), assign=instance.assign
                    )
                except AttendanceClass.DoesNotExist:
                    a = AttendanceClass(
                        date=single_date.strftime("%Y-%m-%d"), assign=instance.assign
                    )
                    a.save()


def delete_attendance(sender, instance: AssignTime, **kwargs):
    start_date = AttendanceRange.objects.first().start_date
    end_date = AttendanceRange.objects.first().end_date
    dates = [
        single_date
        for single_date in daterange(start_date, end_date)
        if single_date.isoweekday() == days[instance.day]
    ]
    AttendanceClass.objects.filter(assign=instance.assign, date__in=dates).delete()


def create_student_course(sender, instance: Attendance, **kwargs):
    if kwargs["created"]:
        course = instance.attendanceclass.assign.course
        student = instance.student
        try:
            StudentCourse.objects.get(course=course, student=student)
        except StudentCourse.DoesNotExist:
            a = StudentCourse(
                course=instance.attendanceclass.assign.course, student=instance.student
            )
            a.save()


def create_mark_class(sender, instance: Assign, **kwargs):
    if kwargs["created"]:
        for test in test_name:
            try:
                MarkClass.objects.get(assign=instance, test_name=test[0])
            except MarkClass.DoesNotExist:
                a = MarkClass(test_name=test[0], assign=instance)
                a.save()


post_save.connect(create_attendance_class, AssignTime)
post_save.connect(create_student_course, Attendance)
post_save.connect(create_mark_class, Assign)
post_delete.connect(delete_attendance, AssignTime)
