from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Resume, Information, Data
from .forms import InformationForm, DataForm, ResumeForm
from decorators.decorators import student_required
from django.contrib.auth.decorators import login_required

# Vue pour l'affichage et la modification du CV de l'étudiant
@login_required
@student_required
def student_cv(request):
    """
    Vue permettant à un étudiant d'afficher et de modifier son CV. 
    Le formulaire de résumé, ainsi que les formulaires associés pour 
    les informations et les données sont traités ici.
    """
    # Récupération ou création du résumé de l'étudiant
    resume, created = Resume.objects.get_or_create(etudiant=request.user.etudiant)
    
    # Création des formulaires imbriqués pour les informations et les données
    InformationFormSet = inlineformset_factory(Resume, Information, form=InformationForm, extra=0, can_delete=False)
    DataFormSet = inlineformset_factory(Resume, Data, form=DataForm, extra=0, can_delete=False)

    # Traitement des données envoyées par le formulaire
    if request.method == 'POST':
        # Initialisation des formulaires avec les données POST
        resume_form = ResumeForm(request.POST, instance=resume)
        info_formset = InformationFormSet(request.POST, instance=resume)
        data_formset = DataFormSet(request.POST, instance=resume)
        
        try:
            # Si tous les formulaires sont valides, sauvegarde des données
            if resume_form.is_valid() and data_formset.is_valid() and info_formset.is_valid():
                resume_form.save()
                info_formset.save()
                data_formset.save()
                messages.success(request, 'Données enregistrées avec succès !')
                return redirect('student_cv')
            else:
                # Si un des formulaires est invalide, affichage des messages d'erreur
                error_messages = []
                if not resume_form.is_valid():
                    error_messages.extend(resume_form.errors.values())
                if not data_formset.is_valid():
                    for form in data_formset:
                        if form.errors:
                            error_messages.extend(form.errors.values())
                
                # Afficher les erreurs
                for error_msg in error_messages:
                    messages.error(request, error_msg)
        except Exception as error:
            messages.error(request, error)
    else:
        # Initialisation des formulaires sans données
        resume_form = ResumeForm(instance=resume)
        info_formset = InformationFormSet(instance=resume)
        data_formset = DataFormSet(instance=resume)
    
    # Contexte pour afficher la page du CV
    context = {
        'titre': 'Mon Cv',  # Titre de la page
        'student_print': True,  # Indicateur pour l'affichage de la page du CV
        'resume': resume,  # Objet Resume à afficher
        'base_url': request.build_absolute_uri('/'),  # URL de base
        'url': reverse('student_cv_shared', kwargs={'code': resume.etudiant.code_paiement})[1:],  # URL partagée
        'resume_form': resume_form,  # Formulaire du résumé
        'info_formset': info_formset,  # Formulaire des informations
        'data_formset': data_formset,  # Formulaire des données
        'cv': True  # Indicateur pour dire que c'est une page de CV
    }
    
    # Rendu de la page du CV
    return render(request, 'curriculum/cv.html', context=context)


# Fonction pour supprimer des informations ou des données du CV
def delete_info_or_data(request, element, pk):
    """
    Permet de supprimer des éléments du CV (données ou informations) en fonction de l'élément spécifié.
    """
    if element == "data":
        try:
            # Suppression des données spécifiées
            data = get_object_or_404(Data, pk=pk, resume__etudiant=request.user.etudiant)
            data.delete()
            messages.success(request, 'Données supprimées avec succès !')
        except:
            messages.error(request, 'Impossible de supprimer cet élément !')
        return redirect('student_cv')

    if element == "info":
        try:
            # Suppression des informations spécifiées
            data = get_object_or_404(Information, pk=pk, resume__etudiant=request.user.etudiant)
            data.delete()
            messages.success(request, 'Données supprimées avec succès !')
        except:
            messages.error(request, 'Impossible de supprimer cet élément !')
        return redirect('student_cv')

    if element == "create_data":
        try:
            # Création de nouvelles données
            data = Data.objects.create(resume=request.user.etudiant.resume, nature="", intitule="")
        except:
            pass
        return redirect('student_cv')

    if element == "create_info":
        try:
            # Création de nouvelles informations
            data = Information.objects.create(resume=request.user.etudiant.resume, nature="", intitule="", etablissement="", debut="", fin="")
        except:
            pass
        return redirect('student_cv')


# Vue pour afficher le CV partagé de l'étudiant
def student_cv_shared(request, code):
    """
    Vue pour afficher le CV d'un étudiant à partir de son code de paiement.
    """
    # Récupérer le résumé de l'étudiant basé sur le code de paiement
    resume, created = Resume.objects.get_or_create(etudiant__code_paiement=code)
    
    # Contexte pour afficher la page du CV partagé
    context = {
        'titre': f'CV {resume.etudiant}',  # Titre de la page
        'student_print': True,  # Indicateur pour l'affichage de la page du CV
        'resume': resume,  # Objet Resume à afficher
        'shared': True,  # Indicateur pour dire que c'est un CV partagé
    }
    
    # Rendu de la page du CV partagé
    return render(request, 'curriculum/cv.html', context=context)
