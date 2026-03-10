from django.shortcuts import render, redirect, reverse
from django.forms import inlineformset_factory
from .models import EmploisDutemps, Programme
from .forms import  ProgrammeForm
from gestion_academique.models import AnneeAcademique, Classe
from decorators.decorators import staff_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import EmploisDutemps, Programme
from django.contrib import messages
from .forms import ProgrammeForm
from enseignant.models import ContratEnseignant

## Section Classes
@login_required
@staff_required
def emploi_du_temps_list(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    emplois_du_temps = EmploisDutemps.objects.filter(classe__annee_academique__etablissement_id=request.user.etablissement.id)

    if selected_annee_id:

        emplois_du_temps = emplois_du_temps.filter(classe__annee_academique_id=selected_annee_id)
    else:
        emplois_du_temps = emplois_du_temps.filter(classe__annee_academique_id=request.user.etablissement.annee_academiques.last())

    context = {
        "titre": "Emplois du temps",
        "info": "Lites",
        "info2": "Emplois du temps",
        "emplois_du_temps": emplois_du_temps,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'emplois_du_temps/list.html', context=context)


from django.core.exceptions import ValidationError
from django.db.models import Q

@login_required
@staff_required
def emploisdutemps_detail(request, emploisdutemps_id, edit):
    emploisdutemps = get_object_or_404(EmploisDutemps, pk=emploisdutemps_id)
    programmes = emploisdutemps.emplois_du_temps_matiere.all()
    form = ProgrammeForm(request.user.etablissement.id , emploisdutemps.classe.id)
    
    
    if request.method == 'POST':
        form = ProgrammeForm(request.user.etablissement.id , emploisdutemps.classe.id, request.POST)
        if form.is_valid():
            programme = form.save(commit=False)
            
            # Vérifier si un programme similaire existe déjà
            existing_programme = Programme.objects.filter(
                Q(emplois_du_temps=emploisdutemps) &
                Q(salle=programme.salle) &
                Q(date=programme.date) &
                Q(debut__lt=programme.fin, fin__gt=programme.debut)
            )
            if existing_programme.exists():
                messages.error(request, "Un programme similaire existe déjà.")
            else:
                # Vérifier si le programme chevauche d'autres programmes
                overlapping_programmes = Programme.objects.filter(
                    Q(emplois_du_temps=emploisdutemps) &
                    Q(date=programme.date) &
                    Q(debut__lt=programme.fin, fin__gt=programme.debut)
                )
                if overlapping_programmes.exists():
                    messages.error(request, "Le programme chevauche un autre programme existant.")
                else:
                    programme.emplois_du_temps = emploisdutemps
                    programme.save()
                    messages.success(request, "Programme ajouté !")
                    return redirect(reverse('emploisdutemps_detail', kwargs={'emploisdutemps_id': emploisdutemps_id, 'edit': 1}))

    context = {
        "titre": f'EMPLOIS DU TEMPS {emploisdutemps}',
        "info": "Details",
        "info2": "Emplois du temps",
        "datatable": True,
        'emploisdutemps': emploisdutemps,
        'programmes': programmes.order_by('date'),
        'form': form,
        'edit': float(edit),
        'time_add': True,
        'jours_semaine' : ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
    }

    return render(request, 'emplois_du_temps/update_emplois_programme.html', context)



@login_required
@staff_required
def delete_programme(request, programme_id):
    programme = get_object_or_404(Programme, pk=programme_id)
    emploisdutemps_id = programme.emplois_du_temps.id
    programme.delete()
    messages.success(request, f"Programme supprimé !")
    return redirect(reverse('emploisdutemps_detail', kwargs={'emploisdutemps_id': emploisdutemps_id, 'edit': 1}))


@login_required
@staff_required
def emargements(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')

    programmes = Programme.objects.filter(emplois_du_temps__classe__annee_academique__etablissement_id=request.user.etablissement.id)

    if selected_annee_id:

        programmes = programmes.filter(emplois_du_temps__classe__annee_academique_id=selected_annee_id)
    else:
        programmes = programmes.filter(emplois_du_temps__classe__annee_academique_id=request.user.etablissement.annee_academiques.last())

    
    if request.method == 'POST':
        contrat_id = request.POST.get('contrat_id')
        duree = request.POST.get('duree')

        try:
            contrat = ContratEnseignant.objects.get(id=contrat_id)
            duree_float = float(duree)
            progression = contrat.progression + duree_float

            if progression <= contrat.volume_horaire:
                contrat.progression = progression
                if contrat.progression == contrat.volume_horaire:
                    contrat.closed = True
                else:
                    contrat.closed = False
                contrat.save()

                messages.success(request, "L'emargement a été enregistré avec succès.")
            else:
                messages.error(request, "La durée d'emargement dépasse le volume horaire du contrat.")

        except ContratEnseignant.DoesNotExist:
            messages.error(request, "Le contrat d'enseignant spécifié n'existe pas.")

    context = {
        "titre": "Emargements",
        "info": "Emargements",
        "info2": "Emargements",
        "programmes": programmes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        'contrat_validated' : True
    }
    return render(request, 'emplois_du_temps/emargements.html', context=context)