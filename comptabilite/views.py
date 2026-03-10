from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse

from decorators.decorators import staff_required
from gestion_academique.models import AnneeAcademique
from gestion_academique.views import _get_user_etablissement
from inscription.models import Paiement

import openpyxl


# ----------------------------------------------------------------------
# 1) Service : récupérer les paiements de l'établissement
# ----------------------------------------------------------------------
def get_paiements_for_etablissement(etablissement, annee_id=None):
    """
    Retourne le queryset des paiements confirmés de l'établissement,
    en attente de confirmation du service finance, éventuellement filtré
    par année académique.
    """
    paiements = Paiement.objects.filter(
        inscription__etudiant__etablissement_id=etablissement.id,
        confirmed=True,
        confirmation_finance=False,
    )

    if annee_id:
        paiements = paiements.filter(
            inscription__annee_academique_id=annee_id
        )
    else:
        # Dernière année académique de l'établissement
        last_annee_academique = etablissement.annee_academiques.order_by(
            "-created"
        ).first()
        if last_annee_academique:
            paiements = paiements.filter(
                inscription__annee_academique_id=last_annee_academique.id
            )

    return paiements


# ----------------------------------------------------------------------
# 2) Service : export Excel
# ----------------------------------------------------------------------
def export_paiements_to_excel(etablissement, annee_id=None):
    """
    Exporte en Excel les paiements d'un établissement (et éventuellement
    d'une année académique donnée) sous forme de fichier .xlsx.
    """
    paiements = get_paiements_for_etablissement(etablissement, annee_id)

    # Création du classeur Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historique des Paiements"

    # En-têtes
    headers = [
        "Reference_Id",
        "Étudiant",
        "Filière",
        "Niveau",
        "Montant",
        "Source",
        "Référence Système",
        "Date de Paiement",
        "Année Académique",
        "Confirmé par Finance",
    ]
    ws.append(headers)

    # Lignes de données
    for paiement in paiements:
        inscription = paiement.inscription
        etu = inscription.etudiant
        user_etu = etu.utilisateur

        ws.append(
            [
                paiement.id,
                f"{user_etu.nom} {user_etu.prenom}",
                inscription.filiere.nom if inscription.filiere else "",
                inscription.niveau.nom if inscription.niveau else "",
                float(paiement.montant) if paiement.montant is not None else 0,
                paiement.source or "",
                paiement.reference or "",
                paiement.created.strftime("%d/%m/%Y")
                if paiement.created
                else "",
                (
                    f"{inscription.annee_academique.debut}-"
                    f"{inscription.annee_academique.fin}"
                    if inscription.annee_academique
                    else ""
                ),
                "Oui" if paiement.confirmation_finance else "Non",
            ]
        )

    # Nom de fichier un peu plus explicite
    filename = "historique_paiements"
    if annee_id:
        try:
            annee = AnneeAcademique.objects.get(
                id=annee_id, etablissement=etablissement
            )
            filename = f"historique_paiements_{annee.debut}_{annee.fin}"
        except AnneeAcademique.DoesNotExist:
            pass

    filename = f"{filename}.xlsx"

    # Réponse HTTP
    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


# ----------------------------------------------------------------------
# 3) Vue : liste + confirmation des paiements
# ----------------------------------------------------------------------
@login_required
@staff_required
def paiement_historique_list_details(request):
    """
    Liste paginée des paiements de l'établissement,
    filtrables par année académique, avec possibilité
    de confirmer un paiement (confirmation_finance=True).
    """
    # 1) Établissement de l'utilisateur
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            (
                "Votre compte n'est rattaché à aucun établissement. "
                "Merci de contacter l’administrateur pour corriger "
                "cette situation."
            ),
        )
        context = {
            "page_obj": None,
            "titre": "Historique des paiements",
            "info": "Historique des paiements",
            "info2": "Historique des paiements",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "paiements": [],
            "no_etablissement": True,
        }
        return render(
            request,
            "comptabilite/paiements/historique.html",
            context=context,
        )

    # 2) Gestion de l'année académique
    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = (
        AnneeAcademique.objects.filter(etablissement_id=etablissement.id)
        .order_by("-created")
    )

    annee_active = None
    if selected_annee_id:
        annee_active = annees_academiques.filter(
            id=selected_annee_id
        ).first()

    if annee_active is None:
        annee_active = annees_academiques.first()

    annee_id_for_service = annee_active.id if annee_active else None

    # 3) Récupération des paiements
    paiements_qs = get_paiements_for_etablissement(
        etablissement, annee_id_for_service
    )

    # 4) Confirmation d'un paiement
    if request.method == "POST" and "validate_payment" in request.POST:
        paiement_id = request.POST.get("paiement_id")

        try:
            paiement = Paiement.objects.get(
                id=paiement_id,
                inscription__etudiant__etablissement_id=etablissement.id,
            )
            paiement.confirmation_finance = True
            paiement.save()
            messages.success(
                request, "Le paiement a été confirmé avec succès !"
            )
        except Paiement.DoesNotExist:
            messages.error(request, "Paiement introuvable !")

        # Redirection sur la même page + même année
        url = reverse("paiement_historique_list_details")
        if annee_active:
            url = f"{url}?annee_id={annee_active.id}"
        return redirect(url)

    # 5) Pagination
    paginator = Paginator(paiements_qs, 20)  # 20 paiements / page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 6) Contexte
    context = {
        "page_obj": page_obj,
        "titre": f"Historique des paiements {etablissement}",
        "info": "Historique des paiements",
        "info2": "Historique des paiements",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "annee_active": annee_active,
        "paiements": paiements_qs,
        "no_etablissement": False,
    }

    return render(
        request, "comptabilite/paiements/historique.html", context=context
    )


# ----------------------------------------------------------------------
# 4) Vue : export Excel (branchée dans urls.py)
# ----------------------------------------------------------------------
@login_required
@staff_required
def export_paiements_to_excel_view(request):
    """
    Vue publique (URL) qui prépare le contexte (établissement + année)
    puis délègue l'export effectif à export_paiements_to_excel().
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            (
                "Votre compte n'est rattaché à aucun établissement. "
                "Merci de contacter l’administrateur pour corriger "
                "cette situation."
            ),
        )
        return redirect("paiement_historique_list_details")

    # Récupération de l'année académique depuis l'URL (?annee_id=...)
    annee_id_param = request.GET.get("annee_id")

    annee_active = None
    if annee_id_param:
        annee_active = AnneeAcademique.objects.filter(
            id=annee_id_param,
            etablissement_id=etablissement.id,
        ).first()

    if annee_active is None:
        annee_active = (
            AnneeAcademique.objects.filter(etablissement_id=etablissement.id)
            .order_by("-created")
            .first()
        )

    annee_id_final = annee_active.id if annee_active else None

    # Délégation à la fonction utilitaire
    return export_paiements_to_excel(etablissement, annee_id_final)
