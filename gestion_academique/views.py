from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    Salle,
    Niveau,
    UniteEnseignement,
    Campus,
    Etablissement,
    AnneeAcademique,
    Filiere,
    Classe,
)
from emplois_du_temps.models import Programme, EmploisDutemps
from inscription.models import Inscription
from .forms import MaquetteForm, UniteEnseignementForm, MatiereForm, ClasseForm

import openpyxl

from django.contrib.auth.decorators import login_required

from decorators.decorators import staff_required
from .models import Etablissement
from .forms import EtablissementForm


@login_required
@staff_required
def mon_etablissement(request):
    """
    Vue de profil d'établissement :
    - création si l'utilisateur n'a pas encore d'établissement
    - consultation + mise à jour sinon
    """

    user = request.user
    etablissement = getattr(user, "etablissement", None)

    if request.method == "POST":
        # Mode update ou création
        form = EtablissementForm(
            request.POST,
            request.FILES,
            instance=etablissement
        )
        if form.is_valid():
            etab = form.save()

            # Si l'utilisateur n'avait pas encore d'établissement,
            # on le lie à celui qui vient d'être créé ou mis à jour.
            if user.etablissement_id != etab.id:
                user.etablissement = etab
                user.save(update_fields=["etablissement"])

            messages.success(request, "Les informations de l'établissement ont été enregistrées avec succès.")
            return redirect("mon_etablissement")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = EtablissementForm(instance=etablissement)

    # On envoie un flag pour savoir si on est en mode création
    is_creation = etablissement is None

    context = {
        "titre": "Mon Établissement",
        "info": "Gestion",
        "info2": "Profil Établissement",
        "datatable": False,
        "can_select_annee": False,
        "form": form,
        "etablissement": etablissement,
        "is_creation": is_creation,
    }
    return render(request, "gestion_academique/etablissement/fiche.html", context)



def get_annees_academiques(request):
    """
    Endpoint AJAX pour récupérer les années académiques
    d'un établissement donné (via etablissement_id).
    """
    etablissement_id = request.GET.get("etablissement_id")
    if etablissement_id:
        annees = AnneeAcademique.objects.filter(
            etablissement_id=etablissement_id
        ).values("id", "debut", "fin")
        return JsonResponse(list(annees), safe=False)
    return JsonResponse([], safe=False)


# -------------------------------------------------------------------
# Utilitaire interne : récupération de l'établissement utilisateur
# -------------------------------------------------------------------
def _get_user_etablissement(request):
    """
    Retourne l'établissement associé à l'utilisateur ou None.
    """
    return getattr(request.user, "etablissement", None)


# -------------------------------------------------------------------
# Années académiques
# -------------------------------------------------------------------
@login_required
@staff_required
def annees_academiques_list(request):
    etablissement = _get_user_etablissement(request)

    # Cas où aucun établissement n'est rattaché à l'utilisateur
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Années Académiques",
            "info": "Liste",
            "info2": "Années Académiques",
            "annees": [],
            "datatable": False,
            "no_etablissement": True,
        }
        return render(
            request, "gestion_academique/annee_academique/list.html", context=context
        )

    if request.method == "POST":
        debut = request.POST.get("debut")
        fin = request.POST.get("fin")

        try:
            debut_int = int(debut)
            fin_int = int(fin)

            if AnneeAcademique.objects.filter(
                etablissement=etablissement, debut=debut_int, fin=fin_int
            ).exists():
                messages.error(
                    request, "L'année académique existe déjà pour ces dates."
                )
            else:
                AnneeAcademique.objects.create(
                    etablissement=etablissement, debut=debut_int, fin=fin_int
                )
                messages.success(
                    request, "L'année académique a été créée avec succès."
                )
        except ValueError:
            messages.error(
                request, "Les années doivent être des nombres entiers."
            )
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect("annees_academiques_list")

    context = {
        "titre": "Années Académiques",
        "info": "Liste",
        "info2": "Années Académiques",
        "annees": AnneeAcademique.objects.filter(
            etablissement_id=etablissement.id
        ).order_by("-debut", "-fin"),
        "datatable": True,
        "no_etablissement": False,
    }
    return render(
        request, "gestion_academique/annee_academique/list.html", context=context
    )

# -------------------------------------------------------------------
# Salles & Campus
# -------------------------------------------------------------------
@login_required
@staff_required
def salles_list(request):
    """
    Liste des salles + campus, création salle & campus,
    et tableau récapitulatif des capacités.
    """
    etablissement = _get_user_etablissement(request)

    # Cas où l'utilisateur n'est lié à aucun établissement
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Salles",
            "info": "Gestion",
            "info2": "Salles & Capacité",
            "salles": [],
            "campus": [],
            "datatable": False,
            "no_etablissement": True,
        }
        return render(
            request, "gestion_academique/salles/list.html", context=context
        )

    # Querysets de base
    campus_qs = Campus.objects.filter(etablissement=etablissement).order_by("nom")
    salles_qs = (
        Salle.objects.filter(etablissement=etablissement)
        .select_related("campus")
        .order_by("campus__nom", "nom")
    )

    if request.method == "POST":
        action = request.POST.get("action")

        # --------------------------------------------------
        # Création d'un CAMPUS
        # --------------------------------------------------
        if action == "create_campus":
            campus_nom = (request.POST.get("campus_nom") or "").strip()

            if len(campus_nom) < 3:
                messages.error(
                    request,
                    "Le nom du campus doit contenir au moins 3 caractères.",
                )
                return redirect("salles_list")

            if Campus.objects.filter(
                etablissement=etablissement, nom__iexact=campus_nom
            ).exists():
                messages.error(
                    request,
                    "Un campus avec ce nom existe déjà pour cet établissement.",
                )
                return redirect("salles_list")

            Campus.objects.create(
                etablissement=etablissement,
                nom=campus_nom,
                active=True,
            )
            messages.success(request, "Campus créé avec succès.")
            return redirect("salles_list")

        # --------------------------------------------------
        # Création d'une SALLE
        # --------------------------------------------------
        if action == "create_salle":
            nom = (request.POST.get("nom") or "").strip()
            capacite = (request.POST.get("capacite") or "").strip()
            campus_id = request.POST.get("campus_id")

            # Validation simple
            if len(nom) < 3:
                messages.error(
                    request,
                    "Le nom de la salle doit contenir au moins 3 caractères.",
                )
                return redirect("salles_list")

            try:
                capacite_int = int(capacite)
                if capacite_int <= 1:
                    raise ValueError
            except ValueError:
                messages.error(
                    request,
                    "La capacité doit être un nombre entier supérieur à 1.",
                )
                return redirect("salles_list")

            # Récupération du campus
            campus_obj = None
            if campus_id:
                try:
                    campus_obj = Campus.objects.get(
                        id=campus_id, etablissement=etablissement
                    )
                except Campus.DoesNotExist:
                    messages.error(
                        request,
                        "Le campus sélectionné est invalide pour cet établissement.",
                    )
                    return redirect("salles_list")
            else:
                messages.error(
                    request,
                    "Veuillez sélectionner un campus pour la salle.",
                )
                return redirect("salles_list")

            # Unicité salle par établissement + nom + campus
            if Salle.objects.filter(
                etablissement=etablissement,
                campus=campus_obj,
                nom__iexact=nom,
            ).exists():
                messages.error(
                    request,
                    "Une salle avec ce nom existe déjà sur ce campus.",
                )
                return redirect("salles_list")

            Salle.objects.create(
                etablissement=etablissement,
                campus=campus_obj,
                nom=nom,
                capacite=capacite_int,
            )
            messages.success(request, "La salle a été créée avec succès.")
            return redirect("salles_list")

        # Si action inconnue
        messages.error(request, "Action non reconnue.")
        return redirect("salles_list")

    # Calcul de la capacité globale de l'établissement
    total_capacity = etablissement.salles_count  # via @property

    context = {
        "titre": "Salles & Campus",
        "info": "Gestion Académique",
        "info2": "Salles, Campus & Capacités",
        "salles": salles_qs,
        "campus": campus_qs,
        "datatable": True,
        "no_etablissement": False,
        "total_capacity": total_capacity,
    }
    return render(
        request, "gestion_academique/salles/list.html", context=context
    )


