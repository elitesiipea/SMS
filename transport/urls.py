from django.urls import path
from .views import CarListView  , TrajetListView , AbonnementListDetail, AbonnementListAll

urlpatterns = [
    path('cars/', CarListView, name='car_list'),
    path('trajets/', TrajetListView, name='trajet_list'),
    path('abonnements/9i57j0i271l<int:pk>2j69i60j69i61l2j69/', AbonnementListDetail, name='AbonnementListDetail'),
    path('abonnements/AbonnementListAll/', AbonnementListAll, name='AbonnementListAll'),
    # path('abonnements/create/', AbonnementCreateView.as_view(), name='abonnement_create'),
    # path('abonnements/<int:pk>/update/', AbonnementUpdateView.as_view(), name='abonnement_update'),
    # path('abonnements/<int:pk>/delete/', AbonnementDeleteView.as_view(), name='abonnement_delete'),
]
