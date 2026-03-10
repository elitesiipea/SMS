from django.urls import path, include

from .views import (
                    student_cv,
                    student_cv_shared,
                    delete_info_or_data
                    )

urlpatterns = [
    path('student_resume/', student_cv, name="student_cv" ),
    path('student_resume/<slug:code>/', student_cv_shared, name="student_cv_shared" ),
    path('student_resume/delete/<slug:element>/<int:pk>/', delete_info_or_data, name="delete_info_or_data" ),
]