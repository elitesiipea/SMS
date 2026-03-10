from datetime import date
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime, now
from decorators.decorators import staff_required
from gestion_academique.models import AnneeAcademique, Classe, Niveau
from enseignant.models import Enseignant, ContratEnseignant
from inscription.models import Inscription
from medicale.models import Consultation
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DemoRequestForm
from .services import send_demo_request_emails


@login_required
@staff_required
def home(request):
    """
    Vue principale pour afficher le tableau de bord de l'administration.
    Fournit des statistiques sur les étudiants, enseignants, consultations, et scolarités.
    """
    user = request.user
    etablissement = getattr(user, "etablissement", None)

    # 1) Si l'utilisateur n'a pas d'établissement associé, on renvoie un dashboard "vide"
    if etablissement is None:
        context = {
            "titre": f"{user}",
            "info": "Accueil",
            "info2": "Tableau de Bord",
            "chart": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "etudiants": 0,
            "attentes": 0,
            "universitaires": 0,
            "professionnels": 0,
            "continue": 0,
            "online": 0,
            "enseignants": 0,
            "classes": 0,
            "scolarite_ouverte": 0,
            "scolarites_versees": 0,
            "scolarites_attendues": 0,
            "accomptes": [],
            "datatable": False,
            "niveaux": [],
            "consultations": [],
            "inscriptions_du_jour": 0,
            "no_etablissement": True,  # flag que tu peux exploiter dans le template
        }
        return render(request, "administration/uses/index.html", context=context)

    etablissement_id = etablissement.id

    # 2) Années académiques de l'établissement
    annees_academiques = (
        AnneeAcademique.objects.filter(etablissement_id=etablissement_id)
        .order_by("created")
    )
    last_year = annees_academiques.last()  # peut être None
    selected_annee_id = request.GET.get("annee_id")

    # 3) Détermination de l'année académique "active" (sélectionnée ou dernière par défaut)
    selected_annee = None
    if selected_annee_id:
        try:
            selected_annee = annees_academiques.get(id=selected_annee_id)
        except AnneeAcademique.DoesNotExist:
            selected_annee = last_year
    else:
        selected_annee = last_year

    # 4) Consultations futures pour l'établissement
    consultations = Consultation.objects.filter(
        annee_academique__etablissement_id=etablissement_id,
        rendez_vous__gte=date.today(),
    )

    # 5) Étudiants et inscriptions
    etudiants_qs = Inscription.objects.filter(
        annee_academique__etablissement_id=etablissement_id,
        confirmed=True,
    )
    attentes_qs = Inscription.objects.filter(
        annee_academique__etablissement_id=etablissement_id,
        confirmed=False,
    )

    # 6) Classes & acomptes
    classes_qs = Classe.objects.filter(
        annee_academique__etablissement_id=etablissement_id
    )
    accomptes_qs = ContratEnseignant.objects.filter(
        enseignant__etablissement_id=etablissement_id,
        demande_accompte=True,
        demande_traitee=False,
    )

    # 7) Niveaux
    niveaux = Niveau.objects.filter(etablissement_id=etablissement_id)

    # 8) Application du filtre par année académique (si disponible)
    if selected_annee is not None:
        etudiants_qs = etudiants_qs.filter(annee_academique=selected_annee)
        attentes_qs = attentes_qs.filter(annee_academique=selected_annee)
        classes_count = classes_qs.filter(annee_academique=selected_annee).count()
        # On suppose que ContratEnseignant possède un champ annee_academique
        accomptes_qs = accomptes_qs.filter(annee_academique=selected_annee)
    else:
        # Pas encore d'année académique : tout est à zéro côté stats
        classes_count = 0
        etudiants_qs = etudiants_qs.none()
        attentes_qs = attentes_qs.none()
        accomptes_qs = accomptes_qs.none()

    # 9) Nombre d'enseignants
    enseignants_count = Enseignant.objects.filter(
        etablissement_id=etablissement_id
    ).count()

    # 10) Inscriptions du jour (en heure locale)
    current_time = localtime(now())
    start_of_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)

    inscriptions_du_jour = (
        Inscription.objects.filter(
            annee_academique__etablissement_id=etablissement_id,
            confirmed=True,
            created__range=(start_of_day, end_of_day),
        ).count()
    )

    # 11) Statistiques scolarité sur le queryset d'étudiants filtré
    # On protège contre les valeurs nulles avec "or 0"
    scolarite_ouverte = sum((item.frais or 0) for item in etudiants_qs)
    scolarites_versees = sum((item.paye or 0) for item in etudiants_qs)
    scolarites_attendues = sum((item.reste or 0) for item in etudiants_qs)

    # 12) Découpage par parcours
    universitaires_count = etudiants_qs.filter(
        parcour__exact="CYCLE UNIVERSITAIRE"
    ).count()
    professionnels_count = etudiants_qs.filter(
        parcour__exact="CYCLE PROFESSIONNEL JOUR"
    ).count()
    continue_count = etudiants_qs.filter(
        parcour__exact="CYCLE PROFESSIONNEL SOIR"
    ).count()
    online_count = etudiants_qs.filter(parcour__exact="CYCLE EN LIGNE").count()

    # 13) Construction du contexte
    context = {
        "titre": f"{user}",
        "info": "Accueil",
        "info2": "Tableau de Bord",
        "chart": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "etudiants": etudiants_qs.count(),
        "attentes": attentes_qs.count(),
        "universitaires": universitaires_count,
        "professionnels": professionnels_count,
        "continue": continue_count,
        "online": online_count,
        "enseignants": enseignants_count,
        "classes": classes_count,
        "scolarite_ouverte": scolarite_ouverte,
        "scolarites_versees": scolarites_versees,
        "scolarites_attendues": scolarites_attendues,
        "accomptes": accomptes_qs,
        "datatable": True,
        "niveaux": niveaux,
        "consultations": consultations,
        "inscriptions_du_jour": inscriptions_du_jour,
        "selected_annee": selected_annee,
    }

    return render(request, "administration/uses/index.html", context=context)


def sms_landing_view(request):
    """
    Landing page one-page pour présenter SMS + formulaire de demande de démo.
    """
    if request.method == "POST":
        form = DemoRequestForm(request.POST)
        if form.is_valid():
            demo = form.save()
            send_demo_request_emails(demo)
            messages.success(
                request,
                "Merci ! Votre demande de démo a bien été envoyée. "
                "Vous recevrez un e-mail de confirmation dans quelques instants.",
            )
            return redirect("sms-landing")
    else:
        form = DemoRequestForm()

    return render(request, "landing.html", {"form": form})

