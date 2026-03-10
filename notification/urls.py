from django.urls import path
from .views import notification_list_json, create_notification, list_notification, edit_notification, delete_notification, notification_list_json_detail

urlpatterns = [
    # ...
    path('api/notifications/create/', create_notification, name='create_notification'),
    path('api/notifications/list/', list_notification, name='list_notification'),
    path('api/notifications/', notification_list_json, name='notification_list_json'),
    path('api/notifications/<int:pk>/details', notification_list_json_detail, name='notification_list_json_detail'),
    path('api/notifications/<int:notification_id>/', edit_notification, name='edit_notification'),
    path('api/notifications/<int:notification_id>/delete/', delete_notification, name='delete_notification'),
    # ...
]