# -------------------------------------------------------------------
# Filières
# -------------------------------------------------------------------
@login_required
@staff_required
def filieres_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Filières",
            "info": "Liste",
            "info2": "Filières",
            "filieres": [],
            "datatable": False,
            "no_etablissement": True,
        }
        return render(
            request, "gestion_academique/filiere/list.html", context=context
        )

    if request.method == "POST":
        nom = request.POST.get("nom")
        parcours = request.POST.get("parcours")
        sigle = request.POST.get("sigle")

        try:
            if (
                len(nom) >= 3
                and parcours in ["UNIVERSITAIRE", "PROFESSIONNEL"]
                and len(sigle) >= 2
            ):
                if Filiere.objects.filter(
                    etablissement=etablissement, nom=nom
                ).exists():
                    messages.error(
                        request, "La filière avec ce nom existe déjà."
                    )
                else:
                    Filiere.objects.create(
                        etablissement=etablissement,
                        nom=nom,
                        parcour=parcours,
                        sigle=sigle,
                    )
                    messages.success(
                        request, "La filière a été créée avec succès."
                    )
            else:
                messages.error(
                    request, "Les données de la filière ne sont pas valides."
                )
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect("filieres_list")

    context = {
        "titre": "Filières",
        "info": "Liste",
        "info2": "Filières",
        "filieres": Filiere.objects.filter(etablissement_id=etablissement.id),
        "datatable": True,
        "no_etablissement": False,
    }
    return render(
        request, "gestion_academique/filiere/list.html", context=context
    )


# -------------------------------------------------------------------
# Niveaux
# -------------------------------------------------------------------
@login_required
@staff_required
def niveaux_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Niveaux",
            "info": "Liste",
            "info2": "Niveaux",
            "niveaux": [],
            "datatable": False,
            "no_etablissement": True,
        }
        return render(
            request, "gestion_academique/niveau/list.html", context=context
        )

    if request.method == "POST":
        nom = request.POST.get("nom")

        try:
            if len(nom) >= 3:
                if Niveau.objects.filter(
                    etablissement=etablissement, nom=nom
                ).exists():
                    messages.error(
                        request, "Le niveau avec ce nom existe déjà."
                    )
                else:
                    Niveau.objects.create(
                        etablissement=etablissement,
                        nom=nom,
                    )
                    messages.success(
                        request, "Le niveau a été créé avec succès."
                    )
            else:
                messages.error(
                    request,
                    "Le nom du niveau doit contenir au moins 3 caractères.",
                )
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect("niveaux_list")

    context = {
        "titre": "Niveaux",
        "info": "Liste",
        "info2": "Niveaux",
        "niveaux": Niveau.objects.filter(etablissement_id=etablissement.id),
        "datatable": True,
        "no_etablissement": False,
    }
    return render(
        request, "gestion_academique/niveau/list.html", context=context
    )


# -------------------------------------------------------------------
# Classes
# -------------------------------------------------------------------
@login_required
@staff_required
def classes_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Classes",
            "info": "Liste",
            "info2": "Classes",
            "classes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "form": ClasseForm(user=request.user),
            "no_etablissement": True,
        }
        return render(
            request, "gestion_academique/classe/list.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement=etablissement
    ).order_by("-created")
    classes = Classe.objects.filter(
        annee_academique__etablissement=etablissement
    )

    if selected_annee_id:
        classes = classes.filter(annee_academique_id=selected_annee_id)
    else:
        derniere_annee = etablissement.annee_academiques.last()
        if derniere_annee:
            classes = classes.filter(annee_academique=derniere_annee)

    form = ClasseForm(user=request.user)

    if request.method == "POST":
        form = ClasseForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Classe ajoutée avec succès.")
                return redirect("classes_list")
            except Exception as e:
                messages.error(
                    request,
                    f"Erreur lors de l'ajout de la classe : {str(e)}",
                )
        else:
            messages.error(
                request,
                "Veuillez corriger les erreurs dans le formulaire.",
            )

    context = {
        "titre": "Classes",
        "info": "Liste",
        "info2": "Classes",
        "classes": classes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "form": form,
        "no_etablissement": False,
    }
    return render(
        request, "gestion_academique/classe/list.html", context=context
    )




## Section Classes
@login_required
@staff_required
def classes_details(request,pk):
    classe = get_object_or_404(Classe, pk=pk)
    try:
        maquette = get_object_or_404(Maquette, annee_academique=classe.annee_academique, filiere=classe.filiere, niveau=classe.niveau)
        emplois_du_temps =  get_object_or_404(EmploisDutemps, classe_id=pk)
    except:
        maquette = False
        emplois_du_temps = False

    context = {
        "titre": f"Données {classe}",
        "info": "Info",
        "info2": "Classe",
        "classe": classe,
        "datatable": True,
        'jours_semaine' : ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE'],
        "programmes" : Programme.objects.filter(emplois_du_temps__classe=classe).order_by('debut','fin'),
        "maquette" : maquette,
        "evaluations" : classe.classe_note.all(),
        "emplois_du_temps" : emplois_du_temps,
        'etudiants' : Inscription.objects.filter(classe=classe).order_by('etudiant__nom','etudiant__prenom'),

    }
    return render(request, 'gestion_academique/classe/details.html', context=context)


## Section Classes
@login_required
@staff_required
def classes_appel(request,pk):
    classe = get_object_or_404(Classe, pk=pk)
    context = {
        "titre": f"Liste d'appel  {classe.nom}",
        'classe' : classe
    }
    return render(request, 'gestion_academique/classe/appel.html', context=context)


## Section Classes
@login_required
@staff_required
def classes_televerser_notes(request,pk):
    classe = get_object_or_404(Classe, pk=pk)
    context = {
        "titre": f"FICHE TELEVERSEMENT NOTES  {classe.nom}",
        'classe' : classe, 
        'etudiants' : classe.effectifs,
         "datatable": True,
         "not_order" : True,
    }
    return render(request, 'gestion_academique/classe/notes.html', context=context)

########################################### Section Maquettes
@login_required
@staff_required
def maquettes_list(request):
    # Récupérer l'établissement de l'utilisateur
    etablissement = _get_user_etablissement(request)

    # Si aucun établissement n'est lié au compte, on affiche un message explicite
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )

        context = {
            "titre": "Maquettes",
            "info": "Liste",
            "info2": "Maquettes",
            "maquettes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "form": None,
            "no_etablissement": True,
        }
        return render(
            request, "gestion_academique/maquette/list.html", context=context
        )

    # -----------------------------------------------
    # Cas normal : l'utilisateur a un établissement
    # -----------------------------------------------
    selected_annee_id = request.GET.get("annee_id")

    # Années académiques de l'établissement
    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    # Maquettes de l'établissement
    maquettes = Maquette.objects.filter(etablissement_id=etablissement.id)

    # Filtrage par année académique
    if selected_annee_id:
        maquettes = maquettes.filter(annee_academique_id=selected_annee_id)
    else:
        derniere_annee = etablissement.annee_academiques.last()
        if derniere_annee:
            maquettes = maquettes.filter(annee_academique_id=derniere_annee.id)

    # Gestion du formulaire
    if request.method == "POST":
        form = MaquetteForm(etablissement.id, request.POST)
        if form.is_valid():
            annee_academique = form.cleaned_data["annee_academique"]
            filiere = form.cleaned_data["filiere"]
            niveau = form.cleaned_data["niveau"]
            maquette_universitaire = form.cleaned_data["maquette_universitaire"]
            maquette_professionnel_jour = form.cleaned_data[
                "maquette_professionnel_jour"
            ]
            maquette_professionnel_soir = form.cleaned_data[
                "maquette_professionnel_soir"
            ]
            maquette_cours_en_ligne = form.cleaned_data[
                "maquette_cours_en_ligne"
            ]

            # Vérifier si une maquette avec les mêmes caractéristiques existe déjà
            existing_maquette = Maquette.objects.filter(
                etablissement=etablissement,
                annee_academique=annee_academique,
                filiere=filiere,
                niveau=niveau,
                maquette_universitaire=maquette_universitaire,
                maquette_professionnel_jour=maquette_professionnel_jour,
                maquette_professionnel_soir=maquette_professionnel_soir,
                maquette_cours_en_ligne=maquette_cours_en_ligne,
            ).exists()

            if existing_maquette:
                messages.error(
                    request,
                    "Une maquette avec les mêmes caractéristiques existe déjà.",
                )
            else:
                maquette = form.save(commit=False)
                maquette.etablissement = etablissement
                maquette.save()
                messages.success(request, "Maquette ajoutée avec succès.")
                return redirect("maquette_details", maquette.id)
        else:
            messages.error(
                request, "Veuillez corriger les erreurs dans le formulaire."
            )
    else:
        form = MaquetteForm(etablissement.id)

    context = {
        "titre": "Maquettes",
        "info": "Liste",
        "info2": "Maquettes",
        "maquettes": maquettes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "form": form,
        "no_etablissement": False,
    }
    return render(
        request, "gestion_academique/maquette/list.html", context=context
    )

