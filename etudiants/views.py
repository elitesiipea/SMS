from __future__ import print_function
from django.shortcuts import render, redirect, reverse
from django.utils.text import slugify
from transport.models import Trajet, Abonnement, Paiement as Pcar
from authentication.models import User
from .models import Diplome, Etudiant, SessionSoutenanceNew, AttestationNew, SessionDiplome, CertificatSession, Certificat
from django.views.generic import ListView
from .forms import EtudiantForm, PasswordChangeCustomForm, EtudiantUpdateForm, ExcelUploadForm, SessionSoutenanceNewForm, SessionDiplomeNewForm, SessionCertificatNewForm
from decorators.decorators import staff_required, student_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from googleapiclient.discovery import build
from pathlib import Path
import os.path
from django.shortcuts import get_object_or_404
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from django.conf import settings
from gestion_academique.models import Maquette, AnneeAcademique, Classe, StudentMessage
from inscription.models import Inscription, Paiement
from enseignant.models import ContratEnseignant
from django.contrib.auth import update_session_auth_hash
from emplois_du_temps.models import Programme
from evaluations.models import Resultat
from medicale.models import DossierMedical
from bibliotheque.models import CategorieLivre, Livre
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

from .forms import StudentPhotoForm  # Import your StudentPhotoForm, SessionCertificatNewForm

import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import AttestationNew




local = False

