from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash

from gestion_academique.views import _get_user_etablissement
from gestion_academique.models import Matiere, Classe, AnneeAcademique
from emplois_du_temps.models import Programme

from .forms import (
    EnseignantForm,
    ContratEnseignantForm,
    PasswordChangeCustomForm,
    RibForm,
)
from .models import Enseignant, ContratEnseignant, TravauxDirige, Rib

from decorators.decorators import staff_required, teacher_required
from authentication.models import User


# -------------------------------------------------------------------
# Helpers communs
# -------------------------------------------------------------------
def _get_annees_for_etablissement(etablissement):
    """
    Retourne les années académiques de l'établissement (de la plus récente à la plus ancienne).
    """
    return AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")


def _get_selected_or_last_annee(etablissement, selected_annee_id):
    """
    Retourne (annee_selectionnee, queryset_des_annees) pour un établissement.

    - Si selected_annee_id correspond à une année de cet établissement → on la prend.
    - Sinon → on prend la dernière année (la plus récente).
    - S'il n'y a aucune année → annee_selectionnee = None.
    """
    annees_qs = _get_annees_for_etablissement(etablissement)

    selected_annee = None
    if selected_annee_id:
        selected_annee = annees_qs.filter(id=selected_annee_id).first()

    if selected_annee is None:
        selected_annee = annees_qs.first()

    return selected_annee, annees_qs


def is_staff_or_teacher(user):
    return user.is_staff or user.is_teacher


# -------------------------------------------------------------------
# Admission / création enseignant
# -------------------------------------------------------------------
@login_required
@staff_required
def admission(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "ENREGISTREMENT ENSEIGNANT",
            "info": "ENREGISTREMENT",
            "info2": "ENREGISTREMENT ENSEIGNANT",
            "datatable": False,
            "form": None,
            "no_etablissement": True,
        }
        return render(
            request, "enseignant/admission/admission.html", context=context
        )

    if request.method == "POST":
        form = EnseignantForm(request.POST, request.FILES)
        if form.is_valid():
            nom = form.cleaned_data["nom"]
            prenom = form.cleaned_data["prenom"]
            email = form.cleaned_data["email"]

            # Mot de passe déjà hashé (comme dans ton code original)
            password = (
                "pbkdf2_sha256$260000$H157G58nYUDjbBTAZTSPbI$JGpbJlZ5pV9nB2lZGAc6jguEWKHJzagBEyG7D2rKZas="
            )

            user = User.objects.create(
                email=email,
                password=password,
                nom=nom,
                prenom=prenom,
                is_teacher=True,
                etablissement_id=etablissement.id,
            )

            enseignant = form.save(commit=False)
            enseignant.utilisateur = user
            enseignant.etablissement_id = etablissement.id
            enseignant.save()

            messages.success(
                request, "Dossier de l'enseignant créé avec succès !"
            )
            return redirect(
                reverse(
                    "enseignant_profile", kwargs={"code": enseignant.code}
                )
            )
    else:
        form = EnseignantForm()

    context = {
        "titre": "ENREGISTREMENT ENSEIGNANT",
        "info": "ENREGISTREMENT",
        "info2": "ENREGISTREMENT ENSEIGNANT",
        "datatable": False,
        "form": form,
        "no_etablissement": False,
    }
    return render(request, "enseignant/admission/admission.html", context=context)


# -------------------------------------------------------------------
# Liste enseignants
# -------------------------------------------------------------------
@login_required
@staff_required
def liste_enseignants(request):
    etablissement = _get_user_etablissement(request)

    # Aucun établissement rattaché au compte
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Liste des enseignants",
            "info": "Liste",
            "info2": "Liste des enseignants",
            "enseignants": [],
            "datatable": False,
            "no_etablissement": True,
        }
        return render(request, "enseignant/listes/list.html", context=context)

    enseignants = Enseignant.objects.filter(etablissement_id=etablissement.id)

    context = {
        "titre": f"Liste des enseignants - {etablissement.nom}",
        "info": "Liste",
        "info2": "Liste des enseignants",
        "enseignants": enseignants,
        "datatable": True,
        "no_etablissement": False,
    }
    return render(request, "enseignant/listes/list.html", context=context)