@login_required
@staff_required
def maquette_details(request, pk):
    maquette = get_object_or_404(Maquette, pk=pk)
    unite_form = UniteEnseignementForm()
    matiere_form = MatiereForm(maquette.id)

    if request.method == 'POST':
        print(request.POST)
        if 'categorie' in request.POST:
            unite_form = UniteEnseignementForm(request.POST)
            if unite_form.is_valid():
                # Vérifier si l'unité d'enseignement existe déjà dans la maquette
                existing_unite = UniteEnseignement.objects.filter(
                    maquette=maquette,
                    nom=unite_form.cleaned_data['nom'],
                    semestre=unite_form.cleaned_data['semestre'],
                    categorie=unite_form.cleaned_data['categorie']
                ).exists()

                if existing_unite:
                    messages.error(request, "Une unité d'enseignement avec les mêmes caractéristiques existe déjà dans la maquette.")
                else:
                    unite_enseignement = unite_form.save(commit=False)
                    unite_enseignement.maquette = maquette
                    unite_enseignement.save()
                    messages.success(request, "Unité d'enseignement ajoutée avec succès.")
        elif 'unite' in request.POST:
            matiere_form = MatiereForm(maquette.id, request.POST)
            if matiere_form.is_valid():
                # Vérifier si la matière existe déjà dans la maquette
                existing_matiere = Matiere.objects.filter(
                    maquette=maquette,
                    unite=matiere_form.cleaned_data['unite'],
                    nom=matiere_form.cleaned_data['nom']
                ).exists()

                if existing_matiere:
                    messages.error(request, "Une matière avec le même nom existe déjà dans la maquette.")
                else:
                    matiere = matiere_form.save(commit=False)
                    matiere.maquette = maquette
                    matiere.save()
                    messages.success(request, "Matière ajoutée avec succès.")

    context = {
        "maquette": maquette,
        "matieres": maquette.matieres,
        "titre": maquette,
        "info": "Maquette Pédagogique",
        "info2": "Maquettes",
        "datatable": True,
        "unite_form": unite_form,
        "matiere_form": matiere_form,
    }

    return render(request, 'gestion_academique/maquette/detail.html', context=context)

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

@login_required
@staff_required
def statistiques(request):
    """
    Vue de statistiques globales sur les inscriptions / scolarités.
    Gère le cas où l'utilisateur n'a pas d'établissement rattaché.
    """

    # On récupère d'abord l'éventuel etablissement passé en GET
    etablissement_id_param = request.GET.get("etablissement_id")

    # Tous les établissements (pour un select dans le template par exemple)
    etablissements = Etablissement.objects.all()

    etablissement = None

    if etablissement_id_param:
        # Si un etablissement_id est fourni, on essaie de le charger
        try:
            etablissement = Etablissement.objects.get(pk=etablissement_id_param)
            etablissement_id = etablissement.id
        except Etablissement.DoesNotExist:
            messages.error(
                request,
                "L'établissement sélectionné n'existe pas. Merci de vérifier votre sélection."
            )
            # Pas d'établissement valide -> message + page vide
            context = {
                "titre": "Statistiques",
                "annees_academiques": [],
                "etablissements": etablissements,
                "selected_etablissement": None,
                "selected_annee": None,
                "cycle_stats": {},
                "niveau_stats": {},
                "total_inscriptions": 0,
                "total_re_inscriptions": 0,
                "total_new_inscriptions": 0,
                "affectes": 0,
                "non_affectes": 0,
                "inscriptions_attente_paiement": 0,
            }
            return render(request, "gestion_academique/statistiques.html", context)
    else:
        # Sinon on tente de prendre l'établissement de l'utilisateur
        etablissement = _get_user_etablissement(request)
        if etablissement is None:
            messages.error(
                request,
                "Votre compte n'est rattaché à aucun établissement. "
                "Merci de contacter l’administrateur pour corriger cette situation."
            )
            context = {
                "titre": "Statistiques",
                "annees_academiques": [],
                "etablissements": etablissements,
                "selected_etablissement": None,
                "selected_annee": None,
                "cycle_stats": {},
                "niveau_stats": {},
                "total_inscriptions": 0,
                "total_re_inscriptions": 0,
                "total_new_inscriptions": 0,
                "affectes": 0,
                "non_affectes": 0,
                "inscriptions_attente_paiement": 0,
            }
            return render(request, "gestion_academique/statistiques.html", context)

        etablissement_id = etablissement.id

    # À partir d'ici, on est sûr d'avoir un établissement valide
    annee_id = request.GET.get("annee_id")

    # Années académiques de cet établissement
    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement_id
    ).order_by("-created")

    # Inscriptions / scolarités confirmées
    scolarites = Inscription.objects.filter(
        etudiant__etablissement=etablissement,
        confirmed=True,
    )

    # Filtrage par année académique
    if annee_id:
        try:
            annee_nom = AnneeAcademique.objects.get(
                pk=annee_id, etablissement_id=etablissement_id
            )
            scolarites = scolarites.filter(annee_academique_id=annee_id)
        except AnneeAcademique.DoesNotExist:
            annee_nom = "Inconnue"
            messages.error(
                request,
                "L'année académique sélectionnée n'existe pas pour cet établissement."
            )
    else:
        last_annee_academique = etablissement.annee_academiques.last()
        if last_annee_academique:
            scolarites = scolarites.filter(annee_academique=last_annee_academique)
            annee_nom = last_annee_academique
        else:
            # Aucun année académique : on laisse scolarites tel quel (probablement vide)
            annee_nom = "Aucune année académique définie"

    # Agrégats globaux
    total_stats = scolarites.aggregate(
        total_inscriptions=Count("id"),
        total_re_inscriptions=Count("id", filter=Q(nature="RE-INSCRIPTION")),
        total_new_inscriptions=Count("id", filter=Q(nature="INSCRIPTION")),
        affectes=Count("id", filter=Q(etudiant__type_etudiant="Affecté(e)")),
        non_affectes=Count("id", filter=Q(etudiant__type_etudiant="Non Affecté(e)")),
        inscriptions_attente_paiement=Count(
            "id",
            filter=Q(paye=0) & ~Q(solded=True),
        ),
    )

    cycles = [
        "CYCLE UNIVERSITAIRE",
        "CYCLE PROFESSIONNEL JOUR",
        "CYCLE PROFESSIONNEL SOIR",
        "CYCLE EN LIGNE",
    ]
    cycle_stats = {}
    niveau_stats = {}
    ordre_niveaux = [
        "BTS 1",
        "BTS 2",
        "LICENCE 1",
        "LICENCE 2",
        "LICENCE 3",
        "MASTER 1",
        "MASTER 2",
    ]

    for cycle in cycles:
        cycle_queryset = scolarites.filter(parcour=cycle)

        cycle_stats[cycle] = {
            "etudiant_affecte": cycle_queryset.filter(
                etudiant__type_etudiant="Affecté(e)"
            ).count(),
            "etudiant_non_affecte": cycle_queryset.filter(
                etudiant__type_etudiant="Non Affecté(e)"
            ).count(),
            "inscriptions": cycle_queryset.filter(nature="INSCRIPTION").count(),
            "re_inscriptions": cycle_queryset.filter(
                nature="RE-INSCRIPTION"
            ).count(),
            "total": cycle_queryset.count(),
        }

        niveaux = (
            cycle_queryset.values("niveau__nom")
            .distinct()
        )
        niveaux = sorted(
            niveaux,
            key=lambda x: ordre_niveaux.index(x["niveau__nom"])
            if x["niveau__nom"] in ordre_niveaux
            else len(ordre_niveaux),
        )

        niveau_stats[cycle] = {}
        for niveau in niveaux:
            niveau_name = niveau["niveau__nom"]
            niveau_queryset = cycle_queryset.filter(niveau__nom=niveau_name)

            niveau_stats[cycle][niveau_name] = {
                "etudiant_affecte": niveau_queryset.filter(
                    etudiant__type_etudiant="Affecté(e)"
                ).count(),
                "etudiant_non_affecte": niveau_queryset.filter(
                    etudiant__type_etudiant="Non Affecté(e)"
                ).count(),
                "inscriptions": niveau_queryset.filter(
                    nature="INSCRIPTION"
                ).count(),
                "re_inscriptions": niveau_queryset.filter(
                    nature="RE-INSCRIPTION"
                ).count(),
                "total": niveau_queryset.count(),
            }

    context = {
        **total_stats,
        "cycle_stats": cycle_stats,
        "niveau_stats": niveau_stats,
        "titre": f"Statistiques de l'Année Académique {annee_nom}",
        "annees_academiques": annees_academiques,
        "etablissements": etablissements,
        "selected_etablissement": etablissement_id,
        "selected_annee": annee_id,
    }
    return render(request, "gestion_academique/statistiques.html", context)


