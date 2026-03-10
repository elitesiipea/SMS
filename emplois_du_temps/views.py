from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from gestion_academique.views import _get_user_etablissement
from .models import EmploisDutemps, Programme
from .forms import ProgrammeForm
from gestion_academique.models import AnneeAcademique
from enseignant.models import ContratEnseignant
from decorators.decorators import staff_required



def _get_annees_for_etablissement(etablissement):
    """
    Retourne le queryset des années académiques d'un établissement,
    triées de la plus récente à la plus ancienne.
    """
    return AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")


def _get_selected_or_last_annee(etablissement, selected_annee_id):
    """
    À partir d'un établissement et d'un éventuel annee_id passé en GET,
    retourne (annee_selectionnee, queryset_des_annees).

    - Si selected_annee_id correspond à une année de cet établissement → on la prend.
    - Sinon → on prend la dernière année de l'établissement.
    - Si aucune année n'existe → annee_selectionnee = None.
    """
    annees_qs = _get_annees_for_etablissement(etablissement)

    selected_annee = None
    if selected_annee_id:
        selected_annee = annees_qs.filter(id=selected_annee_id).first()

    if selected_annee is None:
        selected_annee = annees_qs.first()

    return selected_annee, annees_qs


# -------------------------------------------------------------------
# Emplois du temps : Liste
# -------------------------------------------------------------------
@login_required
@staff_required
def emploi_du_temps_list(request):
    """
    Affiche la liste des emplois du temps pour l'établissement de l'utilisateur.
    Permet de filtrer par année académique.
    """
    etablissement = _get_user_etablissement(request)

    # Aucun établissement lié → message + page "vide"
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Emplois du temps",
            "info": "Liste",
            "info2": "Emplois du temps",
            "emplois_du_temps": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "emplois_du_temps/list.html", context=context)

    selected_annee_id = request.GET.get("annee_id")

    # Récupération année sélectionnée ou dernière année dispo
    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    # Base queryset : tous les emplois du temps de l'établissement
    emplois_du_temps = EmploisDutemps.objects.filter(
        classe__annee_academique__etablissement_id=etablissement.id
    )

    # Si on a une année dispo, on filtre dessus
    if annee_selectionnee is not None:
        emplois_du_temps = emplois_du_temps.filter(
            classe__annee_academique_id=annee_selectionnee.id
        )
    else:
        # Aucun emploi du temps possible sans année
        emplois_du_temps = emplois_du_temps.none()
        messages.info(
            request,
            "Aucune année académique n'est encore définie pour votre établissement.",
        )

    context = {
        "titre": "Emplois du temps",
        "info": "Liste",
        "info2": "Emplois du temps",
        "emplois_du_temps": emplois_du_temps,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
        "no_etablissement": False,
    }
    return render(request, "emplois_du_temps/list.html", context=context)


