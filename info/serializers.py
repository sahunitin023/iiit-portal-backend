from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import *


class DeptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dept
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"


class ClassSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ["id", "degree", "branch", "batch", "sem", "class_name"]
        read_only_fields = ("class_name",)

    def get_class_name(self, obj):
        return str(obj)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ["id", "name", "class_id", "sex", "DOB", "email", "phone_number"]


class FacultySerializer(serializers.ModelSerializer):

    class Meta:
        model = Faculty
        fields = "__all__"


# Assign Serializer for Faculty View
class FacultyAssignSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class_info = ClassSerializer(source="class_id")
    # faculty = FacultySerializer()
    name = serializers.SerializerMethodField()
    assigntimes = serializers.SerializerMethodField()

    class Meta:
        model = Assign
        fields = ["name", "faculty", "class_info", "course", "assigntimes"]

    def get_name(self, obj):
        return str(obj)

    def get_assigntimes(self, obj):
        assign_obj = get_object_or_404(Assign, id=obj.id)
        queryset = assign_obj.assigntime_set.all()
        serializer = AssignTimeInLineSerializer(queryset, many=True).data
        return serializer


# Assign Serializer for Timetable View
class TimetableAssignSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()

    class Meta:
        model = Assign
        fields = ["course", "class_info"]

    def get_course(self, obj: Assign):
        return obj.course.shortname

    def get_class_info(self, obj: Assign):
        return f"{obj.class_id.branch.short_name} {obj.class_id.batch}"


class AssignTimeInLineSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignTime
        fields = ["period", "day"]


class AssignTimeSerializer(serializers.ModelSerializer):
    assign = TimetableAssignSerializer()

    class Meta:
        model = AssignTime
        fields = ["period", "day", "assign"]