@login_required
@staff_required
def recap_inscriptions(request):
    """
    Récapitulatif des inscriptions par filière / niveau / cycle.
    Gère l'absence d'établissement rattaché.
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "titre": "Récapitulatif des Inscriptions",
            "stats": [],
            "info": "Récapitulatif des Inscriptions",
            "info2": "Récapitulatif des Inscriptions",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
        }
        return render(request, "gestion_academique/effectifs.html", context)

    # Années académiques liées à l'établissement
    annees_academiques = AnneeAcademique.objects.filter(
        etablissement=etablissement
    ).order_by("-created")

    selected_annee_id = request.GET.get("annee_id")

    if selected_annee_id:
        annee_academique = get_object_or_404(
            AnneeAcademique,
            pk=selected_annee_id,
            etablissement=etablissement,
        )
    else:
        annee_academique = annees_academiques.first()

    if annee_academique is None:
        messages.warning(
            request,
            "Aucune année académique n'est encore définie pour cet établissement."
        )
        inscriptions = Inscription.objects.none()
    else:
        inscriptions = Inscription.objects.filter(
            etudiant__etablissement=etablissement,
            confirmed=True,
            annee_academique=annee_academique,
        )

    stats = (
        inscriptions.values("filiere__nom", "niveau__nom", "parcour")
        .annotate(total_inscriptions=Count("id"))
        .order_by("parcour", "filiere__nom", "niveau__nom")
    )

    context = {
        "titre": f"Récapitulatif des Inscriptions {annee_academique}"
        if annee_academique
        else "Récapitulatif des Inscriptions",
        "stats": stats,
        "info": "Récapitulatif des Inscriptions",
        "info2": "Récapitulatif des Inscriptions",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }

    return render(request, "gestion_academique/effectifs.html", context)

@login_required
@staff_required
def scolarites_par_statut(request, statut):
    """
    Liste des scolarités filtrées par statut (total, new, re, affectes, non_affectes, attente_paiement).
    Gère l'absence d'établissement rattaché.
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "scolarites": [],
            "statut": statut,
            "titre": f"Listes Inscriptions {statut}",
            "info": "Liste des Scolarités",
            "info2": "Liste des Scolarités",
            "datatable": False,
            "can_select_annee": False,
        }
        return render(
            request, "gestion_academique/scolarites_par_statut.html", context
        )

    base_qs = Inscription.objects.filter(etudiant__etablissement=etablissement)

    if statut == "total":
        scolarites = base_qs
    elif statut == "new":
        scolarites = base_qs.filter(nature="INSCRIPTION")
    elif statut == "re":
        scolarites = base_qs.filter(nature="RE-INSCRIPTION")
    elif statut == "affectes":
        scolarites = base_qs.filter(etudiant__type_etudiant="Affecté(e)")
    elif statut == "non_affectes":
        scolarites = base_qs.filter(etudiant__type_etudiant="Non Affecté(e)")
    elif statut == "attente_paiement":
        scolarites = base_qs.filter(paye=0, solded=False)
    else:
        scolarites = Inscription.objects.none()

    context = {
        "scolarites": scolarites,
        "statut": statut,
        "titre": f"Listes Inscriptions {statut}",
        "info": "Liste des Scolarités",
        "info2": "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
    }

    return render(
        request, "gestion_academique/scolarites_par_statut.html", context
    )

### Migrations et fusion


