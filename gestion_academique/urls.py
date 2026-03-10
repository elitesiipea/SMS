from django.urls import path, include
from .views import (annees_academiques_list,
                    salles_list,
                   filieres_list, 
                   niveaux_list, 
                   classes_list, 
                   maquettes_list,
                   maquette_details,
                   classes_details,
                   statistiques, 
                   migrate_students, 
                   move_uto_other_class_students, 
                   classes_appel, 
                   classes_televerser_notes,
                   classes_recu,
                   classes_certificats,
                   classes_details_results,
                   global_results, 
                   SessionListView,
                   SessionDetailView,
                   Authenticite,
                   Reussite,
                   Admission,
                   DiplomesPrint,
                   DocumentStudent,
                   scolarites_par_statut,
                   recap_inscriptions,
                   MaquetteMatiereUpdateView
                   )

urlpatterns = [

    path('annees_academiques_list/',annees_academiques_list,name="annees_academiques_list"),
    
    
    path('statistiques/',statistiques,name="statistiques"),
    path('recap_inscriptions/',recap_inscriptions,name="effectifs"),
    
    
    path('global_results/',global_results,name="global_results"),
    
    path('salles_list/',salles_list,name="salles_list"),
    path('filieres_list/',filieres_list,name="filieres_list"),
    path('niveaux_list/',niveaux_list,name="niveaux_list"),
    path('classes_list/',classes_list,name="classes_list"),
    path('classe_details/<int:pk>/details/',classes_details,name="classes_details"),
    path('classes_details_results/<int:pk>/classes_details_results/',classes_details_results,name="classes_details_results"),
    path('classes_appel/<int:pk>/classes_appel/',classes_appel,name="appel"),
    path('classes_televerser_notes/<int:pk>/classes_televerser_notes/',classes_televerser_notes,name="classes_televerser_notes"),
    path('classes_recu/<int:pk>/recu/',classes_recu,name="classes_recu"),
    path('classes_certificats/<int:pk>/classes_certificats/',classes_certificats,name="classes_certificats"),
    path('maquettes_list/',maquettes_list,name="maquettes_list"),
    path('maquette_details/<int:pk>/maquette/',maquette_details,name="maquette_details"),
    
    path('migrate-students/', migrate_students, name='migrate_students'),
    path('migrate-move_uto_other_class_students/', move_uto_other_class_students, name='move_uto_other_class_students'),
    
    
    path('sessions/', SessionListView.as_view(), name='session_list'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/authenticite', Authenticite.as_view(), name='authenticite'),
    path('sessions/<int:pk>/reussite', Reussite.as_view(), name='reussite'),
    path('sessions/<int:pk>/admission', Admission.as_view(), name='admission'),
    path('sessions/<int:pk>/diplomes', DiplomesPrint.as_view(), name='diplome'),
    path('students/<int:pk>/diplomes', DocumentStudent.as_view(), name='students'),
    
    path('scolarites/<str:statut>/', scolarites_par_statut, name='scolarites_par_statut'),
     path('maquette/<int:pk>/modifier_matiere/', MaquetteMatiereUpdateView.as_view(), name='maquette_matiere_update'),
    

   
    
]