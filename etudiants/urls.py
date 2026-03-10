from django.urls import path, include
from .views import (admission,liste_etudiants,
                    etudiant_profile,
                    student_home,
                    student_maquette,
                    student_courses,
                    course_details,
                    student_times,
                    student_fees,
                    student_fees_payment,
                    BookListView,
                    student_documents,
                    student_certificat,
                    student_groupe,
                    student_password,
                    student_profile,
                    student_contact,
                    student_notes,

                    payment_success,
                    payment_error,
                    books_details,
                    carte_validated, 
                    student_transport, 
                    student_lignes,
                    student_abonnements, 
                    student_lignes_abonnement,
                    waveMakePaimentForCar,
                    waveerrorAbonnement, 
                    wavesuccessAbonnement,
                    cartes,
                    
                    
                    create_attestations_from_excel, 
                    attestation_print, 
                    attestation_list, 
                    attestation_details,
                    verify_attestation,
                    sessions_list, 
                    authenticite_print,
                    import_diplomes,
                    liste_sessions_diplomes,
                    diplomes_details, 

                    certificats_create,
                    certificats_details,
                    certificats_listes,
                    )

urlpatterns = [
    
    ### Attestation 
    path('create_attestations/', create_attestations_from_excel, name='create_attestations'),
    path('print_attestations/<int:pk>/', attestation_print, name='attestation_print'),
    path('authenticite_print/<int:pk>/', authenticite_print, name='authenticite_print'),
    path('list_attestations/', attestation_list, name='attestation_list'),
    path('sessions_list/', sessions_list, name='sessions_list'),
    path('details_attestations/<pk>/print/', attestation_details, name='attestation_details'),
    path('verify/attestations/identify-<slug:code>/', verify_attestation, name='verify'),

    path('import-diplomes/', import_diplomes, name='import_diplomes'),
    path('liste_sessions_diplomes/', liste_sessions_diplomes, name='liste_sessions_diplomes'),
    path('diplomes_details/<pk>/print/', diplomes_details, name='diplomes_details'),

    path('create-certificats/', certificats_create, name='certificats_create'),
    path('listes-certificats/',certificats_listes, name='certificats_listes'),
    path('details-certificats/<pk>/print/', certificats_details, name='certificats_details'),
    
    path('admission/',admission, name="admission"),
    path('liste_etudiants/',liste_etudiants, name="liste_etudiants"),
    path('etudiant_profile/<int:pk>/',etudiant_profile, name="etudiant_profile"),


    # Student Dashbord URL 
    path('home/',student_home, name="student_home"),
    path('student_maquette/',student_maquette, name="student_maquette"),
    path('student_times/',student_times, name="student_times"),
    path('student_card/',cartes, name="cartes"),
    path('student_courses/',student_courses, name="student_courses"),
    path('student_transports/',student_transport, name="student_transport"),
    path('student_lignes/',student_lignes, name="student_lignes"),
    path('student_lignes_abonnement/7j0i271l<int:pk>2j69i60j6/',student_lignes_abonnement, name="student_lignes_abonnement"),
    
    
    path('student_abonnements/',student_abonnements, name="student_abonnements"),
    path('student_courses/<int:pk>/<slug:code>',course_details, name="course_details"),
    path('student_fees/',student_fees, name="student_fees"),
    path('student_fees_payment/<int:pk>/<slug:code>',student_fees_payment, name="student_fees_payment"),
    path('student_book/', BookListView.as_view(), name="student_book"),
    path('student_book_details/7j0i271l<int:pk>2j69i60j69i61l2j69i65/', books_details, name="books_details"),
    path('student_documents/',student_documents, name="student_documents"),
    path('student_certificat_scolarite/<slug:name>/',student_certificat, name="student_certificat"),
    path('student_groupe/',student_groupe, name="student_groupe"),
    path('student_school_mark/',student_notes, name="student_notes"),
    path('student_password/',student_password, name="student_password"),
    path('student_profile/',student_profile, name="student_profile"),
    path('student_contact/',student_contact, name="student_contact"),

    path('billig/success/g/69i57j0i271l<int:pk>2j69i60j69i61l2j69i65/validated_bills',payment_success, name="payment_success"),
    path('billig/error/',payment_error, name="payment_error"),

    path('carte_validated/57j0i271l<int:pk>2j69i6/',carte_validated, name="carte_validated"),
    
    
    path('waveMakePaimentForcar/69i57j0i271l<int:pk>2j69i60j69i61l2j69i65/', waveMakePaimentForCar, name='waveMakePaimentForCar'),
    path('successForCar/69i57j0i271l<int:pk>2j69i60j69i61l2j69i65/', wavesuccessAbonnement, name='wavesuccessCar'),
    path('errorForCar/69i57j0i271l<int:pk>2j69i60j69i61l2j69i65/', waveerrorAbonnement, name='waveerrorCar'),


    
  

]