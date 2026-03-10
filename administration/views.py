from django.shortcuts import render
from decorators.decorators import staff_required
from django.contrib.auth.decorators import login_required
# Create your views here.
from gestion_academique.models import *
from enseignant.models import *
from etudiants.models import *
from inscription.models import *
from medicale.models import Consultation
from datetime import date
from django.utils.timezone import localtime, now

@login_required
@staff_required
def home(request):
    etablissement_id = request.user.etablissement.id
    last_year = request.user.etablissement.annee_academiques.last()
    selected_annee_id = request.GET.get('annee_id')
    consultations = Consultation.objects.filter(annee_academique__etablissement_id=etablissement_id, rendez_vous__gte=date.today())
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=etablissement_id).order_by('created')
    etudiants = Inscription.objects.filter(annee_academique__etablissement_id=etablissement_id,confirmed=True)
    attentes = Inscription.objects.filter(annee_academique__etablissement_id=etablissement_id,confirmed=False)
    enseignants = Enseignant.objects.filter(etablissement_id=etablissement_id).count()
    classes = Classe.objects.filter(annee_academique__etablissement_id=etablissement_id)
    accomptes = ContratEnseignant.objects.filter(enseignant__etablissement_id=etablissement_id,demande_accompte=True, demande_traitee=False)
    niveaux = Niveau.objects.filter(etablissement_id=etablissement_id)
    

    if selected_annee_id:

        etudiants = etudiants.filter(annee_academique_id=selected_annee_id)
        attentes = attentes.filter(annee_academique_id=selected_annee_id)
        classes = classes.filter(annee_academique_id=selected_annee_id).count()
        accomptes = accomptes.filter(annee_academique_id=selected_annee_id)

    else:

        etudiants = etudiants.filter(annee_academique_id=last_year)
        attentes = attentes.filter(annee_academique_id=last_year)
        classes = classes.filter(annee_academique_id=last_year).count()
        accomptes = accomptes.filter(annee_academique_id=last_year)
        
    
    start_of_day = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = localtime(now()).replace(hour=23, minute=59, second=59, microsecond=999999)

    # Filtrer les inscriptions du jour en fonction du fuseau horaire local
    inscriptions_du_jour = Inscription.objects.filter(
        annee_academique__etablissement_id=etablissement_id,
        confirmed=True,
        created__range=(start_of_day, end_of_day)
    ).count()

    context = {
        "titre" : f"{request.user}",
        "info": "Accueil",
        "info2" : "Tableau de Bord",
        "chart" : True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        'etudiants' : etudiants.count(),
        'attentes' : attentes.count(),
        'universitaires' : etudiants.filter(parcour__exact="CYCLE UNIVERSITAIRE").count(),
        'professionnels' : etudiants.filter(parcour__exact="CYCLE PROFESSIONNEL JOUR").count(),
        'continue' : etudiants.filter(parcour__exact="CYCLE PROFESSIONNEL SOIR").count(),
        'online' : etudiants.filter(parcour__exact="CYCLE EN LIGNE").count(),
        'enseignants': enseignants,
        'classes' : classes,
        'scolarite_ouverte' : sum(item.frais for item in etudiants),
        'scolarites_versees' : sum(item.paye for item in etudiants),
        'scolarites_attendues' : sum(item.reste for item in etudiants),
        'accomptes' : accomptes,
        "datatable": True,
        "niveaux" : niveaux,
        "consultations" : consultations,
        "inscriptions_du_jour" : inscriptions_du_jour,
    }
    
    return render(request, 'administration/uses/index.html', context=context)

