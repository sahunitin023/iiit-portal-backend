from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes

from .models import *


class UserSerializer(serializers.ModelSerializer):
    other_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "other_info",
        ]

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_other_info(self, obj: User):
        if obj.is_faculty:
            faculty = Faculty.objects.get(user=obj)
            return FacultySerializer(faculty).data
        if obj.is_student:
            student = Student.objects.get(user=obj)
            return StudentSerializer(student).data
        return None


class DeptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Dept
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        exclude = ["dept"]


class ClassSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ["id", "degree", "branch", "batch", "sem", "class_name"]
        read_only_fields = ("class_name",)
        
    @extend_schema_field(serializers.CharField)
    def get_class_name(self, obj):
        return str(obj)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        exclude = ["user"]


class FacultySerializer(serializers.ModelSerializer):

    class Meta:
        model = Faculty
        exclude = ["user"]


class AttendanceClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceClass
        exclude = ["assign"]


class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        exclude = ["id"]


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        exclude = ["id"]


# Assign Serializer for Faculty View
class FacultyAssignSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    class_info = ClassSerializer(source="class_id")
    # faculty = FacultySerializer()
    name = serializers.SerializerMethodField()
    # assigntimes = serializers.SerializerMethodField()

    class Meta:
        model = Assign
        fields = [
            "name",
            "faculty",
            "class_info",
            "course",
            # "assigntimes",
        ]

    @extend_schema_field(serializers.CharField)
    def get_name(self, obj):
        return str(obj)

    # def get_assigntimes(self, obj):
    #     assign_obj = get_object_or_404(Assign, id=obj.id)
    #     queryset = assign_obj.assigntime_set.all()
    #     serializer = AssignTimeInLineSerializer(queryset, many=True)
    #     return serializer.data


# Assign Serializer for Timetable View
class AssignTimetableInlineSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    class_info = serializers.SerializerMethodField()
    faculty = serializers.SerializerMethodField()

    class Meta:
        model = Assign
        fields = ["course", "class_info", "faculty"]
        
    @extend_schema_field(serializers.CharField)
    def get_course(self, obj: Assign):
        return obj.course.name

    @extend_schema_field(serializers.CharField)
    def get_faculty(self, obj: Assign):
        return obj.faculty.name

    @extend_schema_field(serializers.CharField)
    def get_class_info(self, obj: Assign):
        return f"{obj.class_id.branch.short_name} {obj.class_id.batch}"


# class AssignTimeInLineSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = AssignTime
#         fields = ["period", "day"]


class AssignTimeSerializer(serializers.ModelSerializer):
    assign = AssignTimetableInlineSerializer()

    class Meta:
        model = AssignTime
        fields = ["period", "day", "assign"]


class StudentAttendanceSubmitSerializer(serializers.Serializer):
    attd_class = serializers.IntegerField()
    absent_students = serializers.ListField(child=serializers.CharField())


class StudentAttendanceViewSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    attd_class = serializers.SerializerMethodField()
    total_class = serializers.SerializerMethodField()
    classes_to_attend = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentCourse
        fields = ["course", "attd_class", "total_class", "classes_to_attend"]

    @extend_schema_field(serializers.CharField)
    def get_total_class(self, obj):
        return obj.total_class

    @extend_schema_field(serializers.CharField)
    def get_attd_class(self, obj):
        return obj.attd_class

    @extend_schema_field(serializers.CharField)
    def get_classes_to_attend(self, obj):
        return obj.classes_to_attend

class MarksInlineSerializer(serializers.ModelSerializer):
    test_name = serializers.SerializerMethodField()

    class Meta:
        model = Marks
        fields = ["test_name", "mark"]

    @extend_schema_field(serializers.CharField)
    def get_test_name(self, obj: Marks):
        return obj.mark_class.test_name


class StudentMarkViewSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    marks = serializers.ListField(source="course_marks", child=MarksInlineSerializer())

    class Meta:
        model = StudentCourse
        fields = [
            "course",
            "marks",
        ]


class MarkClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkClass
        exclude = ["assign"]


class StudentMarkSubmitSerializer(serializers.Serializer):
    mark_class = serializers.IntegerField()
    students_mark = serializers.DictField(child=serializers.IntegerField())
