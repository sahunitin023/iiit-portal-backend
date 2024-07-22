from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView


from .views import *

urlpatterns = [
    path("auth/token/", CustomTokenVerificationView.as_view(), name="token_obtain_pair"),
    # path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    path("admin/faculty/", FacultyListCreateView.as_view(), name="list&add_faculty"),
    path("admin/student/", StudentListCreateAPIView.as_view(), name="list&add_student"),
    path("admin/dept/", DeptListCreateView.as_view(), name="list&add_departments"),
    path("admin/class/", ClassListCreateView.as_view(), name="list&add_classes"),
    
    path("faculty/<str:faculty_id>/classes/", FacultyAssignListView.as_view(), name="list_faculty_classes"),
    path("faculty/<str:faculty_id>/attendanceclass/", FacultyAttendanceClassListView.as_view(), name="faculty_attendanceclass"),
    path("faculty/class/attendance/submit/", FacultyStudentAttendanceCreateView.as_view(), name="class_attendance_submit"),
    path("faculty/class/cancel/<int:attendance_class_id>/", FacultyClassCancelUpdateView.as_view(), name="class_cancel"),
    path("faculty/class/attendance/<int:attendanceclass_id>/", FacultyClassAttendanceListView.as_view(), name="class_attendance_view"),
    path("faculty/<str:faculty_id>/timetable/", FacultyTimetableListView.as_view(), name="faculty_timetable"),
    path("faculty/<str:faculty_id>/markclass/", FacultyMarkClassListView.as_view(), name="faculty_markclass"),
    path("faculty/class/marks/submit/", FacultyStudentMarkCreateView.as_view(), name="class_mark_submit"),
    path("faculty/class/marks/<int:mark_class_id>/", FacultyStudentMarkListView.as_view(), name="class_marks_view"),

    path("student/<str:student_id>/attendance/", StudentAttendanceListView.as_view(), name="view_student_attendance"),
    path("student/<str:student_id>/marks/", StudentMarkListView.as_view(), name="view_student_marks"),

    path("class/<str:class_id>/timetable/", StudentClassTimetableListView.as_view(), name="class_timetable"),
    path("class/<str:class_id>/students/", ClassStudentListView.as_view(), name="list_class_students"),
    path("user/<int:id>/", ProfileRetrieveView.as_view(), name="get_user_profile"),
]