# -------------------------------------------------------------------
# Profil enseignant
# -------------------------------------------------------------------
@login_required
@staff_required
def enseignant_profile(request, code):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        return redirect("liste_enseignants")

    enseignant = get_object_or_404(
        Enseignant, code=code, etablissement_id=etablissement.id
    )

    if request.method == "POST":
        # Récupère la dernière année académique de l'établissement
        annee_selectionnee, _ = _get_selected_or_last_annee(
            etablissement, selected_annee_id=None
        )
        if annee_selectionnee is None:
            messages.error(
                request,
                "Aucune année académique n'est définie pour l'établissement. "
                "Impossible de créer un contrat.",
            )
            return redirect("enseignant_profile", code=code)

        contrat = ContratEnseignant.objects.create(
            enseignant=enseignant,
            annee_academique=annee_selectionnee,
        )
        messages.success(
            request, f"Renseignez les paramètres du contrat {contrat.id}"
        )
        return redirect(
            reverse(
                "create_contrat_enseignant",
                kwargs={"code": code, "pk": contrat.pk},
            )
        )

    context = {
        "titre": enseignant,
        "info": "Profile Enseignant",
        "info2": enseignant,
        "enseignant": enseignant,
        "can_add_contrat": True,
    }
    return render(request, "enseignant/profiles/index.html", context=context)


# -------------------------------------------------------------------
# AJAX : récupérer matières / classes
# -------------------------------------------------------------------
@login_required
@staff_required
def get_matiere_classe(request):
    if request.method == "GET":
        annee_academique = request.GET.get("annee_academique")
        filiere = request.GET.get("filiere")
        niveau = request.GET.get("niveau")

        matieres = Matiere.objects.filter(
            maquette__filiere=filiere,
            maquette__niveau=niveau,
            maquette__annee_academique=annee_academique,
        )
        classes = Classe.objects.filter(
            filiere=filiere,
            niveau=niveau,
            annee_academique=annee_academique,
        )

        matiere_list = [
            {"id": matiere.id, "nom_matiere": matiere.nom}
            for matiere in matieres
        ]
        classe_list = [
            {"id": classe.id, "nom_classe": classe.nom}
            for classe in classes
        ]

        data = {"matiere": matiere_list, "classe": classe_list}
        return JsonResponse(data)

    return JsonResponse({"error": "Invalid request method"}, status=400)


# -------------------------------------------------------------------
# Création / édition contrat enseignant
# -------------------------------------------------------------------
@login_required
@staff_required
def create_contrat_enseignant(request, code, pk):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        return redirect("liste_enseignants")

    contrat = get_object_or_404(
        ContratEnseignant,
        pk=pk,
        enseignant__code=code,
        annee_academique__etablissement_id=etablissement.id,
    )

    if request.method == "POST":
        form = ContratEnseignantForm(
            etablissement.id, request.POST, request.FILES, instance=contrat
        )
        if form.is_valid():
            existing_contrat = ContratEnseignant.objects.filter(
                annee_academique=form.cleaned_data["annee_academique"],
                filiere=form.cleaned_data["filiere"],
                niveau=form.cleaned_data["niveau"],
                classe=form.cleaned_data["classe"],
                matiere=form.cleaned_data["matiere"],
            ).first()

            if existing_contrat and existing_contrat.pk != contrat.pk:
                messages.error(
                    request,
                    "Un contrat avec les mêmes caractéristiques existe déjà.",
                )
            else:
                contrat = form.save()
                return redirect(
                    reverse(
                        "contrat_enseignant_print",
                        kwargs={"code": code, "pk": contrat.pk},
                    )
                )
    else:
        form = ContratEnseignantForm(etablissement.id, instance=contrat)

    context = {
        "titre": contrat.enseignant,
        "info": "Nouveau Contrat",
        "info2": contrat.enseignant,
        "enseignant": contrat.enseignant,
        "search_matiere_classe": True,
        "form": form,
    }
    return render(request, "enseignant/contrats/create.html", context=context)


