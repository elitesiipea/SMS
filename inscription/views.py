from django.shortcuts import render, redirect,reverse
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

@login_required
@staff_required
def student_inscription_details(request,pk):
    scolarite = Inscription.objects.get(pk=pk)
    context = {
        'scolarite' : scolarite,
        "titre" : "Détail Scolarité",
        "info": "Détail Scolarité",
        "info2" : scolarite,
        "datatable": False,
        "etudiant" : scolarite.etudiant,
        "paiements" : scolarite.inscription_paiement.filter(confirmed=True).order_by('created')
    }
    return render(request, 'inscription/inscription_details.html', context=context)


@login_required
@staff_required
def all_student_inscription_list(request):
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
    return render(request, 'inscription/all_inscrit.html', context=context)

############################################################################################################################

@login_required
@staff_required
def carte_print_details(request):
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
        "annees_academiques": annees_academiques,
        
    }
    return render(request, 'inscription/carte_print.html', context=context)




@login_required
@staff_required
def all_student_inscription_list_attentes(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    scolarites = Inscription.objects.filter(etudiant__etablissement_id=request.user.etablissement.id, confirmed=False)

    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
    else:
        scolarites = scolarites.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())

    context = {
        'scolarites' : scolarites,
        "titre" : f"Liste des Inscriptions en Attentes {request.user.etablissement}",
        "info": "Inscriptions en Attentes",
        "info2" : "Inscriptions en Attentes",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'inscription/all_inscrit_attentes.html', context=context)





@login_required
@staff_required
def scolarite_list(request):
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
        "annees_academiques": annees_academiques,
    }
    return render(request, 'inscription/list_scolarite.html', context=context)


@login_required
@staff_required
def paiement_historique_list(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    paiements = Paiement.objects.filter(inscription__etudiant__etablissement_id=request.user.etablissement.id, confirmed=True)
    if selected_annee_id:
        paiements = paiements.filter(inscription__annee_academique_id=selected_annee_id)
    else:
        paiements = paiements.filter(inscription__annee_academique_id=request.user.etablissement.annee_academiques.last())
    context = {
        'paiements' : paiements,
        "titre" : f"Historique des paiements {request.user.etablissement}",
        "info": "Historique des paiements",
        "info2" : "Historique des paiements",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'inscription/paiements/historique.html', context=context)



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
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    scolarites = Inscription.objects.filter(etudiant__etablissement_id=request.user.etablissement.id)

    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
    else:
        scolarites = scolarites.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())

    context = {
        'scolarites' : scolarites,
        "titre" : f"Emission des Kits & Accéssoires {request.user.etablissement}",
        "info": "Emission des Kits & Accéssoires",
        "info2" : "Emission des Kits & Accéssoires",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'inscription/kits/all_kits.html', context=context)



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



@login_required
@staff_required
def student_scolarite_list(request, slug):
    etudiant = Etudiant.objects.get(code_paiement=slug)
    scolarites = Inscription.objects.filter(etudiant__code_paiement=slug).order_by('-created')

    if request.method == 'POST':
        scolarite_id = request.POST.get('scolarite_id')
        montant = int(request.POST.get('montant'))
        source = request.POST.get('source')
        reference = request.POST.get('reference')

        scolarite = Inscription.objects.get(id=scolarite_id)

        # Vérifier si un paiement avec la même référence existe déjà
        existing_paiement = Paiement.objects.filter(
            Q(inscription=scolarite) & Q(reference=reference)
        ).exists()

        if existing_paiement:
            messages.error(request, "Un paiement avec la même référence existe déjà.")
        else:
            reste_a_payer = scolarite.reste
            if montant <= reste_a_payer:
                nouveau_paiement = Paiement.objects.create(
                    inscription=scolarite,
                    montant=montant,
                    source=source,
                    reference=reference,
                    confirmed=True,
                )
                messages.success(request, "Paiement enregistré avec succès !!")
                return redirect('student_inscription_details', pk=scolarite.id)
            else:
                messages.error(request, f"Montant supérieur. Il reste {reste_a_payer} Francs à payer.")

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
###############################################################################

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
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)  # Parse the JSON data from the request body.
            matricule = json_data.get('matricule', None)
            secret_id = json_data.get('secret_id', None)
            montant = json_data.get('montant', None)
            
            if secret_id in secret:
                if matricule:
                    try:
                        # Search for the Inscription record based on the provided matricule and solded=False.
                        inscription = Inscription.objects.filter(etudiant__code_paiement=matricule, solded=False).latest('created')

                        if action == 'get_inscription':
                            inscription_data = get_inscription_data(inscription)
                            return JsonResponse(inscription_data, status=200)
                        elif action == 'make_payment':
                            if montant is not None and isinstance(montant, int) and montant > 0:
                                ref = str(inscription.id) + "-ECOB-API-" + str(datetime.datetime.now())
                                paiement = Paiement.objects.create(
                                    inscription=inscription, 
                                    reference=ref,
                                    montant=montant,
                                    source="Ecobank Api",
                                    confirmed=True,
                                )
                                inscription_data = get_inscription_data(inscription)
                                return JsonResponse(inscription_data, status=200)
                            else:
                                return JsonResponse({'status': 'error', 'message': 'Montant Invalid.'}, status=400)

                    except Inscription.DoesNotExist:
                        return HttpResponseNotFound(json.dumps({'status': 'not found', 'message': 'No matching Inscription found.'}), content_type="application/json")
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid Secret Id'}, status=400)

        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'status': 'error', 'message': 'Invalid JSON data.'}), content_type="application/json")

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_inscription_by_matricule(request):
    return common_api_view(request, 'get_inscription')

@csrf_exempt
def make_new_paiment_form_ecobank(request):
    return common_api_view(request, 'make_payment')
