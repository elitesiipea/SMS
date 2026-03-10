from django.shortcuts import render, redirect,reverse

from gestion_academique.views import _get_user_etablissement
from .models import Inscription, Paiement
from etudiants.models import Etudiant
from .forms import InscriptionForm
from decorators.decorators import staff_required ,student_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from etudiants.models import Etudiant
from gestion_academique.models import AnneeAcademique
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
import hashlib
import hmac
import requests
import json
from django.http import HttpResponseNotFound
import datetime


@login_required
@staff_required
def inscription_create(request, slug):
    if request.method == 'POST':
        form = InscriptionForm(request.user.etablissement.id, request.POST)
        if form.is_valid():
            etudiant = Etudiant.objects.get(code_paiement=slug)
            annee_academique = request.user.etablissement.annee_academiques.order_by('-created').first()

            # Vérifier si une inscription avec les mêmes caractéristiques existe déjà
            existing_inscription = Inscription.objects.filter(etudiant=etudiant, annee_academique=annee_academique).first()

            if existing_inscription:
                messages.error(request, f'Une inscription pour la dernière année académique avec les mêmes caractéristiques existe déjà.')
            else:
                inscription = form.save(commit=False)
                inscription.etudiant = etudiant
                inscription.annee_academique = annee_academique
                inscription.save()
                messages.success(request, f'Pré-inscription de {inscription.etudiant} effectuée avec succès!')
                return redirect(reverse('etudiant_profile', kwargs={'pk': inscription.etudiant.pk}))  # Remplacez 'success_page' par le nom d'URL de la page de succès.
        else:
            print(form.errors)
    else:
        form = InscriptionForm(request.user.etablissement.id)

    try:
        etudiant = Etudiant.objects.get(code_paiement=slug)
        info2 = etudiant
    except Etudiant.DoesNotExist:
        etudiant = False
        info2 = "Dossier Introuvable"

    context = {
        "etudiant": etudiant,
        "titre": "Enregistrement du livre Académique",
        "info": "ADMISSION",
        "info2": info2,
        "datatable": False,
        'form': form
    }
    return render(request, 'inscription/inscription.html', context=context)


@login_required
@staff_required
def reinscription(request):
    if request.method == 'POST':
        code_paiement = request.POST.get('code_paiement', None)
        if code_paiement:
            try:
                etudiant = Etudiant.objects.get(code_paiement=code_paiement)
                return redirect(reverse('inscription_create', kwargs={'slug': etudiant.code_paiement}))
            except Etudiant.DoesNotExist:
                messages.error(request, "Aucun étudiant trouvé avec ce code de paiement.")
        else:
            messages.error(request, "Veuillez saisir le code de paiement de l'étudiant.")

    context = {
        'titre': "Re-Inscription",
        'info': "Saisissez le code de paiement de l'étudiant",
        'info2': "",
        "datatable": False,
    }

    return render(request, 'inscription/reinscription.html', context)



@login_required
@staff_required
def student_inscription_list(request,slug):
    etudiant = Etudiant.objects.get(code_paiement=slug)
    scolarites = Inscription.objects.filter(etudiant__code_paiement=slug)
    context = {
        'etudiant' : etudiant,
        'scolarites' : scolarites,
        "titre" : "Historique des Scolarités de l'étudiant",
        "info": etudiant,
        "info2" : "Historique des Scolarités de l'étudiant",
        "datatable": True,
    }
    return render(request, 'inscription/inscription_liste.html', context=context)



