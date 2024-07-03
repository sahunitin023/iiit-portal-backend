from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView


from .views import *

urlpatterns = [
    path(
        "auth/token/", CustomTokenVerificationView.as_view(), name="token_obtain_pair"
    ),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("admin/faculty/create/", AdminFacultyCreateView.as_view(), name="add_faculty"),
    path("admin/student/create/", AdminStudentCreateView.as_view(), name="add_student"),
]
