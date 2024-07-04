from rest_framework import serializers

from .models import *


class FacultySerializer(serializers.ModelSerializer):

    class Meta:
        model = Faculty
        fields = ["id", "name", "dept", "sex", "DOB"]


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ["id", "name", "class_id", "sex", "DOB", "email", "phone_number"]


class ClassSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ["id", "degree", "branch", "batch", "sem", "class_name"]
        read_only_fields = ("class_name",)

    def get_class_name(self, obj):
        return str(obj)


class DeptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dept
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"


class AssignSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class_id = ClassSerializer()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Assign
        fields = ["name", "course", "class_id"]

    def get_name(self, obj):
        return str(obj)