@login_required
@staff_required
def student_list_ministere(request):
    selected_annee_id = request.GET.get('annee_id')
    
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    scolarites = Inscription.objects.filter(etudiant__etablissement_id=request.user.etablissement.id).order_by('filiere','niveau','etudiant__nom',)

    if selected_annee_id:
        
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
        
    else:
        scolarites = scolarites.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())

    context = {
        'scolarites' : scolarites,
        "titre" : f"Liste des Scolarités {request.user.etablissement}",
        "info": "Liste des Scolarités",
        "info2" : "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'inscription/ministere.html', context=context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Inscription, Paiement
from .forms import PaiementForm2
from django.utils import timezone


def home(request):
    return render(request, 'inscription/home.html', {
        'titre': "Accueil",
    })

@login_required
@staff_required
def student_inscription_details(request, pk):
    scolarite = get_object_or_404(Inscription, pk=pk)
    paiements = scolarite.inscription_paiement.filter(confirmed=True).order_by('created')
    
    # Si un paiement est édité
    if request.method == 'POST':
        paiement_id = request.POST.get('paiement_id')
        paiement = get_object_or_404(Paiement, id=paiement_id)
        
        # Récupérer les données soumises et formater l'heure
        reference = request.POST.get('reference')
        montant = request.POST.get('montant')
        source = request.POST.get('source')
        effectue_par = request.POST.get('effectue_par')
        active = 'active' in request.POST  # Si le champ est coché, active=True
        
        created = request.POST.get('created')
        
        # Si une valeur a été fournie pour 'created', la convertir en datetime
        if created:
            created_datetime = timezone.datetime.strptime(created, '%Y-%m-%dT%H:%M')
        else:
            created_datetime = paiement.created  # Laisser l'heure inchangée si non modifiée

        # Mettre à jour l'objet paiement
        paiement.reference = reference
       
        paiement.source = source
        paiement.effectue_par = effectue_par
        paiement.active = active
        paiement.created = created_datetime  # Mettre à jour la date et l'heure
        paiement.save()
        
        # Rediriger vers la même page
        return redirect(request.path)  # Cela redirige vers la même URL
    
    context = {
        'scolarite': scolarite,
        'titre': "Détail Scolarité",
        'info': "Détail Scolarité",
        'info2': scolarite,
        'datatable': False,
        'etudiant': scolarite.etudiant,
        'paiements': paiements,
    }
    
    return render(request, 'inscription/inscription_details.html', context=context)


def recu_djabou(request, pk):
    scolarite = get_object_or_404(Inscription, pk=pk)
    paiements = scolarite.inscription_paiement.filter(confirmed=True).order_by('created')
    
    # Si un paiement est édité
    if request.method == 'POST':
        paiement_id = request.POST.get('paiement_id')
        paiement = get_object_or_404(Paiement, id=paiement_id)
        
        # Récupérer les données soumises et formater l'heure
        reference = request.POST.get('reference')
        montant = request.POST.get('montant')
        source = request.POST.get('source')
        effectue_par = request.POST.get('effectue_par')
        active = 'active' in request.POST  # Si le champ est coché, active=True
        
        created = request.POST.get('created')
        
        # Si une valeur a été fournie pour 'created', la convertir en datetime
        if created:
            created_datetime = timezone.datetime.strptime(created, '%Y-%m-%dT%H:%M')
        else:
            created_datetime = paiement.created  # Laisser l'heure inchangée si non modifiée

        # Mettre à jour l'objet paiement
        paiement.reference = reference
       
        paiement.source = source
        paiement.effectue_par = effectue_par
        paiement.active = active
        paiement.created = created_datetime  # Mettre à jour la date et l'heure
        paiement.save()
        
        # Rediriger vers la même page
        return redirect(request.path)  # Cela redirige vers la même URL
    
    context = {
        'scolarite': scolarite,
        'titre': "Détail Scolarité",
        'info': "Détail Scolarité",
        'info2': scolarite,
        'datatable': False,
        'etudiant': scolarite.etudiant,
        'paiements': paiements,
    }
    
    return render(request, 'inscription/recu_djabou.html', context=context)

@login_required
@staff_required
def all_student_inscription_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "scolarites": [],
            "titre": "Liste des Scolarités",
            "info": "Liste des Scolarités",
            "info2": "Liste des Scolarités",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "inscription/all_inscrit.html", context=context)

    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    scolarites = Inscription.objects.filter(
        etudiant__etablissement_id=etablissement.id
    ).order_by("filiere", "niveau", "etudiant__nom")

    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
    else:
        last_annee = etablissement.annee_academiques.order_by("created").last()
        if last_annee:
            scolarites = scolarites.filter(annee_academique_id=last_annee.id)

    context = {
        "scolarites": scolarites,
        "titre": f"Liste des Scolarités {etablissement}",
        "info": "Liste des Scolarités",
        "info2": "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "no_etablissement": False,
    }
    return render(request, "inscription/all_inscrit.html", context=context)