@login_required
@staff_required
def migrate_students(request):
    """
    Crée une nouvelle classe à partir d'une classe fermée (closed=True)
    et migre N étudiants de l'ancienne vers la nouvelle.

    Gère le cas où l'utilisateur n'a pas d'établissement rattaché.
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "titre": "Migration de Classe",
            "info": "Migration de Classe",
            "info2": "Migration de Classe",
            "datatable": False,
            "can_select_annee": False,
            "classes": [],
            "annees_academiques": [],
        }
        return render(request, "gestion_academique/migrate_students.html", context)

    selected_annee_id = request.GET.get("annee_id")

    # Années académiques de l'établissement
    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    # Classes fermées de cet établissement
    classes_qs = Classe.objects.filter(
        annee_academique__etablissement_id=etablissement.id,
        closed=True,
    )

    if selected_annee_id:
        classes_qs = classes_qs.filter(annee_academique_id=selected_annee_id)
    else:
        last_annee = etablissement.annee_academiques.last()
        if last_annee:
            classes_qs = classes_qs.filter(annee_academique=last_annee)
        else:
            messages.warning(
                request,
                "Aucune année académique n'est encore définie pour votre établissement."
            )

    if request.method == "POST":
        selected_class_id = request.POST.get("selected_class")
        num_to_migrate_raw = request.POST.get("num_to_migrate")

        if not selected_class_id or not num_to_migrate_raw:
            messages.error(
                request,
                "Veuillez sélectionner une classe et saisir le nombre d'étudiants à migrer."
            )
            return redirect("migrate_students")

        try:
            num_to_migrate = int(num_to_migrate_raw)
            if num_to_migrate <= 0:
                raise ValueError
        except ValueError:
            messages.error(
                request,
                "Le nombre d'étudiants à migrer doit être un entier strictement positif."
            )
            return redirect("migrate_students")

        try:
            selected_class = Classe.objects.get(
                id=selected_class_id,
                annee_academique__etablissement=etablissement,
            )
        except Classe.DoesNotExist:
            messages.error(
                request,
                "La classe sélectionnée est introuvable pour votre établissement."
            )
            return redirect("migrate_students")

        # Création d'une nouvelle classe avec les mêmes caractéristiques
        new_class = Classe.objects.create(
            annee_academique=selected_class.annee_academique,
            filiere=selected_class.filiere,
            niveau=selected_class.niveau,
            classe_universitaire=selected_class.classe_universitaire,
            classe_professionnelle_jour=selected_class.classe_professionnelle_jour,
            classe_professionnelle_soir=selected_class.classe_professionnelle_soir,
            classe_online=selected_class.classe_online,
            closed=False,  # on laisse la nouvelle classe ouverte par défaut
            # ➜ si tu as d'autres champs obligatoires, ajoute-les ici
        )

        # Étudiants à migrer (les plus anciens)
        students_to_migrate = (
            Inscription.objects
            .filter(classe=selected_class)
            .order_by("created")[:num_to_migrate]
        )

        for student in students_to_migrate:
            student.classe = new_class
            student.save(update_fields=["classe"])

        messages.success(
            request,
            f"Migration effectuée avec succès vers la nouvelle classe : {new_class}"
        )
        return redirect("classes_list")

    context = {
        "titre": "Migration de Classe",
        "info": "Migration de Classe",
        "info2": "Migration de Classe",
        "datatable": True,
        "can_select_annee": True,
        "classes": classes_qs,
        "annees_academiques": annees_academiques,
    }
    return render(request, "gestion_academique/migrate_students.html", context)

@login_required
@staff_required
def move_uto_other_class_students(request):
    """
    Fusion / déplacement d'étudiants d'une classe source vers une classe destination.

    - Les deux classes doivent appartenir au même établissement.
    - Les deux classes doivent avoir les mêmes caractéristiques filière / niveau / année.
    """
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "annees_academiques": [],
            "classes": [],
            "titre": "Fusion de Classe",
            "info": "Fusion de Classe",
            "info2": "Fusion de Classe",
            "datatable": False,
            "can_select_annee": False,
        }
        return render(request, "gestion_academique/move.html", context)

    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    classes_qs = Classe.objects.filter(
        annee_academique__etablissement_id=etablissement.id,
        closed=True,
    )

    if selected_annee_id:
        classes_qs = classes_qs.filter(annee_academique_id=selected_annee_id)
    else:
        last_annee = etablissement.annee_academiques.last()
        if last_annee:
            classes_qs = classes_qs.filter(annee_academique=last_annee)
        else:
            messages.warning(
                request,
                "Aucune année académique n'est encore définie pour votre établissement."
            )

    if request.method == "POST":
        source_class_id = request.POST.get("source_class")
        destination_class_id = request.POST.get("destination_class")
        num_to_migrate_raw = request.POST.get("num_to_migrate")

        if not source_class_id or not destination_class_id or not num_to_migrate_raw:
            messages.error(
                request,
                "Veuillez sélectionner une classe source, une classe destination "
                "et saisir le nombre d'étudiants à déplacer."
            )
            return redirect("move_uto_other_class_students")

        try:
            num_to_migrate = int(num_to_migrate_raw)
            if num_to_migrate <= 0:
                raise ValueError
        except ValueError:
            messages.error(
                request,
                "Le nombre d'étudiants à déplacer doit être un entier strictement positif."
            )
            return redirect("move_uto_other_class_students")

        try:
            source_class = Classe.objects.get(
                id=source_class_id,
                annee_academique__etablissement=etablissement,
            )
            destination_class = Classe.objects.get(
                id=destination_class_id,
                annee_academique__etablissement=etablissement,
            )
        except Classe.DoesNotExist:
            messages.error(
                request,
                "La classe source ou la classe destination est introuvable pour votre établissement."
            )
            return redirect("move_uto_other_class_students")

        # Vérifier que les classes ont les mêmes caractéristiques
        if (
            source_class.filiere != destination_class.filiere
            or source_class.niveau != destination_class.niveau
            or source_class.annee_academique != destination_class.annee_academique
        ):
            messages.error(
                request,
                "Les classes sélectionnées n'ont pas les mêmes filière, niveau ou année académique."
            )
            return redirect("move_uto_other_class_students")

        # On récupère les N plus anciennes inscriptions
        students_to_migrate = (
            Inscription.objects
            .filter(classe=source_class)
            .order_by("created")[:num_to_migrate]
        )

        for student in students_to_migrate:
            student.classe = destination_class
            student.save(update_fields=["classe"])

        # Optionnel : si la classe source n'a plus d'étudiants, on la supprime
        # (en gardant ta logique existante sur nb_etudiant si tu l'as)
        try:
            if hasattr(source_class, "nb_etudiant"):
                if source_class.nb_etudiant == 0:
                    source_class.delete()
        except Exception:
            # En cas de problème sur nb_etudiant, on ne plante pas la vue
            pass

        messages.success(
            request,
            "Les classes ont été fusionnées avec succès."
        )
        return redirect("classes_list")

    context = {
        "annees_academiques": annees_academiques,
        "classes": classes_qs,
        "titre": "Fusion de Classe",
        "info": "Fusion de Classe",
        "info2": "Fusion de Classe",
        "datatable": True,
        "can_select_annee": True,
    }
    return render(request, "gestion_academique/move.html", context)



## Section Classes
@login_required
@staff_required
def classes_certificats(request,pk):
    classe = get_object_or_404(Classe, pk=pk)
    context = {
        "titre": f"certificat {classe.nom}",
        'classe' : classe, 
        'etudiants' : classe.effectifs,
         "datatable": True,
         "not_order" : True,
    }
    return render(request, 'gestion_academique/classe/certificat.html', context=context)
########################################### Section Maquettes

## Section Classes
@login_required
@staff_required
def classes_recu(request,pk):
    classe = get_object_or_404(Classe, pk=pk)
    context = {
        "titre": f"RECU {classe.nom}",
        'classe' : classe, 
        'etudiants' : classe.effectifs,
         "datatable": True,
         "not_order" : True,
    }
    return render(request, 'gestion_academique/classe/recu.html', context=context)
########################################### Section Maquettes


# Statistiques

## Section Classes
@login_required
@staff_required
def classes_details_results(request,pk):
    classe = get_object_or_404(Classe, pk=pk)

    context = {
        "titre": f"Statistiques {classe}",
        "info": "Statistiques",
        "info2": "Classe",
        "classe": classe,
        "datatable": True,
        'etudiants' : Inscription.objects.filter(classe=classe).order_by('etudiant__nom','etudiant__prenom'),

    }
    return render(request, 'gestion_academique/classe/stats.html', context=context)


# Statistiques

## Section Classes
@login_required
@staff_required
def global_results(request):
    context = {
        
    "titre": f"Statistiques Annuelle",
    "info": "Statistiques",
    "info2": "Classe",
    "datatable": True,
    'etudiants' : Inscription.objects.all().order_by('classe','filiere','niveau','etudiant__nom','etudiant__prenom'),
}
    return render(request, 'gestion_academique/classe/annuelle.html', context=context)














############################# Diplome 


from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import SessionDiplome, Diplome
from .forms import SessionDiplomeForm, UploadFileForm
import pandas as pd
import logging
from django.db import transaction
import re


logger = logging.getLogger(__name__)

class SessionListViewCreation(View):
    template_name = 'diplomes/diplome_create.html'

    def get(self, request):
        # 🚨 L'instanciation des formulaires est essentielle ici pour l'affichage 🚨
        form = SessionDiplomeForm()
        upload_form = UploadFileForm()

        return render(request, self.template_name, {
            'form': form,
            'upload_form': upload_form, # <-- Formulaire d'upload passé au template
            "titre": "Commission Diplôme et Documentation Académique",
            "info": "Liste des Sessions",
            "info2": "Commission Diplôme et Documentation Académique",
            "datatable": True,
        })
    
    def post(self, request):
        # 🚨 L'instanciation avec les données POST/FILES est essentielle ici pour la validation 🚨
        form = SessionDiplomeForm(request.POST)
        upload_form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid() and upload_form.is_valid():
            
            # Liste pour stocker les objets Diplome avant l'insertion en masse
            diplomes_a_creer = [] 
            erreurs_lignes = []

            try:
                with transaction.atomic():
                    # 1. Création de la Session
                    session = form.save(commit=False)
                    session.etablissement = request.user.etablissement
                    session.save()

                    # 2. Lecture du Fichier Excel
                    file = upload_form.cleaned_data['file']
                    df = pd.read_excel(file)

                    if df.empty:
                        messages.error(request, "Le fichier Excel est vide.")
                        # On ne fait pas de 'raise' ici car la transaction est déjà commencée
                        # mais on redirige l'utilisateur.
                        return redirect('session_list')

                    # 3. Vérifications des Colonnes
                    required_columns = [
                        'nom', 'prenom', 'date_de_naissance', 'lieu_de_naissance', 
                        'sexe', 'diplome', 'niveau', 'annee_academique', 
                        'date_soutenance', 'session_soutenance', 'cycle'
                    ]
                    
                    df.columns = df.columns.str.lower()
                    
                    for col in required_columns:
                        if col not in df.columns:
                            messages.error(request, f"Colonne manquante dans le fichier Excel : {col}")
                            # Lancer une exception annule la transaction entière
                            raise Exception(f"Colonne manquante: {col}") 
                    
                    # Préparation des données (Conversion en string pour les colonnes)
                    for col in ['nom', 'prenom', 'lieu_de_naissance', 'diplome', 'niveau', 'cycle']:
                        if col in df.columns:
                            # Assure que le nettoyage .strip() fonctionnera
                            df[col] = df[col].astype(str) 

                    # 4. Traitement ligne par ligne pour la validation et la construction des objets
                    for index, row in df.iterrows():
                        try:
                            nom = str(row['nom']).strip()
                            prenom = str(row['prenom']).strip()
                            date_naissance = pd.to_datetime(row['date_de_naissance'], errors='coerce')

                            if pd.isna(date_naissance):
                                raise ValueError("Date de naissance invalide.")
                            
                            date_naissance_normalisee = date_naissance.date()

                            # Génération du matricule
                            matricule_base = self.generer_matricule_base(nom, prenom, date_naissance_normalisee)
                            matricule = f"{matricule_base}0001" # (Basé sur votre ancienne logique)
                            
                            # Création de l'objet Diplome en mémoire
                            diplome = Diplome(
                                session=session,
                                matricule=matricule,
                                nom=nom,
                                prenom=prenom,
                                date_de_naissance=date_naissance_normalisee,
                                lieu_de_naissance=row['lieu_de_naissance'],
                                sexe=row['sexe'],
                                contact1=row.get('contact1', ''),
                                contact2=row.get('contact2', ''),
                                diplome=row['diplome'],
                                niveau=row['niveau'],
                                annee_academique=row['annee_academique'],
                                date_soutenance=row['date_soutenance'],
                                session_soutenance=row['session_soutenance'],
                                cycle=row['cycle'],
                            )
                            diplomes_a_creer.append(diplome)

                        except Exception as e:
                            # Loggue l'erreur et continue au lieu d'annuler toute l'opération
                            log_msg = f"Erreur lors du traitement de la ligne {index + 2} : {str(e)}"
                            logger.error(log_msg)
                            erreurs_lignes.append(f"Ligne {index + 2}: {str(e)}")
                            
                    # 5. Insertion en masse des données
                    if diplomes_a_creer:
                        Diplome.objects.bulk_create(diplomes_a_creer)
                        messages.success(request, f"Session et {len(diplomes_a_creer)} Diplômes créés avec succès.")
                    
                    if erreurs_lignes:
                        messages.warning(request, f"Attention: {len(erreurs_lignes)} ligne(s) non importée(s) à cause d'erreurs de données. Veuillez corriger et réimporter.")
                    
                    return redirect('session_list')

            except pd.errors.EmptyDataError:
                messages.error(request, "Le fichier Excel est vide.")
            except pd.errors.ParserError:
                messages.error(request, "Erreur lors de l'analyse du fichier Excel. Assurez-vous du bon format.")
            except Exception as e:
                # Capture les erreurs fatales (colonnes manquantes, etc.)
                logger.error(f"Erreur fatale lors du traitement de la session : {str(e)}")
                messages.error(request, f"Une erreur fatale est survenue : {str(e)}. L'importation a été annulée.")
            
            return redirect('session_list')
        
        else:
            # En cas d'échec de validation du formulaire initial
            messages.warning(request, "Erreur de validation du formulaire. Vérifiez les champs saisis.")

        # 🚨 En cas d'échec de POST (else), on renvoie les formulaires avec leurs erreurs 🚨
        return render(request, self.template_name, {
            'form': form,
            'upload_form': upload_form,
            "titre": "Commission Diplôme et Documentation Académique",
            "info": "Liste des Sessions",
            "info2": "Commission Diplôme et Documentation Académique",
            "datatable": True,
        })

    # --- Fonctions auxiliaires (inchangées) ---

    def generer_matricule_base(self, nom, prenom, date_naissance):
        # ... (Votre logique de génération de matricule) ...
        nom_clean = re.sub(r'[^A-Za-z]', '', nom.upper())[:3]
        prenom_clean = re.sub(r'[^A-Za-z]', '', prenom.upper())[:1]

        nom_clean = (nom_clean + 'X' * 3)[:3]
        prenom_clean = (prenom_clean + 'X')[:1]

        date_str = date_naissance.strftime('%d%m%y')
        matricule = f"{nom_clean}{prenom_clean}{date_str}"
        
        return matricule

    def generer_matricule_unique_corrected(self, matricule_base):
        # Cette fonction est conservée pour complétude, même si elle n'est pas utilisée dans le post
        existing_matricules = Diplome.objects.filter(matricule__startswith=matricule_base).order_by('matricule')
        
        if not existing_matricules:
            return f"{matricule_base}0001"
        
        last_matricule = existing_matricules.last().matricule
        
        try:
            last_suffix_str = last_matricule[-4:]
            last_suffix = int(last_suffix_str)
            new_suffix = last_suffix + 1
        except (ValueError, IndexError):
            new_suffix = 1
        
        new_matricule = f"{matricule_base}{new_suffix:04d}"
        
        return new_matricule




class SessionListView(View):
    template_name = 'diplomes/session_list.html'

    def get(self, request):
        try:
            sessions = SessionDiplome.objects.all()
            form = SessionDiplomeForm()
            upload_form = UploadFileForm()
        except Exception as e:
            logger.error(f"Error fetching session data: {str(e)}")
            messages.error(request, "An error occurred while retrieving session data.")
            sessions, form, upload_form = [], None, None

        return render(request, self.template_name, {
            'sessions': sessions,
            'form': form,
            'upload_form': upload_form,
            "titre": "Commission Diplôme et Documentation Académique",
            "info": "Liste des Sessions",
            "info2": "Commission Diplôme et Documentation Académique",
            "datatable": True,
        })

    
        
        
logger = logging.getLogger(__name__)

class SessionDetailView(View):
    template_name = 'diplomes/session_detail.html'

    def get(self, request, pk):
        try:
            session = get_object_or_404(SessionDiplome, pk=pk)
            diplomes = Diplome.objects.filter(session=session)
        except SessionDiplome.DoesNotExist:
            logger.error(f"Session with ID {pk} does not exist.")
            messages.error(request, "The requested session does not exist.")
            return redirect('session_list')
        except Exception as e:
            logger.error(f"Error fetching diplomas: {str(e)}")
            messages.error(request, "An error occurred while retrieving diplomas.")
            diplomes = []

        return render(request, self.template_name, {
            'session': session,
            'diplomes': diplomes,
            "titre": session,
            "info": "Liste des Dîplomes",
            "info2": "Commission Dîplome et Documentation Académique",
            "datatable": True,
        })
        
        
        
class Authenticite(View):
    template_name = 'diplomes/authenticite.html'

    def get(self, request, pk):
        try:
            session = get_object_or_404(SessionDiplome, pk=pk)
            diplomes = Diplome.objects.filter(session=session)
        except SessionDiplome.DoesNotExist:
            logger.error(f"Session with ID {pk} does not exist.")
            messages.error(request, "The requested session does not exist.")
            return redirect('session_list')
        except Exception as e:
            logger.error(f"Error fetching diplomas: {str(e)}")
            messages.error(request, "An error occurred while retrieving diplomas.")
            diplomes = []

        return render(request, self.template_name, {
            'session': session,
            'diplomes': diplomes,
            "titre": session,
            "info": "Liste des Dîplomes",
            "info2": "Certificats Authenticite",
            "datatable": True,
        })
        

class Reussite(View):
    template_name = 'diplomes/reussite.html'

    def get(self, request, pk):
        try:
            session = get_object_or_404(SessionDiplome, pk=pk)
            diplomes = Diplome.objects.filter(session=session)
        except SessionDiplome.DoesNotExist:
            logger.error(f"Session with ID {pk} does not exist.")
            messages.error(request, "The requested session does not exist.")
            return redirect('session_list')
        except Exception as e:
            logger.error(f"Error fetching diplomas: {str(e)}")
            messages.error(request, "An error occurred while retrieving diplomas.")
            diplomes = []

        return render(request, self.template_name, {
            'session': session,
            'diplomes': diplomes,
            "titre": session,
            "info": "Liste des Dîplomes",
            "info2": "Attestation de reussite",
            "datatable": True,
        })
        

class Admission(View):
    template_name = 'diplomes/admission.html'

    def get(self, request, pk):
        try:
            session = get_object_or_404(SessionDiplome, pk=pk)
            diplomes = Diplome.objects.filter(session=session)
        except SessionDiplome.DoesNotExist:
            logger.error(f"Session with ID {pk} does not exist.")
            messages.error(request, "The requested session does not exist.")
            return redirect('session_list')
        except Exception as e:
            logger.error(f"Error fetching diplomas: {str(e)}")
            messages.error(request, "An error occurred while retrieving diplomas.")
            diplomes = []

        return render(request, self.template_name, {
            'session': session,
            'diplomes': diplomes,
            "titre": session,
            "info": "Liste des Dîplomes",
            "info2": "Certificats d'Admission",
            "datatable": True,
        })
        

class DiplomesPrint(View):
    template_name = 'diplomes/diplome.html'

    def get(self, request, pk):
        try:
            session = get_object_or_404(SessionDiplome, pk=pk)
            diplomes = Diplome.objects.filter(session=session)
        except SessionDiplome.DoesNotExist:
            logger.error(f"Session with ID {pk} does not exist.")
            messages.error(request, "The requested session does not exist.")
            return redirect('session_list')
        except Exception as e:
            logger.error(f"Error fetching diplomas: {str(e)}")
            messages.error(request, "An error occurred while retrieving diplomas.")
            diplomes = []

        return render(request, self.template_name, {
            'session': session,
            'diplomes': diplomes,
            "titre": session,
            "info": "Liste des Dîplomes",
            "info2": "Diplomes",
            "datatable": True,
        })
        
        
        
class DocumentStudent(View):
    template_name = 'diplomes/student.html'

    def get(self, request, pk):
        try:
            diplome = get_object_or_404(Diplome, pk=pk)
        except SessionDiplome.DoesNotExist:
            logger.error(f"Session with ID {pk} does not exist.")
            messages.error(request, "The requested session does not exist.")
            return redirect('session_list')
        except Exception as e:
            logger.error(f"Error fetching diplomas: {str(e)}")
            messages.error(request, "An error occurred while retrieving diplomas.")
            diplome = None

        return render(request, self.template_name, {
            'attestation': diplome,
            "titre": diplome,
        })
        

class Cv(View):
    template_name = 'diplomes/cv.html'

    def get(self, request, pk):
        try:
            session = get_object_or_404(SessionDiplome, pk=pk)
            diplomes = Diplome.objects.filter(session=session)
        except SessionDiplome.DoesNotExist:
            logger.error(f"Session with ID {pk} does not exist.")
            messages.error(request, "The requested session does not exist.")
            return redirect('session_list')
        except Exception as e:
            logger.error(f"Error fetching diplomas: {str(e)}")
            messages.error(request, "An error occurred while retrieving diplomas.")
            diplomes = []

        return render(request, self.template_name, {
            'session': session,
            'diplomes': diplomes,
            "titre": session,
            "info": "CV des Dîplomes",
            "info2": "CV",
            "datatable": True,
        })
        


from django.views.generic import UpdateView, DetailView
from django.shortcuts import get_object_or_404
from .models import Maquette, Matiere
from django.urls import reverse_lazy
from django.views.generic import UpdateView

class MaquetteMatiereUpdateView(UpdateView):
    model = Maquette
    template_name = 'gestion_academique/maquette/maquette_update.html'
    fields = []  # Les champs de la maquette que vous souhaitez modifier, si nécessaire

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matieres'] = Matiere.objects.filter(unite__maquette=self.object).order_by('unite__semestre','nom')
        context['titre'] = self.object
        context['info'] = "Modification de Maquette "
        return context

    def get_object(self):
        # Récupérer l'objet Maquette
        return get_object_or_404(Maquette, pk=self.kwargs['pk'], etablissement=self.request.user.etablissement)

    def post(self, request, *args, **kwargs):
        maquette = self.get_object()
        matieres = Matiere.objects.filter(unite__maquette=maquette).order_by('unite__semestre','nom')

        # Mettre à jour les matières en fonction des données du formulaire
        for matiere in matieres:
            # Supposons que les noms des inputs pour les matières soient basés sur l'ID de la matière
            nom = request.POST.get(f'matiere_{matiere.id}_nom')
            coefficient = request.POST.get(f'matiere_{matiere.id}_coefficient')
            volume_horaire = request.POST.get(f'matiere_{matiere.id}_volume_horaire')
            taux_horaire = request.POST.get(f'matiere_{matiere.id}_taux_horaire')
            volume_horaire_td = request.POST.get(f'matiere_{matiere.id}_volume_horaire_td')
            taux_horaire_td = request.POST.get(f'matiere_{matiere.id}_taux_horaire_td')
            enseignant = request.POST.get(f'matiere_{matiere.id}_enseignant')

            matiere.nom = nom
            matiere.coefficient = coefficient
            matiere.volume_horaire = volume_horaire
            matiere.taux_horaire = taux_horaire
            matiere.enseignant = enseignant
            matiere.volume_horaire_td = volume_horaire_td
            matiere.taux_horaire_td = taux_horaire_td
            matiere.save()

        return super().form_valid(maquette)
    
    def get_success_url(self):
        return reverse_lazy('maquettes_list')  # Redirection vers la liste des maquettes


###########"" Liste pour progressions : 

@login_required
@staff_required
def progression_classes_list_(request):
    # 1) Récupération de l'établissement de l'utilisateur
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "titre": "Classes",
            "info": "Liste",
            "info2": "Classes",
            "classes": [],
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request,
            "gestion_academique/classe/progress_list.html",
            context=context,
        )

    # 2) Gestion de l'année académique (sélectionnée ou dernière)
    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    annee_active = None
    if selected_annee_id:
        # On vérifie que l’année demandée appartient à l’établissement
        annee_active = annees_academiques.filter(id=selected_annee_id).first()

    if annee_active is None:
        # À défaut, on prend la plus récente
        annee_active = annees_academiques.first()

    # 3) Récupération des classes de l'établissement + année active
    classes_qs = Classe.objects.filter(
        annee_academique__etablissement_id=etablissement.id
    )
    if annee_active:
        classes_qs = classes_qs.filter(annee_academique_id=annee_active.id)

    # 4) Contexte
    context = {
        "titre": "Classes",
        "info": "Liste",
        "info2": "Classes",
        "classes": classes_qs,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "annee_active": annee_active,
        "no_etablissement": False,
    }
    return render(
        request, "gestion_academique/classe/progress_list.html", context=context
    )



from django.shortcuts import get_object_or_404, render
from django.http import Http404
from .models import Classe, Maquette
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError

@login_required
@staff_required
def classes_progress_details(request, pk):
    # Récupérer la classe en fonction du pk
    try:
        classe = get_object_or_404(Classe, pk=pk)
    except Http404:
        # Si la classe n'existe pas, renvoyer une erreur 404 avec un message spécifique
        return render(request, 'gestion_academique/error.html', {"error": "Classe non trouvée"})

    # Essayer de récupérer la maquette correspondante
    try:
        maquette = Maquette.objects.filter(
                annee_academique=classe.annee_academique,
                filiere=classe.filiere,
                niveau=classe.niveau,
                maquette_universitaire=classe.classe_universitaire,
                maquette_professionnel_jour=classe.classe_professionnelle_jour,
                maquette_professionnel_soir=classe.classe_professionnelle_soir,
                maquette_cours_en_ligne=classe.classe_online
            ).first()
    except Http404:
        # Si la maquette n'existe pas, assigner une valeur False
        maquette = False
    except ObjectDoesNotExist as e:
        # Erreur d'objet inexistant (pour une autre exception spécifique)
        maquette = False
        print(f"Erreur lors de la récupération de la maquette : {e}")
    except OperationalError as e:
        # Si une erreur liée à la base de données survient
        print(f"Erreur opérationnelle avec la base de données : {e}")
        maquette = False
    except Exception as e:
        # Gestion de toute autre exception générale
        print(f"Erreur inattendue : {e}")
        maquette = False

    # Essayer de récupérer les matières de la maquette et les progressions
    try:
        matieres = maquette.matieres.all() if maquette else []
        progress = classe.progression_matiere_classe.all()
    except OperationalError as e:
        # Gestion d'erreur de base de données
        print(f"Erreur de récupération des matières ou progressions : {e}")
        matieres = []
        progress = []

    # Créer une liste des matières en cours (ayant une progression correspondante)
    matieres_use = [matiere for matiere in matieres if progress.filter(matiere_id=matiere.id).exists()]

    # Créer une liste des matières non utilisées (sans progression correspondante)
    matieres_not_uses = [matiere for matiere in matieres if not progress.filter(matiere_id=matiere.id).exists()]

    context = {
        "titre": f"PROGRESSSIONS {classe}",
        "info": "Info",
        "info2": "Classe",
        "classe": classe,
        "datatable": True,
        "matieres_use": matieres_use,
        "matieres_not_uses": matieres_not_uses,
        "progress": progress
    }

    return render(request, 'gestion_academique/classe/progress_details.html', context=context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ClasseProgression, Pointage

@csrf_exempt
@login_required
def create_classe_progression(request):
    if request.method == "POST":
        try:
            # Récupération des données
            matiere_id = request.POST.get("matiere_id")
            enseignant = request.POST.get("enseignant")
            classe_id = request.POST.get("classe_id")
            
            if not matiere_id or not enseignant or not classe_id:
                return JsonResponse({"error": "Tous les champs sont obligatoires."}, status=400)
            
            # Vérification des objets associés
            try:
                classe = Classe.objects.get(pk=classe_id)
                matiere = Matiere.objects.get(pk=matiere_id)
            except Classe.DoesNotExist:
                return JsonResponse({"error": "Classe introuvable."}, status=404)
            except Matiere.DoesNotExist:
                return JsonResponse({"error": "Matière introuvable."}, status=404)
            
            # Vérification de l'existence de la progression
            if ClasseProgression.objects.filter(classe=classe, matiere=matiere, enseignant=enseignant).exists():
                return JsonResponse({"error": "Cette progression existe déjà."}, status=400)
            
            # Création de la progression
            ClasseProgression.objects.create(
                classe=classe,
                matiere=matiere,
                enseignant=enseignant,
                volume_realise=0,
                active=True,
            )
            return JsonResponse({"message": "Progression enregistrée avec succès."})

        except Exception as e:
            return JsonResponse({"error": f"Erreur lors du traitement: {str(e)}"}, status=500)
    
    return JsonResponse({"error": "Requête invalide."}, status=400)


@csrf_exempt
@login_required
@staff_required
def create_pointage(request):
    if request.method == "POST":
        classe_progression_id = request.POST.get("classe_progression_id")
        volume_realise = int(request.POST.get("volume_realise"))
        observation = request.POST.get("observation")

        classe_progression = ClasseProgression.objects.get(pk=classe_progression_id)
        Pointage.objects.create(
            matiere=classe_progression,
            volume_realise=volume_realise,
            observation=observation,
            active=True,
        )
        
        if classe_progression.volume_realise + volume_realise <= classe_progression.matiere.volume_total:

            classe_progression.volume_realise += volume_realise
            classe_progression.save()
        
            messages.success(request, "La Progression a été enregistrée avec succes")
            return redirect("classes_progress_details", pk=classe_progression.classe.pk)
        
        messages.error(request, "Le volume horaire saisi ne respecte pas les normes")
        return redirect("classes_progress_details",pk=classe_progression.classe.pk)

    messages.error(request, "Une erreur est survenue")
    return redirect("classes_progress_details",pk=classe_progression.classe.pk)


@login_required
@staff_required
def pointage_details(request,pk):
    matiere = ClasseProgression.objects.get(pk=pk)
    return render(request, "gestion_academique/classe/progress_add.html", 
                  context = {
        "titre": f"POINTAGE {matiere}",
        "info": "PROGRESSION",
        "info2": "PROGRESSION",
        "matiere":matiere
       
    })
# Assurez-vous que ce décorateur est bien défini

@login_required
@staff_required
def pointage_details_dsk(request, pk):
    matiere = get_object_or_404(ClasseProgression, pk=pk)
    
    if matiere.reste == 0:
        matiere.paiement_effectue = True
        matiere.save()
        messages.success(request, "Le paiement a été validé avec succès !")
    else:
        messages.warning(request, f"Impossible de valider le paiement. Il reste encore {matiere.reste} heures à réaliser.")

    return redirect("global_progress")



@login_required
@staff_required
def reset_progress(request,pk):
    try:
        ClasseProgression.objects.get(pk=pk).delete()
        messages.success(request, "Module Réinitialisé avec succes")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except:
        messages.error(request, "Une Erreur est survenue...")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class ClasseProgressionUpdateView(UpdateView):
    model = ClasseProgression
    fields = ['enseignant', 'support', 'syllabys', 'piece', 'rib',  'cours_en_tronc_commun', 'note_deposee','paiement_effectue','demande_de_paiement_initie']
    template_name = 'gestion_academique/classe/progress_update.html'

    def get_object(self, queryset=None):
        """Méthode pour récupérer l'objet à mettre à jour."""
        pk = self.kwargs.get('pk')  # Récupère l'identifiant depuis les paramètres de l'URL
        return get_object_or_404(ClasseProgression, pk=pk)

    def get_success_url(self):
        """Redirection après une mise à jour réussie."""
        return reverse('classe_progression_printable', kwargs={'pk': self.object.pk})
    
    def get_form(self, form_class=None):
        """Ajoute la classe form-control à tous les champs du formulaire."""
        form = super().get_form(form_class)
        for field_name, field in form.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        return form

