from django.urls import path, include
from .views import *

urlpatterns = [
    path('search/', parents_home , name='parents_home'),
]