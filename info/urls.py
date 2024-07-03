from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView


from .views import CustomTokenVerificationView

urlpatterns = [
    path(
        "auth/token/", CustomTokenVerificationView.as_view(), name="token_obtain_pair"
    ),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
