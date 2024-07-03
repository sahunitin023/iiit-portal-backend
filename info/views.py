from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from info.serializers import FacultySerializer, StudentSerializer
from .models import Dept, Faculty, Student, User


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


class AdminFacultyCreateView(generics.CreateAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes=[IsAdminUser, ]

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


class AdminStudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes=[IsAdminUser, ]

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