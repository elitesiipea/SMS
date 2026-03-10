from django.urls import path, include
from .views import (admission, 
                    liste_enseignants,
                    enseignant_profile,
                    create_contrat_enseignant,
                    get_matiere_classe,
                    contrat_enseignant_print,
                    contrat_enseignant_list,
                    home,
                    classe_list,
                    fiche_contrat_note,
                    demande_accompte,
                    demande_accompte_list,
                    validate_demande_update_cheque_number,
                    get_contrat_info,
                    reception_cheque,
                    contrat_enseignant_list_admin,
                    contrat_list_admin, 
                    creation_travaux_dirige, 
                    td_enseignant_print, 
                    teachers_password, 
                    rib_create_and_list, 
                    delete_rib, 
                    td_list
                     )

urlpatterns = [

    path('admission/',admission, name="admission_enseignant"),
    path('contrat_list_admin/',contrat_list_admin, name="contrat_list_admin"),
    path('liste_enseignant/',liste_enseignants, name="liste_enseignants"),
    path('ensignant_profile/<slug:code>/',enseignant_profile, name="enseignant_profile"),
    path('ensignant_profile/<slug:code>/contrat_enseignant_list_admin',contrat_enseignant_list_admin, name="contrat_enseignant_list_admin"),
    path('create_contrat_enseignant/<int:pk>/<slug:code>/',create_contrat_enseignant, name="create_contrat_enseignant"),
    path("get_matiere_classe/",get_matiere_classe, name="get_matiere_classe"),
    path('contrat_enseignant_print/<int:pk>/<slug:code>/',contrat_enseignant_print, name="contrat_enseignant_print"),
    path('contrat_/creation_travaux_dirige/<int:pk>/',creation_travaux_dirige, name="creation_travaux_dirige"),
    path('contrat_/td_enseignant_print/<int:pk>td_enseignant_print/',td_enseignant_print, name="td_enseignant_print"),

    ############## Page Përso Enseignant
    path('home/',home, name="teacher_home"),
    path('teachers_password/',teachers_password, name="teachers_password"),
    path('teachers_ribs/',rib_create_and_list, name="rib_create_and_list"),
    path('td_list/',td_list, name="td_list"),
    path('delete_rib/c/30a9858e-03bf-417b-8e47-1612bfa3a76e<int:rib_id>/c/30a9858e', delete_rib, name='delete_rib'),
    path('contrat/classes/list_classe',classe_list, name="classe_list"),
    path('contrat_/notesmarks/<int:pk>/',fiche_contrat_note, name="fiche_contrat_note"),
    path('demande_accompte/contrat/<int:pk>/<slug:code>/',demande_accompte, name="demande_accompte"),
    path('contrat_enseignant_list/<slug:code>/',contrat_enseignant_list, name="contrat_enseignant_list"),

    ############## Accompte
    path('demande_accompte_list/demande?=<slug:demande>/traiter?=<slug:traiter>/',demande_accompte_list,name="demande_accompte_list"),
    path('validate_demande_update_cheque_number/',validate_demande_update_cheque_number,name="validate_demande_update_cheque_number"),
    path('get_contrat_info/',get_contrat_info,name="get_contrat_info"),
    path('contrat_enseignant_reception_cheque/<int:pk>/<slug:code>/',reception_cheque, name="reception_cheque"),
   
   

    
]