@login_required
@staff_required
def contrat_enseignant_print(request, code, pk):
    etablissement = _get_user_etablissement(request)

    contrat = get_object_or_404(
        ContratEnseignant,
        pk=pk,
        enseignant__code=code,
        annee_academique__etablissement_id=getattr(etablissement, "id", None),
    )

    context = {
        "titre": contrat.enseignant,
        "info": "Nouveau Contrat",
        "info2": contrat.enseignant,
        "enseignant": contrat.enseignant,
        "contrat": contrat,
    }
    return render(request, "enseignant/contrats/print.html", context=context)


# -------------------------------------------------------------------
# Listes de contrats (admin / enseignant)
# -------------------------------------------------------------------
@user_passes_test(is_staff_or_teacher)
def contrat_enseignant_list_admin(request, code):
    etablissement = _get_user_etablissement(request)
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Liste Contrats",
            "info": "Liste Contrats",
            "info2": "Liste Contrats",
            "enseignant": "Liste Contrats",
            "contrats": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "enseignant/contrats/listes_contrat.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    contrats = ContratEnseignant.objects.filter(
        annee_academique__etablissement_id=etablissement.id,
        enseignant__code=code,
    )

    if annee_selectionnee is not None:
        contrats = contrats.filter(annee_academique_id=annee_selectionnee.id)
    else:
        contrats = contrats.none()
        messages.info(
            request,
            "Aucune année académique n'est définie pour votre établissement.",
        )

    context = {
        "titre": "Liste Contrats",
        "info": "Liste Contrats",
        "info2": "Liste Contrats",
        "enseignant": "Liste Contrats",
        "contrats": contrats,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
        "no_etablissement": False,
    }
    return render(
        request, "enseignant/contrats/listes_contrat.html", context=context
    )


@user_passes_test(is_staff_or_teacher)
def contrat_enseignant_list(request, code):
    etablissement = _get_user_etablissement(request)
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Liste Contrats",
            "info": "Liste Contrats",
            "info2": "Liste Contrats",
            "enseignant": "Liste Contrats",
            "contrats": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request,
            "enseignant/contrats/listes_all_contrat.html",
            context=context,
        )

    selected_annee_id = request.GET.get("annee_id")

    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    contrats = ContratEnseignant.objects.filter(
        annee_academique__etablissement_id=etablissement.id,
        enseignant__code=code,
    )

    if annee_selectionnee is not None:
        contrats = contrats.filter(annee_academique_id=annee_selectionnee.id)
    else:
        contrats = contrats.none()
        messages.info(
            request,
            "Aucune année académique n'est définie pour votre établissement.",
        )

    context = {
        "titre": "Liste Contrats",
        "info": "Liste Contrats",
        "info2": "Liste Contrats",
        "enseignant": "Liste Contrats",
        "contrats": contrats,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
        "no_etablissement": False,
    }
    return render(
        request,
        "enseignant/contrats/listes_all_contrat.html",
        context=context,
    )