@login_required
@staff_required
def carte_print_details(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "scolarites": [],
            "titre": "Cartes étudiants",
            "info": "Liste des Scolarités",
            "info2": "Liste des Scolarités",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "inscription/carte_print.html", context=context)

    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    scolarites = Inscription.objects.filter(
        etudiant__etablissement_id=etablissement.id
    )

    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
    else:
        last_annee = etablissement.annee_academiques.order_by("created").last()
        if last_annee:
            scolarites = scolarites.filter(annee_academique_id=last_annee.id)

    context = {
        "scolarites": scolarites,
        "titre": f"Liste des Scolarités {etablissement}",
        "info": "Liste des Scolarités",
        "info2": "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "no_etablissement": False,
    }
    return render(request, "inscription/carte_print.html", context=context)

@login_required
@staff_required
def all_student_inscription_list_attentes(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "scolarites": [],
            "titre": "Inscriptions en attente",
            "info": "Inscriptions en Attentes",
            "info2": "Inscriptions en Attentes",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "inscription/all_inscrit_attentes.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    scolarites = Inscription.objects.filter(
        etudiant__etablissement_id=etablissement.id, confirmed=False
    )

    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
    else:
        last_annee = etablissement.annee_academiques.order_by("created").last()
        if last_annee:
            scolarites = scolarites.filter(annee_academique_id=last_annee.id)

    context = {
        "scolarites": scolarites,
        "titre": f"Liste des Inscriptions en Attentes {etablissement}",
        "info": "Inscriptions en Attentes",
        "info2": "Inscriptions en Attentes",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "no_etablissement": False,
    }
    return render(
        request, "inscription/all_inscrit_attentes.html", context=context
    )

@login_required
@staff_required
def scolarite_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "scolarites": [],
            "titre": "Liste des Scolarités",
            "info": "Liste des Scolarités",
            "info2": "Liste des Scolarités",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "inscription/list_scolarite.html", context=context)

    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    scolarites = (
        Inscription.objects.filter(
            etudiant__etablissement_id=etablissement.id
        )
        .select_related("etudiant", "filiere", "niveau", "classe", "annee_academique")
        .order_by("filiere__nom", "niveau__nom", "etudiant__nom")
    )

    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
    else:
        last_annee = etablissement.annee_academiques.order_by("created").last()
        if last_annee:
            scolarites = scolarites.filter(annee_academique_id=last_annee.id)

    context = {
        "scolarites": scolarites,
        "titre": f"Liste des Scolarités {etablissement}",
        "info": "Liste des Scolarités",
        "info2": "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "no_etablissement": False,
    }
    return render(request, "inscription/list_scolarite.html", context=context)

@login_required
@staff_required
def paiement_historique_list(request):
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "paiements": [],
            "titre": "Historique des paiements",
            "info": "Historique des paiements",
            "info2": "Historique des paiements",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(
            request, "inscription/paiements/historique.html", context=context
        )

    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    paiements = Paiement.objects.filter(
        inscription__etudiant__etablissement_id=etablissement.id,
        confirmed=True,
    ).select_related("inscription", "inscription__etudiant")

    if selected_annee_id:
        paiements = paiements.filter(
            inscription__annee_academique_id=selected_annee_id
        )
    else:
        last_annee = etablissement.annee_academiques.order_by("created").last()
        if last_annee:
            paiements = paiements.filter(
                inscription__annee_academique_id=last_annee.id
            )

    context = {
        "paiements": paiements,
        "titre": f"Historique des paiements {etablissement}",
        "info": "Historique des paiements",
        "info2": "Historique des paiements",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "no_etablissement": False,
    }
    return render(
        request, "inscription/paiements/historique.html", context=context
    )




