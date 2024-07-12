from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView


from .views import *

urlpatterns = [
    path("auth/token/", CustomTokenVerificationView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    path("admin/faculty/", FacultyListCreateView.as_view(), name="list&add_faculty"),
    path("admin/student/", StudentListCreateAPIView.as_view(), name="list&add_student"),
    path("admin/class/", ClassListCreateView.as_view(), name="list&add_classes"),
    path("admin/dept/", DeptListCreateView.as_view(), name="list&add_departments"),
    
    path("faculty/<str:faculty_id>/class/", FacultyAssignListView.as_view(), name="list_faculty_classes"),
    path("faculty/<str:faculty_id>/timetable/", FacultyTimetableListView.as_view(), name="faculty_timetable"),
    path("faculty/<str:faculty_id>/class/attendance/", FacultyAttendanceClassListView.as_view(), name="faculty_class_attendance"),
    path("faculty/class/attendance/submit/", FacultyStudentAttendanceCreateView.as_view(), name="class_attendance_submit"),
    path("faculty/class/cancel/<int:attendance_class_id>/", FacultyClassCancelUpdateView.as_view(), name="class_attendance_submit"),
    path("faculty/<str:faculty_id>/class/mark/", FacultyMarkClassListView.as_view(), name="faculty_class_mark"),
    path("faculty/class/mark/submit/", FacultyStudentMarkCreateView.as_view(), name="class_mark_submit"),

    path("student/<str:id>/attendance/<str:course_id>/", StudentAttendanceRetrieveView.as_view(), name="view_student_attendance"),

    path("class/<str:class_id>/timetable/", StudentClassTimetableListView.as_view(), name="class_timetable"),
    path("class/<str:class_id>/students/", ClassStudentListView.as_view(), name="list_class_students"),
]
