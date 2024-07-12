from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.forms import ValidationError
from django.db.models.signals import post_save


from info.serializers import (
    AttendanceClassSerializer,
    FacultyAssignSerializer,
    AssignTimeSerializer,
    ClassSerializer,
    DeptSerializer,
    FacultySerializer,
    MarkClassSerializer,
    StudentAttendanceSubmitSerializer,
    StudentAttendanceViewSerializer,
    StudentMarkSubmitSerializer,
    StudentSerializer,
)
from .models import (
    Assign,
    AssignTime,
    Attendance,
    AttendanceClass,
    Class,
    Dept,
    Faculty,
    MarkClass,
    Marks,
    Student,
    StudentCourse,
    User,
)


class CustomTokenVerificationView(APIView):
    permission_classes = [AllowAny]

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


class FacultyListCreateView(generics.ListCreateAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    # permission_classes = [
    #     IsAdminUser,
    # ]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        name = validated_data.get("name")
        dob = validated_data.get("DOB")
        faculty_id = validated_data.get("id")

        # Create the Faculty User
        try:
            user = User.objects.create_user(
                username=name.split(" ")[0].lower() + "_" + faculty_id,
                password="faculty@123",
                first_name=name.split(" ")[0],
                # password=name.split(" ")[0].lower()
                # + "_"
                # + str(dob).replace("-", "")[:4],
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save the user into User Database
        user.save()
        # Save the Faculty instance and associate it with the User
        serializer.save(user=user)


class StudentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = [
    #     IsAdminUser,
    # ]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        student_id = validated_data.get("id")
        name = validated_data.get("name")

        # Create the Student User
        try:
            user = User.objects.create_user(
                username=student_id.upper(),
                password="student@123",
                first_name=name.split(" ")[0],
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save the user into User Database
        user.save()
        # Save the Faculty instance and associate it with the User
        serializer.save(user=user)


class DeptListCreateView(generics.ListCreateAPIView):
    queryset = Dept.objects.all()
    serializer_class = DeptSerializer
    # permission_classes = [IsAdminUser]


class ClassListCreateView(generics.ListCreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    # permission_classes = [IsAdminUser]


# ________________FACULTY VIEWS__________________________


# List of Classes
class FacultyAssignListView(generics.ListAPIView):
    queryset = Assign.objects.all()
    serializer_class = FacultyAssignSerializer

    def list(self, request, faculty_id, *args, **kwargs):
        if not faculty_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(faculty=faculty_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# List Class's Course Attendance
class FacultyAttendanceClassListView(generics.ListAPIView):
    queryset = AttendanceClass.objects.all()
    serializer_class = AttendanceClassSerializer

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


class FacultyStudentAttendanceCreateView(generics.CreateAPIView):
    serializer_class = StudentAttendanceSubmitSerializer

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


class FacultyClassCancelUpdateView(generics.UpdateAPIView):
    queryset = AttendanceClass.objects.all()
    lookup_field = "attendance_class_id"

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
        return Response({"message": "Class Cancelled"}, status=status.HTTP_202_ACCEPTED)


class FacultyTimetableListView(generics.ListAPIView):
    queryset = AssignTime.objects.all()
    serializer_class = AssignTimeSerializer

    def list(self, request, faculty_id, *args, **kwargs):
        if not faculty_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(assign__faculty=faculty_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# List Class's Course Mark
class FacultyMarkClassListView(generics.ListAPIView):
    queryset = MarkClass.objects.all()
    serializer_class = MarkClassSerializer

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


class FacultyStudentMarkCreateView(generics.CreateAPIView):
    serializer_class = StudentMarkSubmitSerializer

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
                    marks_instance = Marks(
                        student=student, mark_class=mark_class
                    )
                    
                marks_instance.mark = mark
                marks_instance.save()

        return validated_data


# _________________STUDENT VIEWS______________________


class StudentAttendanceRetrieveView(generics.RetrieveAPIView):

    queryset = StudentCourse.objects.all()
    serializer_class = StudentAttendanceViewSerializer
    lookup_field = "id"

    def get(self, request, id, course_id, *args, **kwargs):
        queryset = self.get_queryset().get(student=id, course=course_id)
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)


class StudentClassTimetableListView(generics.ListAPIView):
    queryset = AssignTime.objects.all()
    serializer_class = AssignTimeSerializer

    def list(self, request, class_id, *args, **kwargs):
        if not class_id:
            return Response([], status=status.HTTP_200_OK)

        queryset = self.get_queryset().filter(assign__class_id=class_id)

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ____________________OTHERS__________________________________


class ClassStudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def list(self, request, class_id, *args, **kwargs):
        class_obj = get_object_or_404(Class, id=class_id)
        queryset = (
            class_obj.student_set.all()
        )  # by reverse realtionship between Class and Student
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
