from django.shortcuts import render, redirect, reverse
from .forms import EnseignantForm,ContratEnseignantForm, PasswordChangeCustomForm
from .models import Enseignant, ContratEnseignant, TravauxDirige
from decorators.decorators import staff_required, teacher_required
from django.contrib.auth.decorators import login_required, user_passes_test
from authentication.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
# Create your views here.
from gestion_academique.models import Matiere, Classe, AnneeAcademique
from django.http import JsonResponse
from django.core import serializers
from emplois_du_temps.models import Programme
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash


@login_required
@staff_required
def admission(request):

    if request.method == 'POST':
        form = EnseignantForm(request.POST,request.FILES)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            email = form.cleaned_data['email']
            password = "pbkdf2_sha256$260000$H157G58nYUDjbBTAZTSPbI$JGpbJlZ5pV9nB2lZGAc6jguEWKHJzagBEyG7D2rKZas="
            user = User.objects.create(email=email, 
                                            password=password, 
                                            nom=nom, prenom=prenom, 
                                            is_teacher=True,
                                            etablissement_id=request.user.etablissement.id
                                            )
            enseignant = form.save(commit=False)
            
            enseignant.utilisateur = user
            enseignant.etablissement_id = request.user.etablissement.id
            enseignant.save()
            messages.success(request, "Dossier de l'enseignant créé avec succès , !")
            return redirect(reverse('enseignant_profile', kwargs={'code': enseignant.code }))
             
            
    else:
        form = EnseignantForm()
    context = {
      
        "titre" : "ENREGISTREMENT ENSEIGNANT",
        "info": "ENREGISTREMENT",
        "info2" : "ENREGISTREMENT ENSEIGNANT",
        "datatable": False,
        'form': form
    }
    return render(request, 'enseignant/admission/admission.html', context=context)


@login_required
@staff_required
def liste_enseignants(request):

    context = {
        "titre" : "Liste des enseignants",
        "info": "Lites",
        "info2" : "Liste des enseignants",
        "enseignants": Enseignant.objects.filter(etablissement_id=request.user.etablissement.id),
        "datatable": True,
    }
    return render(request, 'enseignant/listes/list.html', context=context)

@login_required
@staff_required
def enseignant_profile(request,code):
    if request.method == 'POST':
        enseignant = Enseignant.objects.get(code=code)
        annee_academique = request.user.etablissement.annee_academiques.last()
        # Create the ContratEnseignant object
        contrat = ContratEnseignant.objects.create(
            enseignant=enseignant,
            annee_academique=annee_academique,
        )
        messages.success(request, f"Reinseignez les parametre du contrat {contrat.id}")
        return redirect(reverse('create_contrat_enseignant', kwargs={'code' : code , 'pk' : contrat.pk }))
    enseignant = get_object_or_404(Enseignant, code=code)
    context = {
        "titre" : enseignant,
        "info": "Profile Enseignant",
        "info2" : enseignant,
        "enseignant" : enseignant,
        "can_add_contrat" : True,
    }
    return render(request, 'enseignant/profiles/index.html', context=context)

@login_required
@staff_required
def get_matiere_classe(request):
    if request.method == 'GET':
        annee_academique = request.GET.get('annee_academique')
        filiere = request.GET.get('filiere')
        niveau = request.GET.get('niveau')

        matieres = Matiere.objects.filter(maquette__filiere=filiere, maquette__niveau=niveau, maquette__annee_academique=annee_academique)
        classes = Classe.objects.filter(filiere=filiere, niveau=niveau, annee_academique=annee_academique)

        matiere_list = [{'id': matiere.id, 'nom_matiere': matiere.nom} for matiere in matieres]
        classe_list = [{'id': classe.id, 'nom_classe': classe.nom} for classe in classes]

        data = {'matiere': matiere_list, 'classe': classe_list}

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)