@login_required
@staff_required
def remise_kits(request):
    if request.method == 'POST':
        code_paiement = request.POST.get('code_paiement', None)
        if code_paiement:
            try:
                etudiant = Etudiant.objects.get(code_paiement=code_paiement)
                return redirect(reverse('student_kits_list', kwargs={'slug': etudiant.code_paiement}))
            except Etudiant.DoesNotExist:
                messages.error(request, "Aucun étudiant trouvé avec ce code de paiement.")
        else:
            messages.error(request, "Veuillez saisir le code de paiement de l'étudiant à réinscrire.")

    context = {
        'titre': "Réinscription",
        'info': "Saisissez le code de paiement de l'étudiant à réinscrire",
        'info2': "",
        "datatable": False,
    }

    return render(request, 'inscription/kits/remise_kits.html', context)



@login_required
@staff_required
def student_kits_list(request,slug):
    etudiant = Etudiant.objects.get(code_paiement=slug)
    scolarites = Inscription.objects.filter(etudiant__code_paiement=slug).order_by('-created')
    context = {
        'etudiant' : etudiant,
        'scolarites' : scolarites,
        "titre" : "Remise de Kits & Accéssoires",
        "info": etudiant,
        "info2" : "Remise de Kits & Accéssoires",
        "datatable": True,
        'remise_kits' : True
    }
    return render(request, 'inscription/kits/inscriptions_kits.html', context=context)


@login_required
@staff_required
def get_scolarite_info(request):
    scolarite_pk = request.GET.get('scolarite_pk')
    
    if scolarite_pk:
        scolarite = Inscription.objects.get(pk=scolarite_pk)
        data = {
            "code" : scolarite.etudiant.code_paiement,
            "filiere" : scolarite.filiere.nom,
            "niveau" : scolarite.niveau.nom,
            "classe" : scolarite.classe.nom,
            "frais" : scolarite.frais,
            "paye" : scolarite.paye,
            "etudiant" : scolarite.etudiant.nom + " " + scolarite.etudiant.prenom,
            "scolarite_id" : scolarite.pk,
            "photo" : str(scolarite.etudiant.photo.url),
        }
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'scolarite non trouvé.'}, status=400)

@login_required
@staff_required
@require_POST
def validate_remise_kits(request):
    scolarite_id = request.POST.get('scolarite_id')
    elements = ['macaron', 'cravate', 'tissu', 'rame', 'marqueur', 'polo']

    if scolarite_id:
        scolarite = get_object_or_404(Inscription, pk=scolarite_id)
        
        for element in elements:
            if not getattr(scolarite, element):
                setattr(scolarite, element, request.POST.get(element) == 'on')
        
        scolarite.save()
        messages.success(request, "Remise de Kits & Accessoires effectuée avec succès !")
    else:
        messages.error(request, "Une erreur est survenue lors de la remise")

    return redirect(reverse('student_kits_list', kwargs={'slug': scolarite.etudiant.code_paiement}))



@login_required
@staff_required
def all_student_kits_list(request):
    # 1) Récupération de l'établissement de l'utilisateur
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "scolarites": [],
            "titre": "Emission des Kits & Accéssoires",
            "info": "Emission des Kits & Accéssoires",
            "info2": "Emission des Kits & Accéssoires",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "inscription/kits/all_kits.html", context=context)

    # 2) Gestion de l'année académique
    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    annee_active = None
    if selected_annee_id:
        annee_active = annees_academiques.filter(id=selected_annee_id).first()

    if annee_active is None:
        annee_active = annees_academiques.first()

    # 3) Récupération des inscriptions (scolarités) de l'établissement
    scolarites = (
        Inscription.objects
        .filter(etudiant__etablissement_id=etablissement.id)
    )
    if annee_active:
        scolarites = scolarites.filter(annee_academique_id=annee_active.id)

    # 4) Contexte
    context = {
        "scolarites": scolarites,
        "titre": f"Emission des Kits & Accéssoires {etablissement}",
        "info": "Emission des Kits & Accéssoires",
        "info2": "Emission des Kits & Accéssoires",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "annee_active": annee_active,
        "no_etablissement": False,
    }

    return render(request, "inscription/kits/all_kits.html", context=context)

