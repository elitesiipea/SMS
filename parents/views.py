from django.shortcuts import render
from inscription.models import Inscription
from emplois_du_temps.models import EmploisDutemps, Programme
from evaluations.models import Resultat
from gestion_academique.models import Maquette
from etudiants.models import Etudiant
from django.contrib import messages

def parents_home(request):
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        contactparent = request.POST.get('contactparent')
        try:
            etudiant = Etudiant.objects.get(matricule=matricule, contactparent=contactparent)
            scolarites = Inscription.objects.filter(etudiant=etudiant).order_by('created')
            scolarite_last = Inscription.objects.filter(etudiant=etudiant).last()
            maquette = Maquette.objects.filter(filiere=scolarites.last().filiere,niveau=scolarites.last().niveau,annee_academique=scolarites.last().annee_academique,).first()
            jours_semaine =  ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI', 'DIMANCHE']
            programmes = Programme.objects.filter(emplois_du_temps__classe=scolarites.last().classe,).order_by('debut','fin')
            resultats = Resultat.objects.filter(etudiant=scolarites.last(), note__classe__annee_academique=scolarites.last().annee_academique)
            messages.success(request, f'Dossier Trouvé | Etudiant :  {etudiant}')
            context = {

                'etudiant' : etudiant,
                 'scolarites' : scolarites,
                  'maquette' : maquette,
                   'jours_semaine' : jours_semaine,
                    'programmes' : programmes,
                    'resultats' : resultats,
                    'scolarite_last' : scolarite_last,

            }
            return render(request, 'parents/index.html', context=context)

        except Etudiant.DoesNotExist:

            messages.error(request, 'Aucun étudiant trouvé avec ces informations. !')
            return render(request, 'parents/index.html')

    return render(request, 'parents/index.html')