class ClasseProgressionPrintableView(DetailView):
    model = ClasseProgression
    template_name = 'gestion_academique/classe/progress_printable.html'

    def get_context_data(self, **kwargs):
        """Ajoute les URLs et QR codes au contexte."""
        context = super().get_context_data(**kwargs)
        progression = self.object  # L'objet ClasseProgression

        base_url = "https://myiipea.com"
        files = {
            "support": progression.support.url if progression.support else None,
            "syllabys": progression.syllabys.url if progression.syllabys else None,
            "piece": progression.piece.url if progression.piece else None,
            "rib": progression.rib.url if progression.rib else None,
        }
        context['files'] = files
        return context
    
    
    
    
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ClasseProgression, AnneeAcademique
from .models import Classe


@login_required
@staff_required
def global_progress(request):
    """
    Vue récapitulative des progressions de toutes les classes
    de l'établissement de l'utilisateur, avec filtre par année académique.
    """
    # 1) Récupération de l'établissement de l'utilisateur
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "annees_academiques": [],
            "progress": [],
            "selected_annee_id": None,
            "datatable": False,
            "can_select_annee": False,
            "titre": "PROGRESSIONS",
            "info": "PROGRESSION",
            "info2": "PROGRESSION",
            "no_etablissement": True,
        }
        return render(
            request,
            "gestion_academique/classe/global_progress.html",
            context,
        )

    # 2) Liste des années académiques actives de cet établissement
    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id,
        active=True,
    ).order_by("created")

    annee_active = None
    if selected_annee_id:
        # On vérifie que l'année demandée appartient bien à cet établissement
        annee_active = annees_academiques.filter(id=selected_annee_id).first()

    if annee_active is None:
        # Si rien de sélectionné ou ID invalide → on prend la dernière active
        annee_active = annees_academiques.last()

    # 3) Récupération des progressions pour l'établissement + année active
    progress_qs = ClasseProgression.objects.filter(
        classe__annee_academique__etablissement_id=etablissement.id
    ).order_by("id")

    if annee_active:
        progress_qs = progress_qs.filter(
            classe__annee_academique_id=annee_active.id
        )

    # 4) Contexte pour le template
    context = {
        "annees_academiques": annees_academiques,
        "progress": progress_qs,
        "selected_annee_id": annee_active.id if annee_active else None,
        "datatable": True,
        "can_select_annee": True,
        "titre": "PROGRESSIONS",
        "info": "PROGRESSION",
        "info2": "PROGRESSION",
        "annee_active": annee_active,
        "no_etablissement": False,
    }

    return render(
        request, "gestion_academique/classe/global_progress.html", context
    )