# Function to create a G Suite account
def create_gsuite_account(email, nom, prenom):

    if local :

        lien = "C:/Users/Utilisateur/Documents/GitHub/SMS/SMS/etudiants/credentials.json"
        token_url = "C:/Users/Utilisateur/Documents/GitHub/SMS/SMS/etudiants/token.json"

    else:

        lien = "/home/daniel/SMS/SMS/etudiants/credentials.json"
        token_url = "/home/daniel/SMS/SMS/etudiants/token.json"

    SCOPES = ['https://www.googleapis.com/auth/admin.directory.user','https://www.googleapis.com/auth/admin.directory.group.member']

    creds = None

    if Path(token_url).exists():
        creds = Credentials.from_authorized_user_file(token_url, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(lien, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_url, "w") as token:
            token.write(creds.to_json())

    service = build('admin', 'directory_v1', credentials=creds)
    user_data = {
        'primaryEmail': email, 
        'name': {
            'familyName': nom,   # Replace with the student's last name
            'givenName': prenom,   # Replace with the student's first name
        },
        'password': '@elites@',  # Set a temporary password for the student
        'changePasswordAtNextLogin': True, 
    }

    try:
        user = service.users().insert(body=user_data).execute()
       

        # Add the user to the "student@iipea.com" group
        group_key = 'student@iipea.com'  # Replace with the correct group email
        member_key = user['primaryEmail']

        members = {
            "email": member_key
        }

        result = service.members().insert(groupKey=group_key, body=members).execute()
        
        

        return user

    except Exception as e:

        return None



#generation des mail et verification
def generate_unique_email(nom, premier_prenom):
    i = 1
    email = f'{premier_prenom}-{nom}@iipea.com'
    while User.objects.filter(email=email).exists():
        email = f"{slugify(nom)}-{slugify(premier_prenom)}{i}@iipea.com"
        i += 1
    return email


@login_required
@staff_required
def admission(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST,request.FILES)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            premier_prenom = prenom.split()[0]
            email = generate_unique_email(nom.lower(),premier_prenom.lower())
            password = "pbkdf2_sha256$260000$H157G58nYUDjbBTAZTSPbI$JGpbJlZ5pV9nB2lZGAc6jguEWKHJzagBEyG7D2rKZas="
            user = User.objects.create(email=email, 
                                            password=password, 
                                            nom=nom, prenom=prenom, 
                                            is_student=True,
                                            etablissement_id=request.user.etablissement.id
                                            )
            if user:
                gsuite_user = create_gsuite_account(user.email,user.nom, user.prenom.replace('-', ' ').split()[0])
                messages.success(request,'Profile G-suite ajouté avec succes !')
                # try:
                #     gsuite_user = create_gsuite_account(user.email,user.nom, user.prenom.replace('-', ' ').split()[0])
                #     messages.success(request,'Profile G-suite ajouté avec succes !')

                # except  Exception as e:
                #     # Handle other errors or exceptions
                #     messages.error(request, f'Profile G-suite non crée . Rasion : {e} !')
                   
            else:
                messages.error(request, 'Profile G-suite non ajouté!')

            etudiant = form.save(commit=False)
            etudiant.utilisateur = user
            etudiant.etablissement_id = request.user.etablissement.id
            etudiant.save()
            DossierMedical.objects.get_or_create(etudiant=etudiant)
            messages.success(request, 'Dossier créé avec succès , !')
            return redirect(reverse('inscription_create', kwargs={'slug': etudiant.code_paiement }))# Replace 'inscription page' with the URL name of the success page.
             
            
    else:
        form = EtudiantForm()
    context = {
      
        "titre" : "ADMISSION ETUDIANT",
        "info": "ADMISSION",
        "info2" : "ADMISSION ETUDIANT",
        "datatable": False,
        'form': form
    }
    return render(request, 'etudiants/admission/admission.html', context=context)


###############
# Impression des cartes d'étudiants
###############


@login_required
@staff_required
def liste_etudiants(request):
    context = {
        "titre" : "Liste des étudiants",
        "info": "Lites",
        "info2" : "Liste des étudiants",
        "etudiants": Etudiant.objects.filter(etablissement_id=request.user.etablissement.id),
        "datatable": True,
    }
    return render(request, 'etudiants/listes/list.html', context=context)


@login_required
@staff_required
def etudiant_profile(request,pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    context = {
        "titre" : etudiant,
        "info": "Profile Etudiant",
        "info2" : etudiant,
        "etudiant" : etudiant,
        "scolarites" : Inscription.objects.filter(etudiant=etudiant),
    }
    return render(request, 'etudiants/profiles/index.html', context=context)

####################### Dashbord 
@login_required
@student_required
def student_home(request):
    
    try:
            cursus = get_object_or_404(Inscription, etudiant_id=request.user.etudiant.id, annee_academique=AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id,  active=True).order_by('-created').first(),confirmed=True)
    except:
            cursus = None 
          
    context = {
        'titre' : 'Tableau de Bord',
        'home' : True,
        'cursus': cursus, 
        's_messages': StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created'),
    }
    return render(request,'etudiants/dashboard/uses/index.html', context=context)

############### Maquette

@login_required
@student_required
def student_maquette(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id,  active=True).order_by('created')
    maquettes = Maquette.objects.filter(etablissement_id=request.user.etablissement.id)

    if selected_annee_id:

        try:
            cursus = get_object_or_404(Inscription, etudiant_id=request.user.etudiant.id, annee_academique_id=selected_annee_id,confirmed=True)
            maquette = get_object_or_404(Maquette, annee_academique=cursus.annee_academique,filiere=cursus.filiere,niveau=cursus.niveau)
        except:
            cursus = None 
            maquette = None

        if cursus:
            found_cursus = True
        else:
            found_cursus = False
        if maquette:
            found_maquette = True
        else:
            found_maquette = False

    else:

        maquette = None
        found_maquette = None
        found_cursus = None
    
    context = {
        'titre' : 'Maquettes Pédagogique',
        'maquette' : maquette,
        'annees_academiques' : annees_academiques,
        'can_select_annee' : True,
        'found_cursus' : found_cursus,
        'found_maquette' :found_maquette,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/maquette.html', context=context)

############### Cours

@login_required
@student_required
def student_courses(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id,  active=True).order_by('created')
    if selected_annee_id:
        try:
            cursus = get_object_or_404(Inscription, etudiant_id=request.user.etudiant.id, annee_academique_id=selected_annee_id,confirmed=True)
            cours = ContratEnseignant.objects.filter(annee_academique=cursus.annee_academique,filiere=cursus.filiere,niveau=cursus.niveau)
            
        except:
            cursus = None 
            cours = None

        if cursus:
            found_cursus = True
        else:
            found_cursus = False
        if cours:
            found_cours = True
        else:
            found_cours = False

    else:

        cours = None
        found_cours = None
        found_cursus = None
        cursus = None
    
    context = {
        'titre' : 'Maquettes Pédagogique',
        'cours' : cours,
        'annees_academiques' : annees_academiques,
        'can_select_annee' : True,
        'found_cursus' : found_cursus,
        'found_cours' :found_cours,
        'cursus': cursus,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/courses.html', context=context)

############### Cours Details
@login_required
@student_required
def course_details(request,code,pk):
    cours = get_object_or_404(ContratEnseignant, enseignant__code=code, pk=pk)
    context = {
        'titre' : cours.matiere.nom,
        'cours' : cours,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/courses_detail.html', context=context)

############### Documents 

@login_required
@student_required
def student_certificat(request,name):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id,  active=True).order_by('created')
    datas = Inscription.objects.filter(etudiant_id=request.user.etudiant.id, confirmed=True)
    if selected_annee_id:
        try:
            cursus = get_object_or_404(Inscription, etudiant_id=request.user.etudiant.id, annee_academique_id=selected_annee_id,confirmed=True)
        except:
            cursus = None 

        if cursus:
            found_cursus = True
        else:
            found_cursus = False


    else:

        cursus = None
        found_cursus = None

        
    name = name
    context = {
        'titre' : f'Certificat {name} {request.user.etudiant}',
        'annees_academiques' : annees_academiques,
        'can_select_annee' : True,
        'found_cursus' : found_cursus,
        'cursus': cursus,
        'datas' :  datas,
        'student_print' : True,
        'name' : name.upper(),
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
        
    }
    return render(request,'etudiants/dashboard/uses/documents/certificat.html', context=context)

@login_required
@student_required
def student_times(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id,  active=True).order_by('created')
    if selected_annee_id:

        try:
            cursus = get_object_or_404(Inscription, etudiant_id=request.user.etudiant.id, annee_academique_id=selected_annee_id,confirmed=True)
            classe = get_object_or_404(Classe, pk=cursus.classe.pk)
            programmes = Programme.objects.filter(emplois_du_temps__classe=classe).order_by('date','debut','fin')
            
        except:
            cursus = None 
            classe = None
            programmes = None

        if cursus:
            found_cursus = True
        else:
            found_cursus = False
        if classe:
            found_classe = True
        else:
            found_classe = False

    else:

        classe = None
        programmes = None
        found_classe = None
        found_cursus = None

  
    context = {
        'titre' : "Emplois du Temps",
        'classe' : classe,
        'programmes' : programmes,
        'annees_academiques' : annees_academiques,
        'can_select_annee' : True,
        'found_cursus' : found_cursus,
        'found_classe' :found_classe,
        'jours_semaine' : ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE'],
       
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/times.html', context=context)



@login_required
@student_required
def student_notes(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id,  active=True).order_by('created')
    if selected_annee_id:

        try:
            cursus = get_object_or_404(Inscription, etudiant_id=request.user.etudiant.id, annee_academique_id=selected_annee_id,confirmed=True)
            classe = get_object_or_404(Classe, pk=cursus.classe.pk)
            notes = Resultat.objects.filter(note__classe=classe, etudiant=cursus)
            
        except:
            cursus = None 
            classe = None
            notes = None

        if cursus:
            found_cursus = True
        else:
            found_cursus = False
        if classe:
            found_classe = True
        else:
            found_classe = False

    else:

        classe = None
        notes = None
        found_classe = None
        found_cursus = None

  
    context = {
        'titre' : "Emplois du Temps",
        'classe' : classe,
        'notes' : notes,
        'annees_academiques' : annees_academiques,
        'can_select_annee' : True,
        'found_cursus' : found_cursus,
        'found_classe' :found_classe,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/notes.html', context=context)


@login_required
@student_required
def student_fees(request):
    scolarites = Inscription.objects.filter(etudiant=request.user.etudiant).order_by('-created')
    context = {
        'titre' : 'Ma Scolarité',
        'scolarites' : scolarites,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/fees.html', context=context)

@login_required
@student_required
def cartes(request):
    if request.method == 'POST':
        # Assuming you have a form to handle the photo update
        form = StudentPhotoForm(request.POST, request.FILES, instance=request.user.etudiant)
        if form.is_valid():
            request.user.etudiant.photo_updated = True
            form.save()
            messages.success(request, 'Photo modifiée avec succès.')
            
            return redirect('cartes')  # Redirect to the same page to display the success message
    else:
        form = StudentPhotoForm(instance=request.user.etudiant)

    scolarites = Inscription.objects.filter(etudiant=request.user.etudiant).order_by('-created')
    context = {
        'titre': 'Ma Scolarité',
        'scolarites': scolarites,
        's_messages': StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created'),
        'photo_form': form,
    }
    return render(request, 'etudiants/dashboard/uses/carte.html', context=context)

@login_required
@student_required
def student_fees_payment(request, code, pk):
    scolarite = get_object_or_404(Inscription, etudiant__code_paiement=code, pk=pk)
    context = {
        'titre' : 'Ma Scolarité',
        'scolarite' : scolarite,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/fees_payment.html', context=context)

class BookListView(ListView):
    model = Livre  # Modèle de données à utiliser
    context_object_name = 'livres'  # Nom de la variable de contexte pour les livres
    template_name = 'etudiants/dashboard/uses/book.html'  # Template à utiliser
    paginate_by = 12
    # Nombre de livres par page
    ordering = ['-created']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = 'Bibliothèque'
        context['s_messages'] = StudentMessage.objects.filter(etablissement_id=self.request.user.etablissement.id, active=True).order_by('-created')
        context['categories'] = CategorieLivre.objects.filter(active=True).order_by('nom')
        return context

############### Cours Details
@login_required
@student_required
def books_details(request,pk):
    
    livre = get_object_or_404(Livre,  pk=pk)
    context = {
        'livre' : livre,
    }
    return render(request,'etudiants/dashboard/uses/book_details.html', context=context)

@login_required
@student_required
def student_documents(request):
    context = {
        'titre' : 'Mes Documents',
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/documents.html', context=context)

@login_required
@student_required
def student_groupe(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id,  active=True).order_by('created')
    if selected_annee_id:

        try:
            cursus = get_object_or_404(Inscription, etudiant_id=request.user.etudiant.id, annee_academique_id=selected_annee_id,confirmed=True)
            classe = get_object_or_404(Classe, pk=cursus.classe.pk)
        except:
            cursus = None 
            classe = None

        if cursus:
            found_cursus = True
        else:
            found_cursus = False
        if classe:
            found_classe = True
        else:
            found_classe = False

    else:

        classe = None
        found_classe = None
        found_cursus = None
    
    context = {
        'titre' : "Groupe d'étude",
        'classe' : classe,
        'annees_academiques' : annees_academiques,
        'can_select_annee' : True,
        'found_cursus' : found_cursus,
        'found_classe' :found_classe,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/groupe.html', context=context)



@login_required
@student_required
def student_password(request):
    
    if request.method == "POST":
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Mot de passe modifié !")
            return redirect("student_password")

    else:
        form = PasswordChangeCustomForm(request.user)
    context = {
        'titre' : 'Modifier mes Accès',
        "form": form,
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/password.html', context=context)


@login_required
def student_profile(request):
    user = request.user

    if request.method == 'POST':
        form = EtudiantUpdateForm(request.POST, instance=user.etudiant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile mis à jour avec succes ! ')
            return redirect('student_profile')  # Redirect to the updated profile page
        messages.error(request, 'Une erreur est survenue lors de la mise à jour !')
        return redirect('student_profile')  # Redirect to the updated profile page
    else:
        form = EtudiantUpdateForm(instance=user.etudiant)

    context = {
        'titre': 'Mon Profile',
        's_messages': StudentMessage.objects.filter(etablissement_id=user.etablissement.id, active=True).order_by('-created'),
        'user': user,
        'form': form,
    }
    return render(request, 'etudiants/dashboard/uses/profile.html', context=context)

@login_required
@student_required
def student_contact(request):
    context = {
        'titre' : 'Contactez l"administration',
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/contact.html', context=context)


@login_required
@student_required
def payment_success(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)

    # Vérifier le statut du paiement via l'API Wave (exemple)
    # status_ok = make_payment_check(paiement)  # Vous devez implémenter cette fonction

    # Exemple de vérification du statut (vous devez l'adapter à votre API)
    # status_ok = check_payment_status_with_wave(paiement)
    status_ok = True
    if status_ok:
        paiement.confirmed = True
        paiement.save()
        messages.success(request, 'Paiement effectué avec succès !')
    else:
        messages.error(request, "Le Paiement n'a pas abouti merci de reessayer !.")

    return redirect("student_fees")

@login_required
@student_required
def payment_error(request):
    messages.error(request, 'Echec lors  de la tentative de Paiement !')
    return render(request,'etudiants/dashboard/uses/results/error.html')

    
@login_required
def carte_validated(request,pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    etudiant.carte_etudiant = True
    etudiant.save()
    messages.success(request, 'Carte remise avec succes')
    return redirect("liste_etudiants")


@login_required
@student_required
def student_transport(request):
    context = {
        'titre' : 'Cars & Transports',
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created')
    }
    return render(request,'etudiants/dashboard/uses/transport/transport.html', context=context)

@login_required
@student_required
def student_lignes(request):
    context = {
        'titre' : 'Lignes de Transports',
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created'),
        'lignes' : Trajet.objects.filter(active=True)
    }
    return render(request,'etudiants/dashboard/uses/transport/ligne.html', context=context)

@login_required
@student_required
def student_lignes_abonnement(request,pk):
    
    if Abonnement.objects.filter(trajet_id=pk, etudiant_id=request.user.etudiant.pk).exists():
            messages.error(request, 'Vous êtes déja abonné à cette Ligne !')
            return redirect('student_abonnements')
    else:
        Abonnement.objects.create(trajet_id=pk, etudiant_id=request.user.etudiant.pk)
        messages.success(request, 'Abonnement crée avec success !')
        return redirect('student_abonnements')

@login_required
@student_required
def student_abonnements(request):
    context = {
        'titre' : 'Mes Abonnements',
        's_messages' : StudentMessage.objects.filter(etablissement_id=request.user.etablissement.id, active=True).order_by('-created'),
        'abonnements' : Abonnement.objects.filter(etudiant=request.user.etudiant)
    }
    return render(request,'etudiants/dashboard/uses/transport/abonnements.html', context=context)




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

@login_required
@student_required
def waveMakePaimentForCar(request, pk):
    abonnement = Abonnement.objects.get(pk=pk)
    paiement = Pcar.objects.create(abonnement_id=pk, montant=abonnement.trajet.cout_mensuel, source="WAVE API")
    
    data = {
        'amount': int(paiement.montant),
        'currency': 'XOF',
        'client_reference': 'CAR-PAYMENT-RENEWB{}'.format(paiement.id),
        'success_url': 'https://myiipea.com' + paiement.success_url,
        'error_url': 'https://myiipea.com' + paiement.error_url,
    }

    base_url = "https://api.wave.com"
    post_url = base_url + "/v1/checkout/sessions"

    headers = {
        'Authorization': 'Bearer {}'.format(request.user.etablissement.wave_api_key),
        'Content-Type': 'application/json',
    }

    response = requests.post(post_url, json=data,headers=headers)  # Post data to create payment session

    print(response)
    
    if response.status_code == 200:
        response_data = response.json()
        # Update Paiement model with wave_launch_url and wave_id
        paiement.wave_launch_url = response_data.get('wave_launch_url')
        paiement.wave_id = response_data.get('id')
        paiement.save()

        # Redirect the user to wave_launch_url
        return redirect(paiement.wave_launch_url)
    else:
        messages.error(request, "Une erreur est survenue lors qu paiement !")
        return redirect('student_lignes')

def wavesuccessAbonnement(request,pk):
    paiement = Pcar.objects.get(pk=pk)
    paiement.confirmed = True
    print(paiement)
    paiement.save()
    messages.success(request, "Paiement enregistré avec succès !")
    return redirect('student_abonnements')

def waveerrorAbonnement(request):
    messages.error(request, "Une erreur est survenue lors qu paiement !")
    return redirect('student_abonnements')

def cancelPayment(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    paiement.delete()
    messages.success(request, "Paiement annulé avec succès !!")
    return redirect('student_fees')


########################## AttestationNew
@login_required
@staff_required
def attestation_list(request):
    context = {
        'attestations' :  AttestationNew.objects.all().order_by('nom'), 
         "titre": "Liste des attestations",
        "info": "Liste des attestations",
        "info2": "Liste des attestations",
        "datatable": True,
        
    }
    
    return render(request, 'etudiants/attestation/liste.html', context=context)

@login_required
@staff_required
def sessions_list(request):
    context = {
        'sessions' :  SessionSoutenanceNew.objects.filter(etablissement_id=request.user.etablissement.id).order_by('created'), 
         "titre": "Liste des Sessions",
        "info": "Liste des Sessions",
        "info2": "Liste des Sessions",
        "datatable": True,
        
    }
    
    return render(request, 'etudiants/sessions/listes.html', context=context)
    

@login_required
@staff_required
def create_attestations_from_excel(request):
    if request.method == 'POST':
        form = SessionSoutenanceNewForm(request.POST, request.FILES)
        if form.is_valid():
            session_soutenance = form.save(commit=False)
            session_soutenance.etablissement_id = request.user.etablissement.id
            session_soutenance.save()
            # Utiliser pandas pour lire le fichier Excel
            df = pd.read_excel(session_soutenance.fichier)

            # Créer une attestation pour chaque ligne dans le fichier Excel
            new_attestations = []
            for index, row in df.iterrows():
                attestation = AttestationNew.objects.create(
                    session=session_soutenance,
                    nom=row['NOM'],
                    prenom=row['PRENOMS'],
                    sexe=row['SEXE'],
                    matricule=row['MATRICULE'],
                    date_de_naissance=row['DATE_DE_NAISSANCE'],
                    lieu_de_naissance=row['LIEU_DE_NAISSANCE'],
                    pays=row['PAYS'],
                    filiere=row['FILIERE'],
                    cycle=row['CYCLE'],
                    niveau=row['NIVEAU'],
                    annee_academique=row['ANNEE_ACADEMIQUE'],
                )

            # Rediriger vers la page d'impression avec les nouvelles attestations
            return redirect('sessions_list')

    else:
        form = SessionSoutenanceNewForm()
        
    context = {
        'form': form,
        "titre": "Nouvelle création de certificat",
        "info": "Nouvelle création de certificat",
        "info2": "Nouvelle création de certificat",
    }

    return render(request, 'etudiants/sessions/create.html', context=context)


@login_required
@staff_required
def attestation_print(request, pk):
    session = SessionSoutenanceNew.objects.get(pk=pk)
    base_url =  request.build_absolute_uri('/'),
    context = {
        'base' : base_url, 
        'attestations' :  session.candidats
    }
    return render(request, 'etudiants/attestation/print_attestations.html', context=context)

@login_required
@staff_required
def authenticite_print(request, pk):
    session = SessionSoutenanceNew.objects.get(pk=pk)
    base_url =  request.build_absolute_uri('/'),
    context = {
        'base' : base_url, 
        'attestations' :  session.candidats
    }
    return render(request, 'etudiants/attestation/print_authenticite.html', context=context)

@login_required
@staff_required
def attestation_details(request, pk):
    base_url =  request.build_absolute_uri('/'),
    context = {
        'attestation' : AttestationNew.objects.get(pk=pk),
        'base':base_url
    }
    return render(request, 'etudiants/attestation/print_attestations.html', context=context)


def verify_attestation(request, code):
    base_url = request.build_absolute_uri('/'),
    try:
        attestation = AttestationNew.objects.get(code=code)
        context = {
        'attestation' : attestation,
        'found' : True,
        'base' : base_url
        }
        return render(request, 'etudiants/attestation/verify.html', context=context)
    except:
        context = {
        
        'found' : False
        }
        return render(request, 'etudiants/attestation/verify.html', context=context)
    

@login_required
@staff_required
def import_diplomes(request):
    if request.method == 'POST':
        form = SessionDiplomeNewForm(request.POST, request.FILES)
        if form.is_valid():

            session_soutenance = form.save(commit=False)
            session_soutenance.etablissement_id = request.user.etablissement.id
            session_soutenance.save()
            # Utiliser pandas pour lire le fichier Excel
            df = pd.read_excel(session_soutenance.fichier)
            # Créer une attestation pour chaque ligne dans le fichier Excel
            new_attestations = []
            for index, row in df.iterrows():
                Diplome.objects.create(
                        session=session_soutenance,
                        nom=row['nom'],
                        prenom=row['prenoms'],
                        diplome=row['diplome'],
                        date_de_naissance=row['date_de_naissance'],
                        lieu_de_naissance=row['lieu_de_naissance'],
                        cycle=row['cycle'],
                        niveau=row['niveau'],
                        annee_academique=row['annee_academique'],
                        programme=row['session'],
                
                )

            # Rediriger vers la page d'impression avec les nouvelles attestations
            return redirect('liste_sessions_diplomes')

    context = {
        
        "titre" : "Nouveau Diplôme",
        "info"  : "Nouveau Diplôme",
        "info2" : "Nouveau Diplôme",
    }
    return render(request, 'etudiants/sessions/diplome_create.html', context)

@login_required
@staff_required
def liste_sessions_diplomes(request):
    sessions = SessionDiplome.objects.all()
    context = {
        
        "titre" : "Liste des Diplômes",
        "info"  : "Liste des Diplômes",
        "info2" : "Liste des Diplômes",
        'sessions': sessions
    }
    return render(request, 'etudiants/sessions/diplome_listes.html', context=context)


@login_required
@staff_required
def diplomes_details(request, pk):
    base_url =  request.build_absolute_uri('/'),
    session = SessionDiplome.objects.get(pk=pk)
    context = {
        'session' : session,
        'base':base_url,
         'attestations' :  session.candidats
    }
    return render(request, 'etudiants/sessions/diplome_details.html', context=context)




#####################################################""


@login_required
@staff_required
def certificats_create(request):
    if request.method == 'POST':
        form = SessionCertificatNewForm(request.POST, request.FILES)
        if form.is_valid():

            session_soutenance = form.save(commit=False)
            session_soutenance.etablissement_id = request.user.etablissement.id
            session_soutenance.save()
            # Utiliser pandas pour lire le fichier Excel
            df = pd.read_excel(session_soutenance.fichier)
            # Créer une attestation pour chaque ligne dans le fichier Excel
            new_attestations = []
            for index, row in df.iterrows():
                Certificat.objects.create(
                        session=session_soutenance,
                        nom=row['nom'],
                        prenom=row['prenoms'],
                        diplome=row['diplome'],
                        date_de_naissance=row['date_de_naissance'],
                        lieu_de_naissance=row['lieu_de_naissance'],
                        cycle=row['cycle'],
                        niveau=row['niveau'],
                        annee_academique=row['annee_academique'],
                        programme=row['session'],
                
                )

            # Rediriger vers la page d'impression avec les nouvelles attestations
            return redirect('certificats_listes')

    context = {
        
        "titre" : "Nouveau Certificats",
        "info"  : "Nouveau Certificats",
        "info2" : "Nouveau Certificats",
    }
    return render(request, 'etudiants/sessions/certificats_create.html', context)

@login_required
@staff_required
def certificats_listes(request):
    sessions = CertificatSession.objects.all()
    context = {
        
        "titre" : "Liste des Certificats",
        "info"  : "Liste des Certificats",
        "info2" : "Liste des Certificats",
        'sessions': sessions
    }
    return render(request, 'etudiants/sessions/certificats_listes.html', context=context)


@login_required
@staff_required
def certificats_details(request, pk):
    base_url =  request.build_absolute_uri('/'),
    session = CertificatSession.objects.get(pk=pk)
    context = {
        'session' : session,
        'base':base_url,
         'attestations' :  session.candidats
    }
    return render(request, 'etudiants/sessions/certificats_details.html', context=context)