# -------------------------------------------------------------------
# Emplois du temps : Détails + ajout de programme
# -------------------------------------------------------------------
@login_required
@staff_required
def emploisdutemps_detail(request, emploisdutemps_id, edit):
    """
    Affiche les détails d'un emploi du temps spécifique et permet d'ajouter un programme.
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Emplois du temps",
            "info": "Détails",
            "info2": "Emplois du temps",
            "emploisdutemps": None,
            "programmes": [],
            "form": None,
            "datatable": False,
            "edit": 0,
            "time_add": False,
            "jours_semaine": ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE'],
            "no_etablissement": True,
        }
        return render(
            request, "emplois_du_temps/update_emplois_programme.html", context
        )

    # On s'assure que l'emploi du temps appartient bien à l'établissement de l'utilisateur
    emploisdutemps = get_object_or_404(
        EmploisDutemps,
        pk=emploisdutemps_id,
        classe__annee_academique__etablissement_id=etablissement.id,
    )

    programmes = emploisdutemps.emplois_du_temps_matiere.all()

    # Form initial
    form = ProgrammeForm(etablissement.id, emploisdutemps.classe.id)

    if request.method == "POST":
        form = ProgrammeForm(etablissement.id, emploisdutemps.classe.id, request.POST)
        if form.is_valid():
            programme = form.save(commit=False)

            # Vérifie si un programme identique existe déjà
            existing_programme = Programme.objects.filter(
                Q(emplois_du_temps=emploisdutemps)
                & Q(salle=programme.salle)
                & Q(date=programme.date)
                & Q(debut__lt=programme.fin, fin__gt=programme.debut)
            )

            if existing_programme.exists():
                messages.error(request, "Un programme similaire existe déjà.")
            else:
                # Vérifie si chevauchement
                overlapping_programmes = Programme.objects.filter(
                    Q(emplois_du_temps=emploisdutemps)
                    & Q(date=programme.date)
                    & Q(debut__lt=programme.fin, fin__gt=programme.debut)
                )
                if overlapping_programmes.exists():
                    messages.error(
                        request,
                        "Le programme chevauche un autre programme existant.",
                    )
                else:
                    programme.emplois_du_temps = emploisdutemps
                    programme.save()
                    messages.success(request, "Programme ajouté !")
                    return redirect(
                        reverse(
                            "emploisdutemps_detail",
                            kwargs={
                                "emploisdutemps_id": emploisdutemps_id,
                                "edit": 1,
                            },
                        )
                    )

    context = {
        "titre": f"EMPLOIS DU TEMPS {emploisdutemps}",
        "info": "Détails",
        "info2": "Emplois du temps",
        "datatable": True,
        "emploisdutemps": emploisdutemps,
        "programmes": programmes.order_by("date"),
        "form": form,
        "edit": float(edit),
        "time_add": True,
        "jours_semaine": [
            "LUNDI",
            "MARDI",
            "MERCREDI",
            "JEUDI",
            "VENDREDI",
            "SAMEDI",
            "DIMANCHE",
        ],
        "no_etablissement": False,
    }
    return render(
        request, "emplois_du_temps/update_emplois_programme.html", context
    )


# -------------------------------------------------------------------
# Suppression d'un programme
# -------------------------------------------------------------------
@login_required
@staff_required
def delete_programme(request, programme_id):
    """
    Supprime un programme spécifique de l'emploi du temps.
    On vérifie aussi que le programme appartient bien à un emploi du temps
    de l'établissement de l'utilisateur.
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        return redirect("emploi_du_temps_list")

    programme = get_object_or_404(
        Programme,
        pk=programme_id,
        emplois_du_temps__classe__annee_academique__etablissement_id=etablissement.id,
    )
    emploisdutemps_id = programme.emplois_du_temps.id
    programme.delete()
    messages.success(request, "Programme supprimé !")
    return redirect(
        reverse(
            "emploisdutemps_detail",
            kwargs={"emploisdutemps_id": emploisdutemps_id, "edit": 1},
        )
    )


# -------------------------------------------------------------------
# Emargements
# -------------------------------------------------------------------
@login_required
@staff_required
def emargements(request):
    """
    Gère les emargements des enseignants pour l'établissement de l'utilisateur.
    Permet de sélectionner une année académique et de valider un emargement.
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Emargements",
            "info": "Emargements",
            "info2": "Emargements",
            "programmes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "contrat_validated": False,
            "no_etablissement": True,
        }
        return render(request, "emplois_du_temps/emargements.html", context=context)

    selected_annee_id = request.GET.get("annee_id")

    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    programmes = Programme.objects.filter(
        emplois_du_temps__classe__annee_academique__etablissement_id=etablissement.id
    )

    if annee_selectionnee is not None:
        programmes = programmes.filter(
            emplois_du_temps__classe__annee_academique_id=annee_selectionnee.id
        )
    else:
        programmes = programmes.none()
        messages.info(
            request,
            "Aucune année académique n'est encore définie pour votre établissement.",
        )

    if request.method == "POST":
        contrat_id = request.POST.get("contrat_id")
        duree = request.POST.get("duree")

        try:
            contrat = ContratEnseignant.objects.get(
                id=contrat_id,
                enseignant__etablissement_id=etablissement.id,  # sécurité
            )
            duree_float = float(duree or 0)
            progression = contrat.progression + duree_float

            if progression <= contrat.volume_horaire:
                contrat.progression = progression
                contrat.closed = contrat.progression == contrat.volume_horaire
                contrat.save()
                messages.success(
                    request, "L'emargement a été enregistré avec succès."
                )
            else:
                messages.error(
                    request,
                    "La durée d'emargement dépasse le volume horaire du contrat.",
                )
        except ContratEnseignant.DoesNotExist:
            messages.error(
                request,
                "Le contrat d'enseignant spécifié n'existe pas pour cet établissement.",
            )
        except ValueError:
            messages.error(
                request,
                "La durée saisie est invalide. Veuillez saisir un nombre.",
            )

    context = {
        "titre": "Emargements",
        "info": "Emargements",
        "info2": "Emargements",
        "programmes": programmes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
        "contrat_validated": True,
        "no_etablissement": False,
    }
    return render(request, "emplois_du_temps/emargements.html", context=context)