from django.shortcuts import render, redirect, get_object_or_404
from .forms import DossierMinistereForm
from .models import DossierMinistere, Filiere

def create_dossier(request):
    if request.method == 'POST':
        form = DossierMinistereForm(request.POST, request.FILES)
        if form.is_valid():
            dossier = form.save()
            dossier_code = f"DM-{dossier.id:05d}23/24/CI01"  # Generate a dossier code
            return redirect('dossier_detail', pk=dossier.id)
    else:
        form = DossierMinistereForm()
    return render(request, 'gestion_academique/ministere/create_dossier.html', {'form': form})

def dossier_detail(request, pk):
    dossier = get_object_or_404(DossierMinistere, pk=pk)
    return render(request, 'gestion_academique/ministere/dossier_detail.html', {'dossier': dossier, 'code': f"DM-{dossier.id:05d}23/24/CI01"})

@login_required
@staff_required
def list_dossiers(request):
    dossiers = DossierMinistere.objects.all()
    return render(request, 'gestion_academique/ministere/list_dossiers.html', {'dossiers': dossiers})


# Vue pour créer une classe
from .forms import ClasseForm
@login_required
@staff_required
def creer_classe(request):
    if request.method == "POST":
        form = ClasseForm(request.POST, user=request.user)
        if form.is_valid():
            classe = form.save(commit=False)
            classe.etablissement = request.user.etablissement
            classe.save()
            return redirect('classes_list')
    else:
        form = ClasseForm(user=request.user)
    return render(request, 'gestion_academique/classe/news.html', {'form': form})