# -------------------------------------------------------------------
# Tableau de bord enseignant
# -------------------------------------------------------------------
@login_required
@teacher_required
def home(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur.",
        )
        context = {
            "titre": "Tableau de Bord",
            "info": "Enseignant",
            "info2": "Tableau de Bord",
            "programmes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "enseignant/dashboard/index.html", context=context
        )

    es = get_object_or_404(Enseignant, utilisateur=request.user)

    selected_annee_id = request.GET.get("annee_id")

    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    programmes = Programme.objects.filter(
        emplois_du_temps__classe__annee_academique__etablissement_id=etablissement.id,
        matiere__enseignant=es,
    )

    if annee_selectionnee is not None:
        programmes = programmes.filter(
            emplois_du_temps__classe__annee_academique_id=annee_selectionnee.id
        )
    else:
        programmes = programmes.none()
        messages.info(
            request,
            "Aucune année académique n'est définie pour votre établissement.",
        )

    context = {
        "titre": "Tableau de Bord",
        "info": "Enseignant",
        "info2": "Tableau de Bord",
        "programmes": programmes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
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
    return render(request, "enseignant/dashboard/index.html", context=context)


# -------------------------------------------------------------------
# Mot de passe enseignant
# -------------------------------------------------------------------
@login_required
@teacher_required
def teachers_password(request):
    if request.method == "POST":
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # pour ne pas déconnecter l'utilisateur
            update_session_auth_hash(request, user)
            messages.success(request, "Mot de passe modifié !")
            return redirect("teacher_home")
    else:
        form = PasswordChangeCustomForm(request.user)

    context = {
        "titre": "Modifier mes Accès",
        "form": form,
    }
    return render(
        request, "enseignant/dashboard/password.html", context=context
    )


# -------------------------------------------------------------------
# Liste des classes (côté enseignant)
# -------------------------------------------------------------------
@login_required
@teacher_required
def classe_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement.",
        )
        context = {
            "titre": "Liste des classes",
            "info": "Enseignant",
            "info2": "Liste des classes",
            "programmes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "enseignant/dashboard/list_classe.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    contrats = ContratEnseignant.objects.filter(
        annee_academique__etablissement_id=etablissement.id,
        enseignant=request.user.enseignant,
    )

    if annee_selectionnee is not None:
        contrats = contrats.filter(annee_academique_id=annee_selectionnee.id)
    else:
        contrats = contrats.none()
        messages.info(
            request,
            "Aucune année académique n'est définie pour votre établissement.",
        )

    context = {
        "titre": "Liste des classes",
        "info": "Enseignant",
        "info2": "Liste des classes",
        "programmes": contrats,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
        "no_etablissement": False,
    }
    return render(
        request, "enseignant/dashboard/list_classe.html", context=context
    )


# -------------------------------------------------------------------
# Fiche de notes
# -------------------------------------------------------------------
@login_required
@teacher_required
def fiche_contrat_note(request, pk):
    contrat = get_object_or_404(
        ContratEnseignant,
        pk=pk,
        enseignant__utilisateur=request.user,
    )
    context = {
        "titre": f"FICHE DE NOTE {contrat} - {contrat.classe}",
        "info": "Fiche de Notes",
        "info2": f"{contrat}",
        "datatable": True,
        "etudiants": contrat.classe.effectifs,
    }
    return render(
        request, "enseignant/dashboard/fiche_note.html", context=context
    )


# -------------------------------------------------------------------
# Demande d'acompte (côté enseignant)
# -------------------------------------------------------------------
@login_required
@teacher_required
def demande_accompte(request, code, pk):
    contrat = get_object_or_404(
        ContratEnseignant,
        pk=pk,
        enseignant__code=code,
        enseignant__utilisateur=request.user,
    )
    contrat.demande_accompte = True
    contrat.save()
    messages.success(request, "Demande d'acompte enregistrée avec succès.")
    return redirect("classe_list")


# -------------------------------------------------------------------
# Liste des demandes d'acompte (staff)
# -------------------------------------------------------------------
@login_required
@staff_required
def demande_accompte_list(request, demande, traiter):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement.",
        )
        context = {
            "titre": "Demandes d'acomptes",
            "info": "Listes",
            "info2": "Demandes d'acomptes",
            "accomptes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "enseignant/contrats/accomptes/list.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    accomptes = ContratEnseignant.objects.filter(
        enseignant__etablissement_id=etablissement.id,
        demande_accompte=demande,
        demande_traitee=traiter,
    )

    if annee_selectionnee is not None:
        accomptes = accomptes.filter(annee_academique_id=annee_selectionnee.id)
    else:
        accomptes = accomptes.none()
        messages.info(
            request,
            "Aucune année académique n'est définie pour votre établissement.",
        )

    context = {
        "titre": "Demandes d'acomptes",
        "info": "Listes",
        "info2": "Demandes d'acomptes",
        "accomptes": accomptes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
        "contrat_validated": True,
        "no_etablissement": False,
    }
    return render(
        request, "enseignant/contrats/accomptes/list.html", context=context
    )


# -------------------------------------------------------------------
# Validation acompte + numéro de chèque
# -------------------------------------------------------------------
@login_required
@staff_required
@require_POST
def validate_demande_update_cheque_number(request):
    etablissement = _get_user_etablissement(request)

    contrat_pk = request.POST.get("contrat_id")
    cheque_number = request.POST.get("chequeNumber")

    if contrat_pk and cheque_number:
        contrat = get_object_or_404(
            ContratEnseignant,
            pk=contrat_pk,
            enseignant__etablissement_id=getattr(etablissement, "id", None),
        )
        contrat.numero_cheque = cheque_number
        contrat.demande_traitee = True
        contrat.save()

        messages.success(
            request, "Acompte validé, l'enseignant sera notifié."
        )
    else:
        messages.error(
            request, "Une erreur est survenue sur la demande d'acompte."
        )

    return redirect(
        reverse(
            "demande_accompte_list",
            kwargs={"demande": True, "traiter": False},
        )
    )


# -------------------------------------------------------------------
# AJAX : info contrat (modal)
# -------------------------------------------------------------------
@login_required
@staff_required
def get_contrat_info(request):
    etablissement = _get_user_etablissement(request)

    contrat_pk = request.GET.get("contrat_pk")

    if contrat_pk:
        contrat = get_object_or_404(
            ContratEnseignant,
            pk=contrat_pk,
            enseignant__etablissement_id=getattr(etablissement, "id", None),
        )
        data = {
            "code": contrat.enseignant.code,
            "filiere": contrat.filiere.nom,
            "niveau": contrat.niveau.nom,
            "classe": contrat.classe.nom,
            "matiere": contrat.matiere.nom,
            "enseignant": f"{contrat.enseignant.nom} {contrat.enseignant.prenom}",
            "montant": contrat.cout,
            "contrat_id": contrat.pk,
        }
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Contrat non trouvé."}, status=400)


# -------------------------------------------------------------------
# Remise de chèque (acompte)
# -------------------------------------------------------------------
@login_required
@staff_required
def reception_cheque(request, code, pk):
    etablissement = _get_user_etablissement(request)

    contrat = get_object_or_404(
        ContratEnseignant,
        enseignant__code=code,
        pk=pk,
        enseignant__etablissement_id=getattr(etablissement, "id", None),
    )
    contrat.cheque_retire = True
    contrat.save()

    context = {
        "titre": f"Remise de cheque {contrat.enseignant}-{contrat}",
        "info": "Remise de cheque",
        "info2": f"Remise de cheque {contrat.enseignant}-{contrat}",
        "enseignant": "Remise de cheque",
        "contrat": contrat,
    }
    return render(
        request,
        "enseignant/contrats/accomptes/fiche_reception.html",
        context=context,
    )


# -------------------------------------------------------------------
# Liste globale des contrats (admin)
# -------------------------------------------------------------------
@user_passes_test(is_staff_or_teacher)
def contrat_list_admin(request):
    etablissement = _get_user_etablissement(request)

    # Cas où le user n'a pas d'établissement rattaché
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Liste Contrats",
            "info": "Liste Contrats",
            "info2": "Liste Contrats",
            "enseignant": "Liste Contrats",
            "contrats": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "enseignant/contrats/listes.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annee_active, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    contrats_qs = ContratEnseignant.objects.filter(
        annee_academique__etablissement_id=etablissement.id
    ).order_by("classe", "filiere", "niveau")

    if annee_active is not None:
        contrats_qs = contrats_qs.filter(annee_academique=annee_active)
    else:
        contrats_qs = contrats_qs.none()
        messages.info(
            request,
            "Aucune année académique n'est définie pour votre établissement.",
        )

    context = {
        "titre": "Liste Contrats",
        "info": "Liste Contrats",
        "info2": "Liste Contrats",
        "enseignant": "Liste Contrats",
        "contrats": contrats_qs,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "annee_active": annee_active,
        "no_etablissement": False,
    }
    return render(request, "enseignant/contrats/listes.html", context=context)


