from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, redirect, reverse
from decorators.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import (Salle, AnneeAcademique, Filiere, Niveau, Classe, Maquette, UniteEnseignement, Matiere, Campus)
from emplois_du_temps.models import Programme, EmploisDutemps
from inscription.models import Inscription
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count
from .forms import MaquetteForm, UniteEnseignementForm, MatiereForm
from django.db.models import Count, Q


## Section Année Academique
@login_required
@staff_required
def annees_academiques_list(request):
    if request.method == 'POST':
        debut = request.POST.get('debut')
        fin = request.POST.get('fin')
        
        try:
            debut_int = int(debut)
            fin_int = int(fin)
            
            if AnneeAcademique.objects.filter(etablissement=request.user.etablissement, debut=debut_int, fin=fin_int).exists():
                messages.error(request, "L'année académique existe déjà pour ces dates.")
            else:
                annee = AnneeAcademique.objects.create(etablissement=request.user.etablissement, debut=debut_int, fin=fin_int)
                messages.success(request, "L'année académique a été créée avec succès.")
        except ValueError:
            messages.error(request, "Les années doivent être des nombres entiers.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect('annees_academiques_list')

    context = {
        "titre" : "Années Académiques",
        "info": "Liste",
        "info2" : "Années Académiques",
        "annees": AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-debut','-fin'),
        "datatable": True,
    }
    return render(request, 'gestion_academique/annee_academique/list.html', context=context)

@login_required
@staff_required
def salles_list(request):
    
    if request.method == 'POST':
        nom = request.POST.get('nom')
        capacite = request.POST.get('capacite')

        try:
            capacite_int = int(capacite)
            
            if len(nom) >= 3 and capacite_int > 1:
                if Salle.objects.filter(etablissement=request.user.etablissement, nom=nom).exists():
                    messages.error(request, "La salle avec ce nom existe déjà.")
                else:
                    salle = Salle.objects.create(etablissement=request.user.etablissement, nom=nom, capacite=capacite_int)
                    messages.success(request, "La salle a été créée avec succès.")
            else:
                messages.error(request, "Les données de la salle ne sont pas valides.")
        except ValueError:
            messages.error(request, "La capacité doit être un nombre entier supérieur à 1.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect('salles_list')

    context = {
        "titre" : "Salles",
        "info": "Liste",
        "info2" : "Salles",
        "salles": Salle.objects.filter(etablissement_id=request.user.etablissement.id),
        "datatable": True,
        "campus" : Campus.objects.filter(etablissement_id=request.user.etablissement.id),
    }
    return render(request, 'gestion_academique/salles/list.html', context=context)


## Section Filiere
@login_required
@staff_required
def filieres_list(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        parcours = request.POST.get('parcours')
        sigle = request.POST.get('sigle')

        try:
            if len(nom) >= 3 and parcours in ['UNIVERSITAIRE', 'PROFESSIONNEL'] and len(sigle) >= 2:
                if Filiere.objects.filter(etablissement=request.user.etablissement, nom=nom).exists():
                    messages.error(request, "La filière avec ce nom existe déjà.")
                else:
                    filiere = Filiere.objects.create(etablissement=request.user.etablissement, nom=nom, parcour=parcours, sigle=sigle)
                    messages.success(request, "La filière a été créée avec succès.")
            else:
                messages.error(request, "Les données de la filière ne sont pas valides.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect('filieres_list')

    context = {
        "titre" : "Filières",
        "info": "Liste",
        "info2" : "Filières",
        "filieres": Filiere.objects.filter(etablissement_id=request.user.etablissement.id),
        "datatable": True,
    }
    return render(request, 'gestion_academique/filiere/list.html', context=context)



## Section Niveau
@login_required
@staff_required
def niveaux_list(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')

        try:
            if len(nom) >= 3:
                if Niveau.objects.filter(etablissement=request.user.etablissement, nom=nom).exists():
                    messages.error(request, "Le niveau avec ce nom existe déjà.")
                else:
                    niveau = Niveau.objects.create(etablissement=request.user.etablissement, nom=nom)
                    messages.success(request, "Le niveau a été créé avec succès.")
            else:
                messages.error(request, "Le nom du niveau doit contenir au moins 3 caractères.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect('niveaux_list')

    context = {
        "titre" : "Niveaux",
        "info": "Liste",
        "info2" : "Niveaux",
        "niveaux": Niveau.objects.filter(etablissement_id=request.user.etablissement.id),
        "datatable": True,
    }
    return render(request, 'gestion_academique/niveau/list.html', context=context)


## Section Classes
@login_required
@staff_required
def classes_list(request):
    selected_annee_id = request.GET.get('annee_id')

    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    classes = Classe.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id)

    if selected_annee_id:

        classes = classes.filter(annee_academique_id=selected_annee_id)
    else:
        classes = classes.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())

    context = {
        "titre": "Classes",
        "info": "Lites",
        "info2": "Classes",
        "classes": classes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'gestion_academique/classe/list.html', context=context)


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
    selected_annee_id = request.GET.get('annee_id')
    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    maquettes = Maquette.objects.filter(etablissement_id=request.user.etablissement.id)

    if selected_annee_id:
        maquettes = maquettes.filter(annee_academique_id=selected_annee_id)
    else:
        maquettes = maquettes.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())

    if request.method == 'POST':
        form = MaquetteForm(request.user.etablissement.id, request.POST)
        if form.is_valid():
            annee_academique = form.cleaned_data['annee_academique']
            filiere = form.cleaned_data['filiere']
            niveau = form.cleaned_data['niveau']
            maquette_universitaire =  form.cleaned_data['maquette_universitaire']
            maquette_professionnel_jour = form.cleaned_data['maquette_professionnel_jour']
            maquette_professionnel_soir = form.cleaned_data['maquette_professionnel_soir']
            maquette_cours_en_ligne = form.cleaned_data['maquette_cours_en_ligne']
            
            # Vérifier si une maquette avec les mêmes caractéristiques existe déjà
            existing_maquette = Maquette.objects.filter(
                etablissement=request.user.etablissement,
                annee_academique=annee_academique,
                filiere=filiere,
                niveau=niveau,
                maquette_universitaire=maquette_universitaire,
                maquette_professionnel_jour=maquette_professionnel_jour,
                maquette_professionnel_soir=maquette_professionnel_soir,
                maquette_cours_en_ligne=maquette_cours_en_ligne
            ).exists()

            if existing_maquette:
                messages.error(request, "Une maquette avec les mêmes caractéristiques existe déjà.")
            else:
                maquette = form.save(commit=False)
                maquette.etablissement = request.user.etablissement
                maquette.save()
                messages.success(request, "Maquette ajoutée avec succès.")
                return redirect('maquette_details', maquette.id)
    else:
        form = MaquetteForm(request.user.etablissement.id)

    context = {
        "titre": "Maquettes",
        "info": "Lites",
        "info2": "Maquettes",
        "maquettes": maquettes,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
        "form" : form,
    }
    return render(request, 'gestion_academique/maquette/list.html', context=context)

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

@login_required
@staff_required
def statistiques(request):
    selected_annee_id = request.GET.get('annee_id')
    etablissement = request.user.etablissement
    annees_academiques = AnneeAcademique.objects.filter(etablissement=etablissement).order_by('-created')

    scolarites = Inscription.objects.filter(etudiant__etablissement=etablissement, confirmed=True)

    if selected_annee_id:
        scolarites = scolarites.filter(annee_academique_id=selected_annee_id)
        annee_nom = AnneeAcademique.objects.get(pk=selected_annee_id)
    else:
        last_annee_academique = etablissement.annee_academiques.last()
        scolarites = scolarites.filter(annee_academique=last_annee_academique)
        annee_nom = last_annee_academique

    # Calcul du nombre total d'inscriptions
    total_stats = scolarites.aggregate(
        total_inscriptions=Count('id'),
        total_re_inscriptions=Count('id', filter=Q(nature='RE-INSCRIPTION')),
        total_new_inscriptions=Count('id', filter=Q(nature='INSCRIPTION')),
        affectes=Count('id', filter=Q(etudiant__type_etudiant='Affecté(e)')),
        non_affectes=Count('id', filter=Q(etudiant__type_etudiant='Non Affecté(e)')),
        inscriptions_attente_paiement=Count('id', filter=Q(paye=0) & ~Q(solded=True))
    )

    # Autres statistiques (par cycle et par niveau)
    cycles = ['CYCLE UNIVERSITAIRE', 'CYCLE PROFESSIONNEL JOUR', 'CYCLE PROFESSIONNEL SOIR', 'CYCLE EN LIGNE']
    cycle_stats = {}
    niveau_stats = {}

    # Définir l'ordre des niveaux
    ordre_niveaux = ['BTS 1', 'BTS 2', 'LICENCE 1', 'LICENCE 2', 'LICENCE 3', 'MASTER 1', 'MASTER 2']

    for cycle in cycles:
        cycle_stats[cycle] = {
            'etudiant_affecte': scolarites.filter(parcour=cycle, etudiant__type_etudiant='Affecté(e)').count(),
            'etudiant_non_affecte': scolarites.filter(parcour=cycle, etudiant__type_etudiant='Non Affecté(e)').count(),
            'inscriptions': scolarites.filter(parcour=cycle, nature='INSCRIPTION').count(),
            're_inscriptions': scolarites.filter(parcour=cycle, nature='RE-INSCRIPTION').count(),
            'total': scolarites.filter(parcour=cycle).count(),
        }

        niveaux = scolarites.filter(parcour=cycle).values('niveau__nom').distinct()

        # Trier les niveaux selon l'ordre défini
        niveaux = sorted(niveaux, key=lambda x: ordre_niveaux.index(x['niveau__nom']) if x['niveau__nom'] in ordre_niveaux else len(ordre_niveaux))

        niveau_stats[cycle] = {}

        for niveau in niveaux:
            niveau_name = niveau['niveau__nom']
            niveau_stats[cycle][niveau_name] = {
                'etudiant_affecte': scolarites.filter(parcour=cycle, niveau__nom=niveau_name, etudiant__type_etudiant='Affecté(e)').count(),
                'etudiant_non_affecte': scolarites.filter(parcour=cycle, niveau__nom=niveau_name, etudiant__type_etudiant='Non Affecté(e)').count(),
                'inscriptions': scolarites.filter(parcour=cycle, niveau__nom=niveau_name, nature='INSCRIPTION').count(),
                're_inscriptions': scolarites.filter(parcour=cycle, niveau__nom=niveau_name, nature='RE-INSCRIPTION').count(),
                'total': scolarites.filter(parcour=cycle, niveau__nom=niveau_name).count(),
            }

    context = {
        **total_stats,
        'cycle_stats': cycle_stats,
        'niveau_stats': niveau_stats,
        'titre': f"Statistiques de l'Année Académique {annee_nom}",
        'info': "Liste des Scolarités",
        'info2': "Liste des Scolarités",
        'datatable': True,
        'can_select_annee': True,
        'annees_academiques': annees_academiques,
    }
    return render(request, 'gestion_academique/statistiques.html', context)




@login_required
@staff_required
def recap_inscriptions(request):
    etablissement = request.user.etablissement

    # Fetch the academic years related to the establishment
    annees_academiques = AnneeAcademique.objects.filter(etablissement=etablissement).order_by('-created')

    # Default to the last academic year
    selected_annee_id = request.GET.get('annee_id')
    if selected_annee_id:
        annee_academique = get_object_or_404(AnneeAcademique, pk=selected_annee_id, etablissement=etablissement)
    else:
        annee_academique = annees_academiques.first()  # Get the most recent year

    # Filter inscriptions for the selected academic year
    inscriptions = Inscription.objects.filter(
        etudiant__etablissement=etablissement,
        confirmed=True,
        annee_academique=annee_academique
    )

    # Get counts grouped by filière, niveau, and cycle
    stats = inscriptions.values(
        'filiere__nom', 'niveau__nom', 'parcour'
    ).annotate(
        total_inscriptions=Count('id')
    ).order_by('parcour', 'filiere__nom', 'niveau__nom', )

    # Prepare the context for rendering
    context = {
        'titre': f"Récapitulatif des Inscriptions {annee_academique}",
        'stats': stats,
        'info': "Récapitulatif des Inscriptions",
        'info2': "Récapitulatif des Inscriptions",
        'datatable': True,
        'can_select_annee': True,
        'annees_academiques': annees_academiques,
    }

    return render(request, 'gestion_academique/effectifs.html', context)



@login_required
@staff_required
def scolarites_par_statut(request, statut):
    etablissement = request.user.etablissement

    # Filtrage basé sur le statut
    if statut == 'total':
        scolarites = Inscription.objects.filter(etudiant__etablissement=etablissement)
    elif statut == 'new':
        scolarites = Inscription.objects.filter(etudiant__etablissement=etablissement, nature='INSCRIPTION')
    elif statut == 're':
        scolarites = Inscription.objects.filter(etudiant__etablissement=etablissement, nature='RE-INSCRIPTION')
    elif statut == 'affectes':
        scolarites = Inscription.objects.filter(etudiant__etablissement=etablissement, etudiant__type_etudiant='Affecté(e)')
    elif statut == 'non_affectes':
        scolarites = Inscription.objects.filter(etudiant__etablissement=etablissement, etudiant__type_etudiant='Non Affecté(e)')
    elif statut == 'attente_paiement':
        scolarites = Inscription.objects.filter(etudiant__etablissement=etablissement, paye=0, solded=False)
    else:
        scolarites = Inscription.objects.none()

    context = {
        'scolarites': scolarites,
        'statut': statut,
        'titre': f"Listes Inscriptions {statut}",
        'info': "Liste des Scolarités",
        'info2': "Liste des Scolarités",
        'datatable': True,
        'can_select_annee': True,
    }
    
    return render(request, 'gestion_academique/scolarites_par_statut.html', context)



@login_required
@staff_required
def migrate_students(request):
    selected_annee_id = request.GET.get('annee_id')

    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    
    classes = Classe.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id, closed=True)

    if selected_annee_id:

        classes = classes.filter(annee_academique_id=selected_annee_id)
    else:
        classes = classes.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())
        
    if request.method == 'POST':
        # Process the form data and create a new class
        selected_class_id = request.POST.get('selected_class')
        num_to_migrate = int(request.POST.get('num_to_migrate'))

        # Get the selected class
        selected_class = Classe.objects.get(id=selected_class_id)

        # Create a new class with the same characteristics
        new_class = Classe.objects.create(
            # You may need to adjust this based on your requirements
            annee_academique=selected_class.annee_academique,
            filiere=selected_class.filiere,
            niveau=selected_class.niveau,
            classe_universitaire=selected_class.classe_universitaire,
            classe_professionnelle_jour=selected_class.classe_professionnelle_jour,
            classe_professionnelle_soir=selected_class.classe_professionnelle_soir,
            classe_online=selected_class.classe_online,
            closed=True
            # Add other field values here
        )

        # Get the students to migrate
        students_to_migrate = Inscription.objects.filter(classe=selected_class).order_by('created')[:num_to_migrate]

        # Update their class to the new class
        for student in students_to_migrate:
            student.classe = new_class
            student.save()

        # Redirect to a success page or some other action
        messages.success(request, f"Migration éfféctuée avec succes, nouvelle classe : {new_class}")
        return redirect('classes_list')

    # If it's a GET request, render the form to select a class and enter the number to migrate
   
    context = {
      
        'titre': f"Migration de Classe",
        'info': "Migration de Classe",
        'info2': "Migration de Classe",
        'datatable': True,
        'can_select_annee': True,
        'classes' : classes,
        'annees_academiques': annees_academiques,
    }
    return render(request, 'gestion_academique/migrate_students.html', context=context)


@login_required
@staff_required
def move_uto_other_class_students(request):
    selected_annee_id = request.GET.get('annee_id')

    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')

    classes = Classe.objects.filter(annee_academique__etablissement_id=request.user.etablissement.id, closed=True)

    if selected_annee_id:
        classes = classes.filter(annee_academique_id=selected_annee_id)
    else:
        classes = classes.filter(annee_academique_id=request.user.etablissement.annee_academiques.last())

    if request.method == 'POST':
        # Process the form data and create a new class
        source_class_id = request.POST.get('source_class')
        destination_class_id = request.POST.get('destination_class')
        num_to_migrate = int(request.POST.get('num_to_migrate'))
        print('{} => {}'.format(source_class_id, destination_class_id))

        # Get the source and destination classes
        source_class = Classe.objects.get(id=source_class_id)
        destination_class = Classe.objects.get(id=destination_class_id)

        # Get the n oldest registrations from the source class
        if (
            source_class.filiere != destination_class.filiere or
            source_class.niveau != destination_class.niveau or
            source_class.annee_academique != destination_class.annee_academique
            ):
            # Handle the case where classes don't have the same characteristics
            # You may redirect to an error page or render an error message in the same page
            messages.error(request, f"Les classes n'ont pas les mêmes Data")
            return redirect('classes_list')
            
        
        students_to_migrate = Inscription.objects.filter(classe=source_class).order_by('created')[:num_to_migrate]

        # Update their class to the destination class
        for student in students_to_migrate:
            student.classe = destination_class
            student.save()

        # Redirect to a success page or some other action
        if source_class.nb_etudiant == 0:
            source_class.delete()
        messages.success(request, f"Les classes ont été fusionnées avec succes")
        return redirect('classes_list')
        

    return render(request, 'gestion_academique/move.html', {
        'annees_academiques': annees_academiques,
        'classes': classes,
        'titre': f"Fusion de Classe",
        'info': "Fusion de Classe",
        'info2': "Fusion de Classe",
        'datatable': True,
        'can_select_annee': True,
        'classes' : classes,
        'annees_academiques': annees_academiques,
    })



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

# Configure logging
logger = logging.getLogger(__name__)

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
            sessions = []
            form = None
            upload_form = None

        return render(request, self.template_name, {
            'sessions': sessions,
            'form': form,
            'upload_form': upload_form,
            "titre": "Commission Dîplome et Documentation Académique",
            "info": "Liste des Sessions",
            "info2": "Commission Dîplome et Documentation Académique",
            "datatable": True,
        })

    def post(self, request):
        try:
            form = SessionDiplomeForm(request.POST)
            upload_form = UploadFileForm(request.POST, request.FILES)

            if form.is_valid() and upload_form.is_valid():
                session = form.save(commit=False)
                session.etablissement = request.user.etablissement
                session.save()

                # Process the uploaded Excel file
                file = upload_form.cleaned_data['file']
                df = pd.read_excel(file)

                for index, row in df.iterrows():
                    Diplome.objects.create(
                        session=session,
                        matricule=row['matricule'],
                        nom=row['nom'],
                        prenom=row['prenom'],
                        date_de_naissance=row['date_de_naissance'],
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

                messages.success(request, 'Session and Diplomes created successfully.')
                return redirect('session_list')
            else:
                messages.warning(request, "Form validation failed. Please check the inputs.")

        except pd.errors.EmptyDataError:
            messages.error(request, "The uploaded Excel file is empty.")
        except pd.errors.ParserError:
            messages.error(request, "There was an error parsing the Excel file. Please ensure it's formatted correctly.")
        except KeyError as e:
            logger.error(f"Missing column in Excel file: {str(e)}")
            messages.error(request, f"The uploaded Excel file is missing a required column: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            messages.error(request, "An unexpected error occurred while processing the session. Please try again.")

        return render(request, self.template_name, {
            'sessions': SessionDiplome.objects.all(),
            'form': form,
            'upload_form': upload_form,
            "titre": "Commission Dîplome et Documentation Académique",
            "info": "Liste des Sessions",
            "info2": "Commission Dîplome et Documentation Académique",
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
        



from django.views.generic import UpdateView
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
