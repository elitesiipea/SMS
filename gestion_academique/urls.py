from django.urls import path, include
from .views import *
urlpatterns = [

    path("mon-etablissement/", mon_etablissement, name="mon_etablissement"),
    path('annees_academiques_list/',annees_academiques_list,name="annees_academiques_list"),
    path('create_pointage/',create_pointage,name="create_pointage"),
    path('create_classe_progression/',create_classe_progression,name="create_classe_progression"),
    path('reset_progress/<int:pk>/',reset_progress,name="reset_progress"),
    path('pointage_details/c/673f1d9e-b95c-800b-9d05-e6b8673fd340<int:pk>c/673f1d9e-b95c-800b-9d05-e6b8673fd340/',pointage_details,name="pointage_details"),
    path('statistiques/',statistiques,name="statistiques"),
    path('recap_inscriptions/',recap_inscriptions,name="effectifs"),
    path('global_progress/',global_progress,name="global_progress"),
    path('global_results/',global_results,name="global_results"),
    path('classe-progression/<int:pk>/printable/', ClasseProgressionPrintableView.as_view(), name='classe_progression_printable'),
    path('salles_list/',salles_list,name="salles_list"),
    path('filieres_list/',filieres_list,name="filieres_list"),
    path('niveaux_list/',niveaux_list,name="niveaux_list"),
    path('classes_list/',classes_list,name="classes_list"),
    path('progression_classes_list_/',progression_classes_list_,name="progression_classes_list_"),
    path('get-annees-academiques/',get_annees_academiques, name='get_annees_academiques'),
    path('classe-progression/<int:pk>/edit/', ClasseProgressionUpdateView.as_view(), name='classe_progression_update'),
    
    path('classe_details/<int:pk>/details/',classes_details,name="classes_details"),
    path('classes_progress_details/<int:pk>/classes_progress_details/',classes_progress_details,name="classes_progress_details"),
    
    
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
    path('cv/<int:pk>/cv', Cv.as_view(), name='cv'),

    path('DiplomeUpdateView/<int:pk>/', DiplomeUpdateView.as_view(), name='diplome_update'),
    path('SessionListViewCreation', SessionListViewCreation.as_view(),name="SessionListViewCreation"),

    
    path('sessions/<int:pk>/admission', Admission.as_view(), name='admission'),
    path('sessions/<int:pk>/diplomes', DiplomesPrint.as_view(), name='diplome'),
    path('students/<int:pk>/diplomes', DocumentStudent.as_view(), name='students'),
    
    path('scolarites/<str:statut>/', scolarites_par_statut, name='scolarites_par_statut'),
     path('maquette/<int:pk>/modifier_matiere/', MaquetteMatiereUpdateView.as_view(), name='maquette_matiere_update'),
     
    path('diplomes/', create_dossier, name='create_dossier'),
    path('diplomes/dossier/73f1d9e-b95c-800b-9d05-e6b8<int:pk>73f1d9e-b95c-800b-9d05-e6b8/', dossier_detail, name='dossier_detail'),
    path('list_dossiers/', list_dossiers, name='list_dossiers'),
    path('classe/toggle/<int:classe_id>/', toggle_classe_status, name='toggle_classe_status'),
]

urlpatterns += [
    path('upload/', upload_excel, name='upload_excel'),
    path('', student_list, name='student_list'),
    path('student/<int:student_id>/', student_detail, name='student_detail'),
    path('students/', StudentListView.as_view(), name='print_students_today'),
]