@login_required
@staff_required
def create_contrat_enseignant(request, code, pk):
    contrat = get_object_or_404(ContratEnseignant, enseignant__code=code, pk=pk)
    if request.method == 'POST':
        form = ContratEnseignantForm(request.user.etablissement.id, request.POST, request.FILES, instance=contrat)
        if form.is_valid():
            # Check if a similar ContratEnseignant already exists
            existing_contrat = ContratEnseignant.objects.filter(
                annee_academique=form.cleaned_data['annee_academique'],
                filiere=form.cleaned_data['filiere'],
                niveau=form.cleaned_data['niveau'],
                classe=form.cleaned_data['classe'],
                matiere=form.cleaned_data['matiere'],
            ).first()

            if existing_contrat and existing_contrat.pk != contrat.pk:
                # If an existing contrat is found and its pk is not the same as the current contrat
                messages.error(request, 'Un contrat avec les mêmes caractéristiques existe déjà.')
            else:
                # No similar contrat found, save the form
                contrat = form.save()
                # Faire quelque chose après la sauvegarde réussie du contrat (redirection, message, etc.)
                return redirect(reverse('contrat_enseignant_print', kwargs={'code': code, 'pk': contrat.pk}))

    else:
        form = ContratEnseignantForm(request.user.etablissement.id, instance=contrat)

    context = {
        "titre": contrat.enseignant,
        "info": "Nouveau Contrat",
        "info2": contrat.enseignant,
        "enseignant": contrat.enseignant,
        "search_matiere_classe": True,
        'form': form
    }
    return render(request, 'enseignant/contrats/create.html', context=context)




@login_required
@staff_required
def contrat_enseignant_print(request, code, pk):
    contrat = get_object_or_404(ContratEnseignant, enseignant__code=code, pk=pk)
    context = {
        "titre" : contrat.enseignant,
        "info": "Nouveau Contrat",
        "info2" :  contrat.enseignant,
        "enseignant" :  contrat.enseignant,
        'contrat': contrat
       
    }
    return render(request, 'enseignant/contrats/print.html', context=context)

def is_staff_or_teacher(user):
    return user.is_staff or user.is_teacher

@user_passes_test(is_staff_or_teacher)
def contrat_enseignant_list_admin(request, code):
    selected_annee_id = request.GET.get('annee_id')

    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    contrats = ContratEnseignant.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id, enseignant__code=code)

    if selected_annee_id:

        contrats = contrats.filter(annee_academique_id=selected_annee_id)
    else:
        contrats = contrats.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())
    
    context = {
        "titre" : "Liste Contrats",
        "info": "Liste Contrats",
        "info2" :  "Liste Contrats",
        "enseignant" :   "Liste Contrats",
        "contrats" : contrats, 
          "datatable": True,
          "can_select_annee": True,
        "annees_academiques": annees_academiques,
       
    }
    return render(request, 'enseignant/contrats/listes_contrat.html', context=context)




def is_staff_or_teacher(user):
    return user.is_staff or user.is_teacher

@user_passes_test(is_staff_or_teacher)
def contrat_enseignant_list(request, code):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    contrats = ContratEnseignant.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id, enseignant__code=code)
    if selected_annee_id:
        contrats = contrats.filter(annee_academique_id=selected_annee_id)
    else:
        contrats = contrats.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())
    context = {
        "titre" : "Liste Contrats",
        "info": "Liste Contrats",
        "info2" :  "Liste Contrats",
        "enseignant" :   "Liste Contrats",
        "contrats" : contrats, 
          "datatable": True,
          "can_select_annee": True,
        "annees_academiques": annees_academiques,
       
    }
    return render(request, 'enseignant/contrats/listes_all_contrat.html', context=context)


########################################### Vue Personnel Espace Enseignant


@login_required
@teacher_required
def home(request):
    selected_annee_id = request.GET.get('annee_id')
    es = Enseignant.objects.get(utilisateur=request.user)

    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    programmes = Programme.objects.filter(emplois_du_temps__classe__annee_academique__etablissement_id=request.user.etablissement.id,
                                          
                                          matiere__enseignant=es)

    if selected_annee_id:

        programmes = programmes.filter(emplois_du_temps__classe__annee_academique_id=selected_annee_id)
    else:
        programmes = programmes.filter(emplois_du_temps__classe__annee_academique_id=request.user.etablissement.annee_academiques.last())
        
    context = {
        "titre": "Tableau de Bord",
        "info": "Enseignant",
        "info2": "Tableau de Bord",
        "programmes": programmes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        'jours_semaine' : ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE'],
    }
    return render(request, 'enseignant/dashboard/index.html', context=context)


@login_required
@teacher_required
def teachers_password(request):
    
    if request.method == "POST":
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Mot de passe modifié !")
            return redirect("teacher_home")
    else:
        form = PasswordChangeCustomForm(request.user)
    context = {
        'titre' : 'Modifier mes Accès',
        "form": form,
         }
    return render(request, 'enseignant/dashboard/password.html', context=context)