@login_required
@staff_required
def nouveau_paiement(request):
    if request.method == 'POST':
        code_paiement = request.POST.get('code_paiement', None)
        if code_paiement:
            try:
                etudiant = Etudiant.objects.get(code_paiement=code_paiement)
                return redirect(reverse('student_scolarite_list', kwargs={'slug': etudiant.code_paiement}))
            except Etudiant.DoesNotExist:
                messages.error(request, "Aucun étudiant trouvé avec ce code de paiement.")
        else:
            messages.error(request, "Veuillez saisir le code de paiement de l'étudiant.")

    context = {
        'titre': "Nouveau Paiement",
        'info': "Saisissez le code de paiement de l'étudiant",
        'info2': "",
        "datatable": False,
    }

    return render(request, 'inscription/paiements/new.html', context)



###############################################################################
###############################################################################
@login_required
@staff_required
def student_scolarite_list(request, slug):
    try:
        etudiant = get_object_or_404(Etudiant, code_paiement=slug)
        scolarites = Inscription.objects.filter(etudiant__code_paiement=slug).order_by('-created')
    except Exception as e:
        messages.error(request, "Erreur lors du chargement des données de l'étudiant : {e}.")
        return redirect('student_inscription_details', pk=scolarite.id)

    if request.method == 'POST':
        try:
            scolarite_id = request.POST.get('scolarite_id')
            montant = int(request.POST.get('montant', 0))
            source = request.POST.get('source', '').strip()
            reference = request.POST.get('reference', '').strip()

            # Validation des entrées
            if not scolarite_id or not montant or not source or not reference:
                messages.error(request, "Tous les champs sont requis.")
                return redirect(request.path)

            scolarite = get_object_or_404(Inscription, id=scolarite_id)

            # Vérifier si un paiement avec la même référence existe déjà
            existing_paiement = Paiement.objects.filter(
                Q(inscription=scolarite) & Q(reference=reference)
            ).exists()

            if existing_paiement:
                messages.error(request, "Un paiement avec la même référence existe déjà.")
            else:
                reste_a_payer = scolarite.reste

                if montant <= 0:
                    messages.error(request, "Le montant doit être supérieur à zéro.")
                elif montant > reste_a_payer:
                    messages.error(request, f"Montant supérieur. Il reste {reste_a_payer} Francs à payer.")
                else:
                    non_direct_api = True if source == "WAVE MONEY" else False

                    Paiement.objects.create(
                        inscription=scolarite,
                        montant=montant,
                        source=source,
                        reference=reference,
                        confirmed=True,
                        effectue_par=request.user,
                        non_wave_direct_api=non_direct_api
                    )

                    messages.success(request, "Paiement enregistré avec succès !!")
                    return redirect('student_inscription_details', pk=scolarite.id)

        except ValueError:
            messages.error(request, "Veuillez entrer un montant valide.")
        except Exception as e:
            messages.error(request, "Une erreur s'est produite lors de l'enregistrement du paiement: {e}.")

    context = {
        'etudiant': etudiant,
        'scolarites': scolarites,
        "titre": "Nouveau Paiement",
        "info": etudiant,
        "info2": "Nouveau Paiement",
        "datatable": True,
        'remise_kits': True
    }
    return render(request, 'inscription/paiements/list.html', context=context)

###############################################################################
##############                API ET MOBILE PAYEMENT          #################
##############                API ET MOBILE PAYEMENT          #################
##############                API ET MOBILE PAYEMENT          #################
###############################################################################

###############################################################################
###############################################################################

