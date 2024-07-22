from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from django.forms import ValidationError
from django.db.models.signals import post_save
from backend import permissions
from info.serializers import *
from .models import *

@extend_schema(tags=['Auth'])
class CustomTokenVerificationView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        access_token = tokens.get("access")
        jwt_authenticator = JWTAuthentication()

        try:
            validated_token = jwt_authenticator.get_validated_token(access_token)
            user: User = jwt_authenticator.get_user(validated_token)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_superuser": user.is_superuser,
            "is_student": user.is_student,
            "is_faculty": user.is_faculty,
        }

        response_data = {
            "access": access_token,
            "refresh": tokens.get("refresh"),
            "user": user_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


# ______________ADMIN VIEWS______________________


@extend_schema(tags=["Admin"])
class FacultyListCreateView(generics.ListCreateAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAdminOrStaff]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        email = validated_data.get("email") or ""
        faculty_id = validated_data.get("id")
        name_parts = validated_data.get("name").split(" ")

        # Create the Faculty User
        try:
            user = User.objects.create_user(
                username=name_parts[0].lower() + "_" + faculty_id.upper(),
                password="faculty@123",
                first_name=name_parts[0],
                last_name=" ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                email=email,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save the user into User Database
        user.save()
        # Save the Faculty instance and associate it with the User
        serializer.save(user=user)


@extend_schema(tags=["Admin"])
class StudentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminOrStaff]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        student_id = validated_data.get("id")
        email = validated_data.get("email") or ""
        name_parts = validated_data.get("name").split(" ")

        # Create the Student User
        try:
            user = User.objects.create_user(
                username=student_id.upper(),
                password="student@123",
                first_name=name_parts[0],
                last_name=" ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                email=email,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save the user into User Database
        user.save()
        # Save the Faculty instance and associate it with the User
        serializer.save(user=user)


@extend_schema(tags=["Admin"])
class DeptListCreateView(generics.ListCreateAPIView):
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    permission_classes = [permissions.IsAdminOrStaff]


@extend_schema(tags=["Admin"])
class ClassListCreateView(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAdminOrStaff]


# ________________FACULTY VIEWS__________________________


# List of Classes
@extend_schema(tags=["Faculty"])
class FacultyAssignListView(generics.ListAPIView):
    queryset = Assign.objects.all()
    serializer_class = FacultyAssignSerializer
    permission_classes = [permissions.IsFaculty]

    def list(self, request, faculty_id, *args, **kwargs):
        if not faculty_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(faculty=faculty_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# List Class's Course Attendance
@extend_schema(tags=["Faculty"])
class FacultyAttendanceClassListView(generics.ListAPIView):
    queryset = AttendanceClass.objects.all()
    serializer_class = AttendanceClassSerializer
    permission_classes = [permissions.IsFaculty]

    def list(self, request, faculty_id=None, *args, **kwargs):
        course_id = request.data.get("course") or None
        class_id = request.data.get("class") or None
        if not course_id or not class_id or not faculty_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(
            assign__course=course_id,
            assign__class_id=class_id,
            assign__faculty=faculty_id,
        )

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Faculty"])
class FacultyStudentAttendanceCreateView(generics.CreateAPIView):
    serializer_class = StudentAttendanceSubmitSerializer
    permission_classes = [permissions.IsFaculty]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        attd_class_id = validated_data.get("attd_class")
        absent_students = validated_data.get("absent_students")

        try:
            attendance_class = AttendanceClass.objects.get(pk=attd_class_id)
        except AttendanceClass.DoesNotExist:
            raise ValidationError("AttendanceClass does not exist")
        # Attendance Create
        if attendance_class.status == 0:
            attendance_instances = []
            class_students = Student.objects.filter(
                class_id=attendance_class.assign.class_id
            )

            for student in class_students:

                status = student.id not in absent_students

                attendance_instance = Attendance(
                    student=student,
                    attendanceclass=attendance_class,
                    status=status,
                    course=attendance_class.assign.course,
                    date=attendance_class.date,
                )
                attendance_instances.append(attendance_instance)

            Attendance.objects.bulk_create(attendance_instances)

            # Manually trigger post_save signals
            for instance in attendance_instances:
                post_save.send(sender=Attendance, instance=instance, created=True)

            # Updating status of the AttendanceClass as "Attendance Marked"
            attendance_class.status = 1
            attendance_class.save()

        # Attendance update
        elif attendance_class.status == 1:

            for attendance in Attendance.objects.filter(
                attendanceclass=attendance_class
            ):
                attendance.status = attendance.student.id not in absent_students
                attendance.save()

        else:
            return Response(
                data={"message": "Class has already been cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return validated_data


@extend_schema(tags=["Faculty"])
class FacultyClassCancelUpdateView(generics.UpdateAPIView):
    queryset = AttendanceClass.objects.all()
    lookup_field = "attendance_class_id"
    permission_classes = [permissions.IsFaculty]
    serializer_class = AttendanceClassSerializer

    def get_attendance_class_id(self, request, attendance_class_id, *args, **kwargs):
        return attendance_class_id

    def partial_update(self, request, attendance_class_id, *args, **kwargs):
        try:
            attd_class = AttendanceClass.objects.get(pk=attendance_class_id)
        except:
            return Response(
                {"error": "Provide a valid Attendance Class ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        attd_class.status = 2
        attd_class.save()
        data = AttendanceClassSerializer(attd_class, many=False).data
        return Response(data=data, status=status.HTTP_202_ACCEPTED)


@extend_schema(tags=["Faculty"])
class FacultyClassAttendanceListView(generics.ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsFaculty]

    def list(self, request, attendanceclass_id=None, *args, **kwargs):

        if not attendanceclass_id:
            return Response(
                data={"message": "Attendance Class ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(attendanceclass_id=attendanceclass_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Faculty"])
class FacultyTimetableListView(generics.ListAPIView):
    queryset = AssignTime.objects.all()
    serializer_class = AssignTimeSerializer
    permission_classes = [permissions.IsFaculty]

    def list(self, request, faculty_id, *args, **kwargs):
        if not faculty_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(assign__faculty=faculty_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# List Class's Course Mark
@extend_schema(tags=["Faculty"])
class FacultyMarkClassListView(generics.ListAPIView):
    queryset = MarkClass.objects.all()
    serializer_class = MarkClassSerializer
    permission_classes = [permissions.IsFaculty]

    def list(self, request, faculty_id=None, *args, **kwargs):
        course_id = request.data.get("course") or None
        class_id = request.data.get("class") or None
        if not course_id or not class_id or not faculty_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(
            assign__course=course_id,
            assign__class_id=class_id,
            assign__faculty=faculty_id,
        )

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Faculty"])
class FacultyStudentMarkCreateView(generics.CreateAPIView):
    serializer_class = StudentMarkSubmitSerializer
    permission_classes = [permissions.IsFaculty]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        mark_class_id = validated_data.get("mark_class")
        students_mark = validated_data.get("students_mark")

        try:
            mark_class = MarkClass.objects.get(pk=mark_class_id)
        except MarkClass.DoesNotExist:
            raise ValidationError("MarkClass does not exist")

        # Mark Create
        if not mark_class.status:

            for student_id, mark in students_mark.items():
                try:
                    student = Student.objects.get(pk=student_id)
                except Student.DoesNotExist:
                    raise ValidationError(
                        f"Student with id {student_id} does not exist"
                    )

                marks_instance = Marks(
                    student=student, mark_class=mark_class, mark=mark
                )
                marks_instance.save()

            # Marks.objects.bulk_create(mark_instances)

            # Updating status of the AttendanceClass as "Attendance Marked"
            mark_class.status = True
            mark_class.save()

        # Mark update
        else:
            for student_id, mark in students_mark.items():
                try:
                    student = Student.objects.get(pk=student_id)
                except Student.DoesNotExist:
                    raise ValidationError(
                        f"Student with id {student_id} does not exist"
                    )

                try:
                    marks_instance = Marks.objects.get(
                        student=student,
                        mark_class=mark_class,
                    )
                except Marks.DoesNotExist:
                    marks_instance = Marks(student=student, mark_class=mark_class)

                marks_instance.mark = mark
                marks_instance.save()

        return validated_data


@extend_schema(tags=["Faculty"])
class FacultyStudentMarkListView(generics.ListAPIView):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [permissions.IsFaculty]

    def list(self, request, mark_class_id=None, *args, **kwargs):

        if not mark_class_id:
            return Response(
                data={"message": "Mark Class ID not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(mark_class_id=mark_class_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# _________________STUDENT VIEWS______________________

@extend_schema(tags=['Student'])
class StudentAttendanceListView(generics.ListAPIView):

    queryset = StudentCourse.objects.all()
    serializer_class = StudentAttendanceViewSerializer
    permission_classes = [permissions.IsStudent]

    def list(self, request, student_id, *args, **kwargs):
        queryset = self.get_queryset().filter(student=student_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@extend_schema(tags=['Student'])
class StudentClassTimetableListView(generics.ListAPIView):
    queryset = AssignTime.objects.all()
    serializer_class = AssignTimeSerializer
    permission_classes = [permissions.IsStudent]

    def list(self, request, class_id, *args, **kwargs):
        if not class_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(assign__class_id=class_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@extend_schema(tags=['Student'])
class StudentMarkListView(generics.ListAPIView):

    queryset = StudentCourse.objects.all()
    serializer_class = StudentMarkViewSerializer
    permission_classes = [permissions.IsStudent]

    def list(self, request, student_id, *args, **kwargs):
        queryset = self.get_queryset().filter(student=student_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ____________________OTHERS__________________________________

@extend_schema(tags=['Faculty', 'Other'])
class ClassStudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, class_id, *args, **kwargs):
        class_obj = get_object_or_404(Class, id=class_id)
        queryset = (
            class_obj.student_set.all()
        )  # by reverse realtionship between Class and Student
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@extend_schema(tags=['Other'])
class ProfileRetrieveView(generics.RetrieveAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]