@login_required
@teacher_required
def classe_list(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    contrats = ContratEnseignant.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id, enseignant=request.user.enseignant)
    if selected_annee_id:
        contrats = contrats.filter(annee_academique_id=selected_annee_id)
    else:
        contrats = contrats.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())
    context = {
        "titre" : "Liste Contrats",
        "info": "Liste Contrats",
        "info2" :  "Liste Contrats",
        "enseignant" :   "Liste Contrats",
        "contrats" : contrats, 
          "datatable": True,
          "can_select_annee": True,
        "annees_academiques": annees_academiques,
       
    }

    context = {
        "titre": "Liste des classes",
        "info": "Enseignant",
        "info2": "Liste des classes",
        "programmes": contrats,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
       
    }
    return render(request, 'enseignant/dashboard/list_classe.html', context=context)



@login_required
@teacher_required
def fiche_contrat_note(request, pk):
    contrat = get_object_or_404(ContratEnseignant,pk=pk)
    context = {
        "titre": f"FICHE DE NOTE {contrat} - {contrat.classe}",
        "info": "Fiche de Notes",
        "info2": f"{contrat}",
        "datatable": True,
        "etudiants" : contrat.classe.effectifs

    }
    return render(request, 'enseignant/dashboard/fiche_note.html', context=context)


@login_required
@teacher_required
def demande_accompte(request, code, pk):
    accompte = ContratEnseignant.objects.get(pk=pk, enseignant__code=code)
    accompte.demande_accompte =True
    accompte.save()
    messages.success(request, "Démande d'accompte enregistrée avec success")
    return redirect('classe_list')



########################################### Section accomptes

@login_required
@staff_required
def demande_accompte_list(request, demande, traiter):
    selected_annee_id = request.GET.get('annee_id')
    etablissement_id = request.user.etablissement.id

    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=etablissement_id).order_by('-created')
    
    accomptes = ContratEnseignant.objects.filter(
        enseignant__etablissement_id=etablissement_id,
        demande_accompte=demande,
        demande_traitee=traiter
    )

    if selected_annee_id:
        accomptes = accomptes.filter(annee_academique_id=selected_annee_id)
    else:
        latest_annee_academique_id = AnneeAcademique.objects.filter(etablissement_id=etablissement_id).last().id
        accomptes = accomptes.filter(annee_academique_id=latest_annee_academique_id)

    
    context = {
        "titre": f"Demandes d'acomptes",
        "info": "Listes",
        "info2": f"Demandes d'acomptes",
        "accomptes": accomptes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        'contrat_validated' : True
    }
    return render(request, 'enseignant/contrats/accomptes/list.html', context=context)


@login_required
@staff_required
@require_POST
def validate_demande_update_cheque_number(request):
    contrat_pk = request.POST.get('contrat_id')
    cheque_number = request.POST.get('chequeNumber')
    print(contrat_pk)
    print(cheque_number)

    if contrat_pk and cheque_number:
        contrat = get_object_or_404(ContratEnseignant, pk=contrat_pk)
        print(contrat)
        contrat.numero_cheque = cheque_number
        contrat.demande_traitee = True
        contrat.save()

        messages.success(request, f"Accompte validée , l'enseignant sera notifié")
        return redirect(reverse('demande_accompte_list', kwargs={'demande' : True , 'traiter' : False }))
        
    else:
        messages.error(request, f"Une erreur est survenue sur la demande d'accompte")
        return redirect(reverse('demande_accompte_list', kwargs={'demande' : True , 'traiter' : False }))


@login_required
@staff_required
def get_contrat_info(request):
    contrat_pk = request.GET.get('contrat_pk')
    
    if contrat_pk:
        contrat = ContratEnseignant.objects.get(pk=contrat_pk)
        data = {
            "code" : contrat.enseignant.code,
            "filiere" : contrat.filiere.nom,
            "niveau" : contrat.niveau.nom,
            "classe" : contrat.classe.nom,
            "matiere" : contrat.matiere.nom,
            "enseignant" : contrat.enseignant.nom + ' ' + contrat.enseignant.prenom,
            "montant" : contrat.cout,
            "contrat_id" : contrat.pk
        }
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'Contrat non trouvé.'}, status=400)


