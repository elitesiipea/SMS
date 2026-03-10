from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect, redirect, reverse
from decorators.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Car, Trajet, Abonnement
from django.contrib import messages

@login_required
@staff_required
def CarListView(request):
    if request.method == 'POST':
        marque = request.POST.get('marque')
        immatriculation = request.POST.get('immatriculation')
        nb_places = int(request.POST.get('nombre_places'))
        
        try:
           
            if Car.objects.filter(immatriculation=immatriculation).exists():
                messages.error(request, "Un Car avec les mêmes references existe déja.")
            else:
                Car.objects.create(immatriculation=immatriculation, marque=marque,nombre_places=nb_places, etablissement_id=request.user.etablissement_id)
                messages.success(request, "Le Car a été créée avec succès.")
        except ValueError:
            messages.error(request, "Une erreur est survenue.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")
        return redirect('car_list')

    context = {
        "titre" : "Liste des Cars",
        "info": "Liste des Cars",
        "info2" : "Liste des Cars",
        "cars" : Car.objects.filter(etablissement_id=request.user.etablissement_id), 
        'datatable' :True
       
    }
    return render(request, 'transport/car_list.html', context=context)


@login_required
@staff_required
def TrajetListView(request):
    if request.method == 'POST':
        try:
            car = Car.objects.get(pk=request.POST['car'])
            depart = request.POST['depart']
            arrive = request.POST['arrive']
            cout_mensuel = int(request.POST['cout_mensuel'])
            print("{} {} {} {}".format(car, depart, arrive, cout_mensuel))

            
            if Trajet.objects.filter(
                car=car,
                ).exists():
                messages.error(request, "Ce Car est déja utilisé pour un trajet.")
            else:
                Trajet.objects.create(
                car=car,
                cout_mensuel=cout_mensuel, 
                depart=depart,
                arrive=arrive
                )
                messages.success(request, "Trajet créé avec succès.")
        except ValueError:
            messages.error(request, "Une erreur est survenue lors de la saisie du coût mensuel.")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {e}")

        return redirect('trajet_list')

    context = {
        "titre": "Liste des Trajets",
        "info": "Liste des Trajets",
        "info2": "Liste des Trajets",
        "trajets": Trajet.objects.filter(car__etablissement_id=request.user.etablissement_id),
        "cars": Car.objects.filter(etablissement_id=request.user.etablissement_id), 
        'datatable' :True
    }

    return render(request, 'transport/trajet_list.html', context=context)


@login_required
@staff_required
def AbonnementListDetail(request,pk):
    trajet = Trajet.objects.get(pk=pk)
    
    context = {
        "titre": f"Liste des Abonnées {trajet}",
        "info": f"Liste des Trajets {trajet}",
        "info2": f"Liste des Trajets  {trajet}",
        'datatable' :True,
        'trajet' :  trajet,
    }
    return render(request, 'transport/abonnement_list.html', context=context)


@login_required
@staff_required
def AbonnementListAll(request):
    
    context = {
        "titre": f"Liste des Abonnements",
        "info": f"Liste des Abonnements",
        "info2": f"Liste des Abonnements",
        'datatable' :True,
        'abonnements' :  Abonnement.objects.all(),
    }
    return render(request, 'transport/abonnement_list_all.html', context=context)