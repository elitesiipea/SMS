from django.urls import path, include
from .views import (inscription_create,
                    student_inscription_list, 
                    student_inscription_details,
                    all_student_inscription_list,
                    scolarite_list,
                    reinscription,
                    remise_kits,
                    student_kits_list,
                    get_scolarite_info,
                    validate_remise_kits,
                    all_student_kits_list,
                    all_student_inscription_list_attentes,
                    nouveau_paiement,
                    student_scolarite_list,
                    paiement_historique_list,

                    #payment_processing_view
                    student_list_ministere,
                    payment_processing_view,
                    PaiementCreateDetails,
                    cancelPayment,
                    getStudentFee,
                    StudentFeeApiView,
                    waveMakePaiment,
                    wavesuccess,
                    waveerror,
                    webhook_handler, 
                    get_inscription_by_matricule,
                    make_new_paiment_form_ecobank, 
                    carte_print_details,
                    success_view1,
                    success_view2,
                    success_view3,
                    success_view4,
                    
                    all_student_inscription_list_dossiers,
                    scolarite_list_djabou,
                    inscription_data_detail,
                    emargement_list,
                    recu_djabou,
                    )

urlpatterns = [

    path("pre_inscription/<slug:slug>/add_fees/", inscription_create, name="inscription_create"),
    path("inscription/<slug:slug>/list_fees/", student_inscription_list, name="student_inscription_list"),
    path("inscription/<int:pk>/details_fees/", student_inscription_details, name="student_inscription_details"),
    path("inscription/<int:pk>/recu_djabou/", recu_djabou, name="recu_djabou"),
    path("inscription/all_student_inscription_list/", all_student_inscription_list, name="all_student_inscription_list"),
    path("inscription/all_student_inscription_list/student_list_ministere/", student_list_ministere, name="student_list_ministere"),
    
    path("inscription/all_student_inscription_list/cartes", carte_print_details, name="carte_print_details"),
    path("inscription/all_student_inscription_list/scolarite_list_djabou", scolarite_list_djabou, name="scolarite_list_djabou"),

    path("inscription/all_student_inscription_list/<int:pk>/<str:titre>/inscription_data_detail/", inscription_data_detail, name="inscription_data_detail"),
    path("inscription/emargement_list/", emargement_list, name="emargement_list"),
    
    
    
    


    
    path("all_student_inscription_list_dossiers/", all_student_inscription_list_dossiers, name="all_student_inscription_list_dossiers"),
     
    path("inscription/reinscription/", reinscription, name="reinscription"),
    path("inscription/all_student_inscription_list_attentes/", all_student_inscription_list_attentes, name="all_student_inscription_list_attentes"),
    path("inscription/remise_kits/", remise_kits, name="remise_kits"),
    path("inscription/scolarite_list/", scolarite_list, name="scolarite_list"),
    path("inscription/<slug:slug>/kits/list_fees/", student_kits_list, name="student_kits_list"),
    path("inscription/getscolarite/kits/data/", get_scolarite_info, name="get_scolarite_info"),
    path("inscription/validate_remise_kits/kits/data/", validate_remise_kits, name="validate_remise_kits"),
    path("inscription/validate_remise_kits/all_student_kits_list/data/", all_student_kits_list, name="all_student_kits_list"),
    path("inscription/nouveau_paiement/", nouveau_paiement, name="nouveau_paiement"),
    path("inscription/paiement_historique_list/", paiement_historique_list, name="paiement_historique_list"),
    path("inscription/<slug:slug>/student_scolarite_list/list_fees/", student_scolarite_list, name="student_scolarite_list"),
    path("inscription/payment_processing_view/add_fees/", payment_processing_view, name="payment_processing_view"),
    path("inscription/student_scolarite_list/list_fees/9i59j69i57j0i271l<int:pk>2j69i60j69i61l2j69i65.931j0j7&sourceid=myiipea&ie=UTF-8/biling/", PaiementCreateDetails, name="PaiementCreateDetails"),
    path("cancel/biling/69i57j0i271l<int:pk>2j69i60j69i61l2j69i65.931j0j/", cancelPayment, name="cancelPayment"),
    path("getfees/getStudentFee/<slug:code>/", getStudentFee, name="getStudentFee"),
    #Wave 
    path('api/get-student-fee/<str:code>/', StudentFeeApiView.as_view(), name='get-student-fee'),
    #Wave 
    path('api/wave/waveMakePaiment/<int:pk>/', waveMakePaiment, name='waveMakePaiment'),
    path('api/wave/success/<slug:code>/<int:pk>/', wavesuccess, name='wavesuccess'),
    path('api/wave/error/<slug:code>/<int:pk>/', waveerror, name='waveerror'),
    path('api/wave/webhook/payment/Paiement iipeaci * intouch/', success_view2, name='success_view2'),
    path('api/wave/webhook/payment/Paiement iipeaci * outtouch/', success_view3, name='success_view3'),
    path('api/wave/webhook/', webhook_handler, name='webhook_handler'),
    path('api/wave/webhook/payment/Paiement IIPEA/Verify/', success_view4, name='success_view4'),
    path('api/wave/webhook/payment/Paiement IIPEA/', success_view1, name='success_view1'),
    path('api/getFees/', get_inscription_by_matricule, name='get_inscription_by_matricule'),
    path('api/AddFees/', make_new_paiment_form_ecobank, name='make_new_paiment_form_ecobank'),


]