@login_required
@staff_required
def reception_cheque(request, code, pk):
    contrat = get_object_or_404(ContratEnseignant, enseignant__code=code, pk=pk)
    contrat.cheque_retire = True 
    contrat.save()
    context = {
        "titre" : f'Remise de cheque {contrat.enseignant}-{contrat}',
        "info": "Remise de cheque",
        "info2" :  f'Remise de cheque {contrat.enseignant}-{contrat}',
        "enseignant" :  "Remise de cheque",
        'contrat': contrat
       
    }
    return render(request, 'enseignant/contrats/accomptes/fiche_reception.html', context=context)


@user_passes_test(is_staff_or_teacher)
def contrat_list_admin(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    contrats = ContratEnseignant.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id).order_by('classe','filiere','niveau')
    if selected_annee_id:
        contrats = contrats.filter(annee_academique_id=selected_annee_id)
    else:
        contrats = contrats.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())
        
    context = {
        
        "titre" : "Liste Contrats",
        "info": "Liste Contrats",
        "info2" :  "Liste Contrats",
        "enseignant" :   "Liste Contrats",
        "contrats" : contrats, 
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'enseignant/contrats/listes.html', context=context)


########" Creation de Td"

@login_required
@staff_required
def creation_travaux_dirige(request, pk):
    contrat = get_object_or_404(ContratEnseignant,pk=pk)
    if request.method == 'POST':
        heure = int(request.POST.get('heure'))
        taux = int(request.POST.get('taux'))
        try:
            td  = TravauxDirige.objects.create(contrat_id=pk,volume_horaire=heure, taux_horaire=taux)
            messages.success(request, 'Le TD a éyé crée avec succes')
            return redirect(reverse('td_enseignant_print', kwargs={'pk': td.pk}))
        
        except Exception as e:
            messages.error(request, f'Une erreur est survenue: {e}')

    context = {
        "titre": f"CREATION DE TRAVAUX DIRIDES POUR LE CONTRAT {contrat}",
        "info": "TRAVAUX DIRIGES",
        "info2": f"",
        "contrat" : contrat
    }
    return render(request, 'enseignant/contrats/creation_td.html', context=context)


@login_required
@staff_required
def td_enseignant_print(request, pk):
    td = get_object_or_404(TravauxDirige, pk=pk)
    context = {
        "titre" : f"{td.contrat.enseignant} TD -  {td.contrat}",
        "info": "Nouveau Contrat",
        "info2" :  td.contrat.enseignant,
        "enseignant" :  td.contrat.enseignant,
        'td': td, 
        "contrat" : td.contrat
       
    }
    return render(request, 'enseignant/contrats/td.html', context=context)


from .models import Rib
from .forms import RibForm  # Replace with the actual form import


@login_required
@teacher_required
def rib_create_and_list(request):
    # Get the enseignant object

    enseignant = request.user.enseignant
    if request.method == 'POST':
        form = RibForm(request.POST, request.FILES)
        if form.is_valid():
            rib = form.save(commit=False)
            rib.enseignant = enseignant
            rib.save()
            return redirect('rib_create_and_list')
    else:
        form = RibForm()

    # Get all Ribs for the enseignant
    ribs = Rib.objects.filter(enseignant=enseignant).order_by('-created')
    
    context = {
        "titre": f"RIB",
        "info": "RIB",
        "info2": f"Liste des RIB",
        "form" :  form, 
        "ribs" : ribs,
        "datatable": True,
    
    }

    return render(request, 'enseignant/dashboard/rib_form.html', context=context)


# Td Liste

@login_required
@teacher_required
def td_list(request):
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    contrats = ContratEnseignant.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id, enseignant=request.user.enseignant)
    if selected_annee_id:
        contrats = contrats.filter(annee_academique_id=selected_annee_id)
    else:
        contrats = contrats.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())
    

    context = {
        "titre": "Mes TD",
        "info": "Enseignant",
        "info2": "Mes TD",
        "programmes": contrats,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
       
    }
    return render(request, 'enseignant/dashboard/td_liste.html', context=context)


@login_required
@teacher_required
def delete_rib(request, rib_id):
    
    rib = get_object_or_404(Rib, id=rib_id)

    # Get the associated enseignant
    enseignant = rib.enseignant

    # Get the most recent plan

    # Delete the Rib
    rib.delete()
    
    most_recent_plan = Rib.objects.filter(enseignant=enseignant).order_by('-created').first()

    # Check if there is a most recent plan
    if most_recent_plan:
        # Update the most recent plan to have default=True
        most_recent_plan.default = True
        most_recent_plan.save()

    messages.success(request, 'Rib supprimé avec succès.')
    return redirect('rib_create_and_list')