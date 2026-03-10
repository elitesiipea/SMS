from django.urls import path

from comptabilite.views import (
    paiement_historique_list_details,
    export_paiements_to_excel_view,
)

urlpatterns = [
    path(
        "comptabilite/paiements/",
        paiement_historique_list_details,
        name="paiement_historique_list_details",
    ),
    path(
        "comptabilite/export_paiements_to_excel",
        export_paiements_to_excel_view,
        name="export_paiements_to_excel",
    ),
]
