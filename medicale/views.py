from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from gestion_academique.views import _get_user_etablissement
from .models import DossierMedical, Consultation
from .forms import ConsultationForm, DossierMedicalForm
from etudiants.models import Etudiant
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from gestion_academique.models import AnneeAcademique
from decorators.decorators import staff_required

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
@staff_required
def dossier_medical_views(request):
    dossier = None
    form = None
    if request.method == 'GET':
        code_paiement = request.GET.get('code_paiement')

        if code_paiement:
            try:
                etudiant = Etudiant.objects.get(code_paiement=code_paiement)
                dossier, created = DossierMedical.objects.get_or_create(etudiant=etudiant)
                form = DossierMedicalForm(instance=dossier)
                messages.success(request, f"Dossier médical {etudiant}")
            except Etudiant.DoesNotExist:
                messages.error(request, "Aucun étudiant trouvé avec ce code.")


    context = {
        'titre': f"Consultation Médicale {dossier}",
        'info': "Saisissez le code de l'étudiant à consulter",
        'info2': "Nouvelle Consultation",
        "datatable": True,
        "dossier": dossier,
        "form" : form,
        "update_medicale" : True
    }

    return render(request, 'medicale/dossier.html', context)

@login_required
@staff_required
def dossier_update(request,pk):
    dossier = DossierMedical.objects.get(pk=pk)
    if is_ajax(request) and request.method == "POST":
            form = DossierMedicalForm(request.POST, instance=dossier)
            if form.is_valid():
                updated_dossier = form.save(commit=False)
                updated_dossier.etudiant = dossier.etudiant
                updated_dossier.save()
                print(updated_dossier)
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "errors": form.errors})




@login_required
@staff_required
def consultation_create(request, pk, code, consultation_id=None):
    dossier = DossierMedical.objects.get(pk=pk)
    consultation = None

    try:
        if consultation_id:
            consultation = get_object_or_404(Consultation, pk=int(consultation_id))
    except:
        pass

    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.medecin = request.user
            consultation.dossier = dossier
            consultation.annee_academique = request.user.etablissement.annee_academiques.last()
            consultation.save()
            messages.success(request, f'Consultation enregistrée avec succès !')
            return redirect(reverse('consultation_details', kwargs={'pk' : consultation.pk, 'dossier' : consultation.dossier.pk, 'code' : consultation.dossier.etudiant.code_paiement }))
    else:
        form = ConsultationForm(instance=consultation)

    context = {
        'titre': f"Nouvelle Consultation - {dossier.etudiant.prenom}",
        'dossier': dossier,
        'form': form,
    }
    return render(request, 'medicale/consultation_create.html', context)



@login_required
@staff_required
def consultation_details(request, pk, dossier, code):
    consultation = Consultation.objects.get(pk=pk)
    context = {
        'consultation' : consultation,
        'titre': f"Consultation Médicale {consultation,}",
        'info': "",
        'info2': " Consultation",
        "datatable": True,
        "dossier": dossier,  # Ajout du dossier au contexte
    }
    return render(request, 'medicale/consultation_details.html', context=context)


@login_required
@staff_required
def consultation_list(request):
    # 1) Récupération de l'établissement de l'utilisateur
    etablissement = _get_user_etablissement(request)

    if etablissement is None:
        messages.error(
            request,
            "Votre compte n'est rattaché à aucun établissement. "
            "Merci de contacter l’administrateur pour corriger cette situation.",
        )
        context = {
            "consultations": [],
            "titre": "Historique des consultations",
            "info": "",
            "info2": "Consultation",
            "datatable": False,
            "can_select_annee": False,
            "annees_academiques": [],
            "no_etablissement": True,
        }
        return render(request, "medicale/historique.html", context=context)

    # 2) Gestion de l'année académique
    selected_annee_id = request.GET.get("annee_id")

    annees_academiques = AnneeAcademique.objects.filter(
        etablissement_id=etablissement.id
    ).order_by("-created")

    annee_active = None
    if selected_annee_id:
        # On vérifie que l’année demandée appartient bien à cet établissement
        annee_active = annees_academiques.filter(id=selected_annee_id).first()

    if annee_active is None:
        # Dernière année (la plus récente)
        annee_active = annees_academiques.first()

    # 3) Récupération des consultations pour cet établissement + année active
    consultations = Consultation.objects.filter(
        medecin__etablissement_id=etablissement.id
    )
    if annee_active:
        consultations = consultations.filter(annee_academique_id=annee_active.id)

    # 4) Contexte envoyé au template
    context = {
        "consultations": consultations,
        "titre": f"Historique des consultations {etablissement}",
        "info": "",
        "info2": "Consultation",
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "annee_active": annee_active,
        "no_etablissement": False,
    }
    return render(request, "medicale/historique.html", context=context)