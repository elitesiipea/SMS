from django.urls import path, include
from .views import (create_note, evaluations_list,evaluation_details, note_resultat_add_edit, 
                   
                    Bulletins_Semestre1,
                    Bulletins_Semestre2,

                    ProcesVerbalSemestre1,
                    ProcesVerbalSemestre2,
                    ProcesVerbalAnnuel, 
                    Bulletins_Semestre3,
                    ResultatUpdateView


                        )

urlpatterns = [

    path('list_evaluations', evaluations_list, name="evaluations_list"),
    path('evaluations/<int:pk>/<int:classe_id>/details', evaluation_details, name="evaluation_details"),

    path('evaluations/?classe=<int:pk>/create', create_note, name="create_note"),
    path('evaluations/?classe=<int:pk>/add_resultats', note_resultat_add_edit, name="note_resultat_add_edit"),

    path('Bulletins_Semestre1/<int:pk>/details', Bulletins_Semestre1.as_view(), name="bulletins_semestre_1_cbv"),
    path('Bulletins_Semestre2/<int:pk>/details', Bulletins_Semestre2.as_view(), name="bulletins_semestre_2_cbv"),
    path('Bulletins_Semestre3/<int:pk>/details', Bulletins_Semestre3.as_view(), name="bulletins_semestre_3_cbv"),
    path('resultat/AGhutEsELQ/Y1mQgGmh6<int:pk>_u3XJ3fd8m0xA/edit/', ResultatUpdateView.as_view(), name='resultat_update'),
    

    path('ProcesVerbalSemestre1/<int:pk>/details', ProcesVerbalSemestre1.as_view(), name="pv_semestre_1_cbv"),
    path('ProcesVerbalSemestre2/<int:pk>/details', ProcesVerbalSemestre2.as_view(), name="pv_semestre_2_cbv"),
    path('ProcesVerbalAnnuel/<int:pk>/details', ProcesVerbalAnnuel.as_view(), name="pv_annuel_cbv"),
    
    
]