# -------------------------------------------------------------------
# Création des Travaux Dirigés
# -------------------------------------------------------------------
@login_required
@staff_required
def creation_travaux_dirige(request, pk):
    etablissement = _get_user_etablissement(request)

    contrat = get_object_or_404(
        ContratEnseignant,
        pk=pk,
        annee_academique__etablissement_id=getattr(etablissement, "id", None),
    )

    if request.method == "POST":
        heure_raw = request.POST.get("heure")
        taux_raw = request.POST.get("taux")

        try:
            heure = int(heure_raw)
            taux = int(taux_raw)
            td = TravauxDirige.objects.create(
                contrat_id=pk, volume_horaire=heure, taux_horaire=taux
            )
            messages.success(request, "Le TD a été créé avec succès.")
            return redirect(
                reverse("td_enseignant_print", kwargs={"pk": td.pk})
            )

        except (ValueError, TypeError):
            messages.error(
                request,
                "Les valeurs de volume horaire et taux horaire doivent être des entiers.",
            )
        except Exception as e:
            messages.error(request, f"Une erreur est survenue: {e}")

    context = {
        "titre": f"CREATION DE TRAVAUX DIRIGÉS POUR LE CONTRAT {contrat}",
        "info": "TRAVAUX DIRIGÉS",
        "info2": "",
        "contrat": contrat,
    }
    return render(
        request, "enseignant/contrats/creation_td.html", context=context
    )


