from dataclasses import fields
from rest_framework import serializers

from info.models import Faculty, Student


class FacultySerializer(serializers.ModelSerializer):

    class Meta:
        model = Faculty
        fields = ["id", "name", "dept", "sex", "DOB"]


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ["id", "name", "class_id", "sex", "DOB", "email", "phone_number"]