################################ WAVE MONEY ##################################
@login_required
@student_required
def payment_processing_view(request):
    if request.method == 'POST':
        # Retrieve form data
        scolarite_id = int(request.POST.get('scolarite_id'))
        montant_id = int(request.POST.get('current-log-email'))
        phone = request.POST.get('phone')
        network = request.POST.get('operateur_id')
        # Print the form data (for demonstration purposes)
        print("Scolarite ID:", scolarite_id)
        print("Montant ID:", montant_id)
        print("Phone:", phone)
        print("Network:", network)

        paiement = Paiement.objects.create(inscription_id=scolarite_id, montant=montant_id,source=network, reference=phone)
        paiement.save()
        # Redirect to a URL with the generated ID as a parameter
        return redirect('PaiementCreateDetails', pk=paiement.pk)

    return HttpResponse("Method not allowed", status=405)


def PaiementCreateDetails(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    context = {
        'scolarite' : paiement.inscription,
        'paiement' : paiement,
        'hide' : True,
        'montant_total' : int(paiement.montant / 0.99)  # Montant à payer incluant les frais de 1%
    }
    return render(request,'etudiants/dashboard/uses/fees_confirmation.html', context=context)


SECRET = "WH_6zuoo71Sw2Lj"

def verify_webhook_signature(request, body):
    wave_signature = request.headers.get('Wave-Signature')
    
    if not wave_signature:
        return False
    
    timestamp, signature = wave_signature.split(',', 1)
    
    expected_signature = hmac.new(
        bytes(SECRET, 'utf-8'),
        msg=bytes(f"{timestamp}.{body}", 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def success_view1(request):
    # Vous pouvez inclure une logique ici si nécessaire
    return JsonResponse({'path': 'Paiement IIPEA'}, status=200)

def success_view2(request):
    # Vous pouvez inclure une logique ici si nécessaire
    return JsonResponse({'path': 'Paiement  iipeaci * intouch'}, status=200)

def success_view3(request):
    # Vous pouvez inclure une logique ici si nécessaire
    return JsonResponse({'path': 'Paiement  iipeaci * outtouch'}, status=200)

def success_view4(request):
    # Vous pouvez inclure une logique ici si nécessaire
    return JsonResponse({'path': 'PAIEMENT IIPEA VERIFY'}, status=200)

@csrf_exempt
def webhook_handler(request):
    if request.method == 'POST':
        wave_signature = request.headers.get('Wave-Signature')
        request_body = request.body.decode('utf-8')
        if not wave_signature:
            return False
        timestamp, signature =  wave_signature.split(',', 1)
        expected_signature = hmac.new(bytes(SECRET, 'utf-8'),msg=bytes(f"{timestamp}.{request.body}", 'utf-8'),digestmod=hashlib.sha256).hexdigest()
        valide = hmac.compare_digest(signature, expected_signature)
        print(expected_signature)
        print(signature)
        print(valide)
        if valide:
            try:
                webhook_data = json.loads(request_body)
                event_type = webhook_data['type']
                if event_type == 'checkout.session.completed':
                    data = webhook_data['data']
                    amount = data['amount']
                    wave_id = data['id']
                    try:
                        fee = Paiement.objects.get(wave_id=wave_id, confirmed=False)
                        fee.confirmed = True
                        fee.save()
                    except:
                        return HttpResponse(status=400)
            except json.JSONDecodeError:
                return HttpResponse(status=400)
        return HttpResponse(status=200)
    return HttpResponse(status=400)

def waveMakePaiment(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    
    # Calcul du montant avec les frais de 1%
    montant_initial = paiement.montant
    montant_total = int(montant_initial / 0.99)  # Montant à payer incluant les frais de 1%

    data = {
        'amount': montant_total,  # Montant ajusté avec les frais
        'currency': 'XOF',
        'client_reference': "Etablissement {}. Année Academique {}- Id : {}".format(request.user.etablissement, paiement.inscription.annee_academique, str(paiement.id)),
        'success_url': 'https://myiipea.com' + paiement.success_url,
        'error_url': 'https://myiipea.com' + paiement.error_url,
    }

    base_url = "https://api.wave.com"
    post_url = base_url + "/v1/checkout/sessions"

    headers = {
        'Authorization': 'Bearer {}'.format(request.user.etablissement.wave_api_key),
        'Content-Type': 'application/json',
    }

    response = requests.post(post_url, json=data, headers=headers)  # Post data to create payment session

    print(response)

    if response.status_code == 200:
        response_data = response.json()
        # Update Paiement model with wave_launch_url and wave_id
        paiement.wave_launch_url = response_data.get('wave_launch_url')
        paiement.wave_id = response_data.get('id')
        paiement.effectue_par = request.user.nom + " " + request.user.prenom
        paiement.save()

        # Redirect the user to wave_launch_url
        return redirect(paiement.wave_launch_url)
    else:
        messages.error(request, "Une erreur est survenue lors du paiement !")
        return redirect('student_fees')



def wavesuccess(request,code,pk):
    fee = Paiement.objects.get(inscription__etudiant__code_paiement=code, pk=pk)
    if fee.confirmed:
        pass
    else:
        fee.confirmed = True
        fee.save()
    messages.success(request, "Paiement enregistré avec succès !")
    return redirect('student_fees')

def waveerror(request,code,pk):
    messages.error(request, "Une erreur est survenue lors qu paiement !")
    return redirect('student_fees')




def cancelPayment(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    paiement.delete()
    messages.success(request, "Paiement annulé avec succès !!")
    return redirect('student_fees')



################# Get Student Financial Data
def getStudentFee(request, code):
    fee = Inscription.objects.filter(etudiant__code_paiement=code).first()
    data = [
    {
            'etudiant': f"{fee.etudiant.nom} {fee.etudiant.prenom}",
            'id': fee.id,
            'filiere': fee.filiere.nom,
            'niveau': fee.niveau.nom,
            'frais': fee.frais,
            'paye': fee.paye,
            'reste': fee.reste,
            'annee_academique': f"{fee.annee_academique.debut}-{fee.annee_academique.fin}",
            'created': fee.created.strftime('%Y-%m-%d %H:%M:%S'),
            'date_update': fee.date_update.strftime('%Y-%m-%d %H:%M:%S')
    }
    ]
    return JsonResponse({'data': data })
   

##############Api"


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

class StudentFeeApiView(APIView):
    @swagger_auto_schema(
        operation_summary="Get Student Financial Data",
        operation_description="Retrieve student financial data.",
        responses={status.HTTP_200_OK: "List of student financial data"}
    )
    def get(self, request, code):
        fee = Inscription.objects.filter(etudiant__code_paiement=code).first()
        data = [
            {
                'etudiant': f"{fee.etudiant.nom} {fee.etudiant.prenom}",
                'id': fee.id,
                'filiere': fee.filiere.nom,
                'niveau': fee.niveau.nom,
                'frais': fee.frais,
                'paye': fee.paye,
                'reste': fee.reste,
                'annee_academique': f"{fee.annee_academique.debut}-{fee.annee_academique.fin}",
                'created': fee.created.strftime('%Y-%m-%d %H:%M:%S'),
                'date_update': fee.date_update.strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        return Response({'data': data }, status=status.HTTP_200_OK)


###############




secret = ['$a50l_puewiz4_i3&sp3fj6y@h^&)2%a$9e=32n_6h&w@2ux*f']

def get_inscription_data(inscription):
    return {
        'etudiant': f'{inscription.etudiant.nom} {inscription.etudiant.prenom}',
        'annee_academique': f'{inscription.annee_academique.debut} - {inscription.annee_academique.fin}',
        'filiere': inscription.filiere.nom,
        'niveau': inscription.niveau.nom,
        'classe': inscription.classe.nom,
        'parcour': inscription.parcour,
        'nature': inscription.nature,
        'frais': inscription.frais,
        'paye': inscription.paye,
        'reste': inscription.reste,
        'created': inscription.created.strftime('%Y-%m-%d %H:%M:%S'),
        'date_update': inscription.date_update.strftime('%Y-%m-%d %H:%M:%S'),
    }

@csrf_exempt
def common_api_view(request, action):
    pass


@csrf_exempt
def get_inscription_by_matricule(request):
    return common_api_view(request, 'get_inscription')

@csrf_exempt
def make_new_paiment_form_ecobank(request):
    return common_api_view(request, 'make_payment')

@login_required
@staff_required
def all_student_inscription_list_dossiers(request):
    etablissement = _get_user_etablissement(request)

    # Si l'utilisateur n'a pas d'établissement associé
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "scolarites": [],
            "titre": "Liste des Scolarités",
            "info": "Liste des Scolarités",
            "info2": "Liste des Scolarités",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "inscription/dossiers.html", context=context)

    selected_annee_id = request.GET.get("annee_id")

    # Années académiques de l'établissement
    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    # Base queryset des scolarités
    scolarites = Inscription.objects.filter(
        etudiant__etablissement_id=etablissement.id
    ).order_by("filiere", "niveau", "etudiant__nom")

    # Filtre par année académique
    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
        annee_active = AnneeAcademique.objects.filter(
            pk=selected_annee_id,
            etablissement=etablissement
        ).first()
    else:
        annee_active = etablissement.annee_academiques.order_by("created").last()
        if annee_active:
            scolarites = scolarites.filter(annee_academique=annee_active)

    context = {
        "scolarites": scolarites,
        "titre": f"Liste des Scolarités {etablissement}",
        "info": "Liste des Scolarités",
        "info2": "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "annee_active": annee_active,
        "no_etablissement": False,
    }
    return render(request, "inscription/dossiers.html", context=context)

@login_required
@staff_required
def scolarite_list_djabou(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    scolarites = Inscription.objects.filter(etudiant__etablissement_id=request.user.etablissement.id)
    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
    else:
        scolarites = scolarites.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())

    context = {
        'scolarites' : scolarites,
        "titre" : f"Liste des Scolarités {request.user.etablissement}",
        "info": "Liste des Scolarités",
        "info2" : "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,}
        
    return render(request, 'inscription/list_scolarite_djabou.html', context=context)


@login_required
@staff_required
def inscription_data_detail(request,pk, titre):
    inscription = get_object_or_404(Inscription, pk=pk)
    context = {
         "inscription" : inscription,
         'cursus': Inscription.objects.filter(etudiant_id=inscription.etudiant.id, confirmed=True),
         'titre': titre,   
         'student_print' : True,
         'hide':True
    }
    return render(request, 'inscription/documents/certificat_2.html', context=context)


@login_required
@staff_required
def emargement_list(request):
    etablissement = _get_user_etablissement(request)

    # Cas où le compte n’est pas rattaché à un établissement
    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation."
        )
        context = {
            "scolarites": [],
            "titre": "Liste des Scolarités",
            "info": "Liste des Scolarités",
            "info2": "Liste des Scolarités",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "inscription/emargement_list.html", context=context)

    selected_annee_id = request.GET.get("annee_id")

    # Années académiques de l’établissement
    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    # Base queryset des inscriptions
    scolarites = Inscription.objects.filter(
        etudiant__etablissement_id=etablissement.id
    ).order_by("filiere", "niveau", "etudiant__nom")

    # Filtre par année
    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
        annee_active = AnneeAcademique.objects.filter(
            pk=selected_annee_id,
            etablissement=etablissement
        ).first()
    else:
        annee_active = etablissement.annee_academiques.order_by("created").last()
        if annee_active:
            scolarites = scolarites.filter(annee_academique=annee_active)

    context = {
        "scolarites": scolarites,
        "titre": f"Liste des Scolarités {etablissement}",
        "info": "Liste des Scolarités",
        "info2": "Liste des Scolarités",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "annee_active": annee_active,
        "no_etablissement": False,
    }
    return render(request, "inscription/emargement_list.html", context=context)