@login_required
def toggle_classe_status(request, classe_id):
    """Vue permettant d'ouvrir ou de fermer une classe"""
    classe = get_object_or_404(Classe, id=classe_id, annee_academique__etablissement=request.user.etablissement)

    # Basculer le statut de la classe
    classe.closed = not classe.closed
    classe.save()

    if classe.closed:
        messages.success(request, "La classe a été fermée avec succès.")
    else:
        messages.success(request, "La classe a été ouverte avec succès.")

    return redirect('classes_list')  # Redirection vers la liste des classes



###########################################################################################################

import re
import datetime
# Vue pour charger un fichier Excel
# Fonction pour nettoyer et convertir une date au format YYYY-MM-DD
def clean_date(date_value):
    if isinstance(date_value, str):
        date_value = date_value.strip().replace("\xa0", "")  # Suppression des espaces invisibles
        
        match = re.match(r'(\d{2})/(\d{2})/(\d{4})', date_value)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month}-{day}"

    return date_value  # Retourne la valeur d'origine si elle est déjà bien formatée

# Vue pour charger un fichier Excel
def upload_excel(request):
    if request.method == "POST" and request.FILES.get('file'):
        file = request.FILES['file']
        wb = openpyxl.load_workbook(file)
        sheet = wb.active

        errors = []  # Liste des erreurs d'importation

        for row in sheet.iter_rows(min_row=2, values_only=True):
            try:
                student, created = Student.objects.get_or_create(
                    ident_perm=row[1],
                    defaults={
                        'nom': row[2],
                        'prenom': row[3],
                        'date_naissance': clean_date(row[4]),
                        'lieu_naissance': row[5],
                        'filiere': row[7],
                        'niveau': row[8],
                        'classe': row[9],
                        'elite_id': row[10],
                        'status': row[11],
                        'sexe': row[12],
                        'contact': row[13],
                        'photo': row[14],
                        'etablissement': row[15]
                    }
                )
            except ValueError as e:
                errors.append(f"Erreur avec {row[2]} {row[3]}: {e}")

        if errors:
            messages.error(request, "Certaines lignes n'ont pas été importées. Vérifiez le format des données.")
        else:
            messages.success(request, "Importation réussie !")

        return redirect('student_list')

    return render(request, 'gestion_academique/djabou/upload.html')


# Vue pour afficher la liste des étudiants
def student_list(request):
    students = Student.objects.all()
    return render(request, 'gestion_academique/djabou/student_list.html', {'students': students})

# Vue pour afficher les détails d'un étudiant
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'gestion_academique/djabou/student_detail.html', {'student': student})

# Vue pour imprimer les étudiants créés aujourd'hui
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Student
import datetime

class StudentListView(ListView):
    model = Student
    template_name = 'gestion_academique/djabou/print_students.html'
    context_object_name = 'students'
    #paginate_by = 100
    ordering = ['nom', 'prenom']

    # def get_queryset(self):
    #     today = datetime.date.today()
    #     return Student.objects.all().order_by(*self.ordering)


########### Diplome Info edit
from .forms import DiplomeForm
class DiplomeUpdateView(UpdateView):
    model = Diplome
    form_class = DiplomeForm
    template_name = 'diplomes/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = "Mise à jour du Diplôme"
        context['info'] = "Modifiez les informations du diplôme ci-dessous."
        context['info2'] = "Mise à jour des données"
        context['diplome'] = self.object  # Pass the current Diplome instance
        return context

    def form_valid(self, form):
        messages.success(self.request, "Diplome mis à jour avec succès !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la mise à jour du diplome. Veuillez vérifier les informations fournies.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('session_detail', kwargs={'pk': self.object.pk})