@login_required
@staff_required
def td_enseignant_print(request, pk):
    td = get_object_or_404(TravauxDirige, pk=pk)
    context = {
        "titre": f"{td.contrat.enseignant} TD -  {td.contrat}",
        "info": "Nouveau Contrat",
        "info2": td.contrat.enseignant,
        "enseignant": td.contrat.enseignant,
        "td": td,
        "contrat": td.contrat,
    }
    return render(request, "enseignant/contrats/td.html", context=context)


# -------------------------------------------------------------------
# RIB enseignant
# -------------------------------------------------------------------
@login_required
@teacher_required
def rib_create_and_list(request):
    enseignant = request.user.enseignant

    if request.method == "POST":
        form = RibForm(request.POST, request.FILES)
        if form.is_valid():
            rib = form.save(commit=False)
            rib.enseignant = enseignant
            rib.save()
            messages.success(request, "RIB enregistré avec succès.")
            return redirect("rib_create_and_list")
    else:
        form = RibForm()

    ribs = Rib.objects.filter(enseignant=enseignant).order_by("-created")

    context = {
        "titre": "RIB",
        "info": "RIB",
        "info2": "Liste des RIB",
        "form": form,
        "ribs": ribs,
        "datatable": True,
    }

    return render(
        request, "enseignant/dashboard/rib_form.html", context=context
    )


@login_required
@teacher_required
def delete_rib(request, rib_id):
    rib = get_object_or_404(Rib, id=rib_id, enseignant=request.user.enseignant)
    enseignant = rib.enseignant
    rib.delete()

    most_recent_plan = Rib.objects.filter(
        enseignant=enseignant
    ).order_by("-created").first()

    if most_recent_plan:
        most_recent_plan.default = True
        most_recent_plan.save()

    messages.success(request, "RIB supprimé avec succès.")
    return redirect("rib_create_and_list")


# -------------------------------------------------------------------
# TD - liste (côté enseignant)
# -------------------------------------------------------------------
@login_required
@teacher_required
def td_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement.",
        )
        context = {
            "titre": "Mes TD",
            "info": "Enseignant",
            "info2": "Mes TD",
            "programmes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "enseignant/dashboard/td_liste.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annee_selectionnee, annees_academiques = _get_selected_or_last_annee(
        etablissement, selected_annee_id
    )

    contrats = ContratEnseignant.objects.filter(
        annee_academique__etablissement_id=etablissement.id,
        enseignant=request.user.enseignant,
    )

    if annee_selectionnee is not None:
        contrats = contrats.filter(annee_academique_id=annee_selectionnee.id)
    else:
        contrats = contrats.none()
        messages.info(
            request,
            "Aucune année académique n'est définie pour votre établissement.",
        )

    context = {
        "titre": "Mes TD",
        "info": "Enseignant",
        "info2": "Mes TD",
        "programmes": contrats,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "selected_annee": annee_selectionnee.id if annee_selectionnee else None,
        "no_etablissement": False,
    }
    return render(
        request, "enseignant/dashboard/td_liste.html", context=context
    )
