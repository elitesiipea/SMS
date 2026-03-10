from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse , redirect
from decorators.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Note, Resultat
from gestion_academique.models  import (AnneeAcademique,Classe)
from django.shortcuts import render, redirect
from .forms import NoteForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .models import Note, Resultat
from .forms import ResultatForm
from django.forms import inlineformset_factory
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from inscription.models import Inscription
from gestion_academique.models import Maquette
import pandas as pd
from io import BytesIO

@login_required
@staff_required
def create_note(request, pk):
    classe = Classe.objects.get(pk=pk)

    if request.method == 'POST':
        form = NoteForm(classe, request.POST, request.FILES)
        if form.is_valid():
            matiere = form.cleaned_data['matiere']

            # Vérifier si une note existe déjà pour la même classe et la même matière
            if Note.objects.filter(classe=classe, matiere=matiere).exists():
                context = {
                    "titre": "Nouvelle Evaluation",
                    "info": f"{classe}",
                    "info2": "Nouvelle Evaluation",
                    "form": form,
                    "classe": classe,
                }
                messages.error(request, "Une note pour cette classe avec la même matière existe déjà.")
                return redirect(reverse('create_note', kwargs={'pk': classe.pk,}))

            note = form.save(commit=False)
            note.classe = classe
            note.matiere.cahier_de_texte = True
            note.matiere.notes = True

            # Save the uploaded Excel file
            note.fichier = request.FILES['fichier']
            note.save()

            # Process the Excel file and create Resultat objects
            excel_data = pd.read_excel(BytesIO(note.fichier.read()))
            for index, row in excel_data.iterrows():
                etudiant_id = row['Code']
                note_1 = row['Note1']
                note_2 = row['Note2']
                note_3 = row['Note3']
                note_partiel = row['Partiel']

                etudiant = Inscription.objects.get(id=etudiant_id)
                Resultat.objects.create(
                    note=note,
                    etudiant=etudiant,
                    note_1=note_1,
                    note_2=note_2,
                    note_3=note_3,
                    note_partiel=note_partiel
                )
                
            messages.success(request, f"La Note {note} a été ajouté avec succes")
            return redirect(reverse('classes_details', kwargs={'pk': note.classe.pk}))
    else:
        form = NoteForm(classe)

    context = {
        "titre": "Nouvelle Evaluation",
        "info": f"{classe}",
        "info2": "Nouvelle Evaluation",
        "form": form,
        "classe": classe
    }
    return render(request, 'evaluations/creation/create_note.html', context=context)

@login_required
@staff_required
def note_resultat_add_edit(request,pk):
    note = Note.objects.get(pk=pk)
    ResultatFormset = inlineformset_factory(Note, Resultat, form=ResultatForm, extra=0, can_delete=False)
    if request.method == 'POST':
        note_form = NoteForm(note.classe.pk, request.POST, instance=note)
        resultats_formset = ResultatFormset(request.POST, instance=note)
        if note_form.is_valid() and resultats_formset.is_valid():
            note_form.save()
            resultats_formset.save()
            # for etudiant in note.classe.effectifs.all():
            
            #     Resultat.objects.get_or_create(etudiant=etudiant, note=note)
            messages.success(request, f'Données enregistrées avec succès !')
            return redirect(reverse('evaluation_details', kwargs={'pk': note.pk, 'classe_id': note.classe.id}))
        else:
            messages.error(request, f'Une erreur est survenue !')
    else:
        note_form = NoteForm(note.classe.pk, instance=note)
        resultats_formset = ResultatFormset(instance=note)
    
    context = {
        "titre": f"Note {note}",
        "info": f"{note.classe}",
        "info2": "Nouvelle Notes",
        "note_form": note_form,
        "resultats_formset": resultats_formset,
        "note" :note,
        'read_only': True

    }
    return render(request,'evaluations/creation/resultat_formset.html', context=context)


@login_required
@staff_required
def evaluations_list(request):
    selected_annee_id = request.GET.get('annee_id')

    annees_academiques = AnneeAcademique.objects.filter(etablissement_id=request.user.etablissement.id).order_by('-created')
    evaluations = Note.objects.filter(classe__annee_academique__etablissement_id=request.user.etablissement.id)

    if selected_annee_id:

        evaluations = evaluations.filter(classe__annee_academique_id=selected_annee_id)
    else:
        evaluations = evaluations.filter(classe__annee_academique_id=request.user.etablissement.annee_academiques.last())

    context = {
        "titre": "Evaluations",
        "info": "Lites",
        "info2": "Evaluations",
        "evaluations": evaluations,
        "datatable": True,
        "can_select_annee": True,
        "annees_academiques": annees_academiques,
    }
    return render(request, 'evaluations/list.html', context=context)


@login_required
@staff_required
def evaluation_details(request ,pk, classe_id):
    evaluation = get_object_or_404(Note, pk=pk, classe_id=classe_id)
    context = {
        "titre": f"{evaluation}",
        "info": "Info",
        "info2": "Evaluation",
        "datatable": True,
        "resultats" : evaluation.note_resultat.all(),
        'note' : evaluation

    }
    return render(request, 'evaluations/details.html', context=context)




@login_required
@staff_required
def bulletins_semestre_1(request, classe_id):
    classe = get_object_or_404(Classe, pk=classe_id)
    context = {
        "titre": f"BULLETINS SEMESTRE 1 {classe}",
        "info": "BULLETINS SEMESTRE 1",
        "info2": f"BULLETINS SEMESTRE 1 {classe}",
        "datatable": False,
        "classe" : classe,
    }
    return render(request, 'evaluations/bulletins/semestre1.html', context=context)


@method_decorator([login_required, staff_required], name="dispatch")
class Bulletins_Semestre1(DetailView):
    model = Classe
    template_name = "evaluations/bulletins/semestre1.html"

    def get_context_data(self, **kwargs):
        context = super(Bulletins_Semestre1, self).get_context_data(**kwargs)
        
        context["notes"] = Resultat.objects.filter(
            note__classe_id=self.kwargs.get("pk"),
            note__matiere__matiere__unite__semestre__exact="SEMESTRE 1"
            )
        if self.object.classe_universitaire:
            context['rang'] = sorted(
                Inscription.objects.filter(classe_id=self.object.id, annee_academique_id=self.object.annee_academique.id),
                key=lambda t: (t.credit_obtenues_notes_semestre_1, t.moyenne1)
            )
        else:
            context['rang'] = sorted(
                Inscription.objects.filter(classe_id=self.object.id, annee_academique_id=self.object.annee_academique.id),
                key=lambda t: (t.moyenne1)
            )
        return context


@method_decorator([login_required, staff_required], name="dispatch")
class Bulletins_Semestre2(DetailView):
    model = Classe
    template_name = "evaluations/bulletins/semestre2.html"

    def get_context_data(self, **kwargs):
        context = super(Bulletins_Semestre2, self).get_context_data(**kwargs)
        
        context["notes"] = Resultat.objects.filter(
            note__classe_id=self.kwargs.get("pk"),
            note__matiere__matiere__unite__semestre__exact="SEMESTRE 2"
            )
        if self.object.classe_universitaire:
            context['rang'] = sorted(
                Inscription.objects.filter(classe_id=self.object.id, annee_academique_id=self.object.annee_academique.id),
                key=lambda t: (t.credit_obtenues_notes_semestre_2, t.moyenne2)
            )
            context['rang_annuel'] = sorted(Inscription.objects.filter(classe_id=self.object.id,annee_academique_id=self.object.annee_academique.id,),
                                        key=lambda t: (t.credit_total, t.moyenne_totale))
        else:
            context['rang'] = sorted(
                Inscription.objects.filter(classe_id=self.object.id, annee_academique_id=self.object.annee_academique.id),
                key=lambda t: (t.moyenne2)
            )
            context['rang_annuel'] = sorted(Inscription.objects.filter(classe_id=self.object.id,annee_academique_id=self.object.annee_academique.id,),
                                        key=lambda t: t.moyenne_totale,)
            
        
        return context
    
@method_decorator([login_required, staff_required], name="dispatch")
class Bulletins_Semestre3(DetailView):
    model = Classe
    template_name = "evaluations/bulletins/semestre3.html"

    def get_context_data(self, **kwargs):
        context = super(Bulletins_Semestre3, self).get_context_data(**kwargs)
        
        context["notes"] = Resultat.objects.filter(
            note__classe_id=self.kwargs.get("pk"),
            note__matiere__matiere__unite__semestre__exact="SEMESTRE 3"
            )
        if self.object.classe_universitaire:
            context['rang'] = sorted(
                Inscription.objects.filter(classe_id=self.object.id, annee_academique_id=self.object.annee_academique.id),
                key=lambda t: (t.credit_obtenues_notes_semestre_3, t.moyenne3)
            )
            context['rang_annuel'] = sorted(Inscription.objects.filter(classe_id=self.object.id,annee_academique_id=self.object.annee_academique.id,),
                                        key=lambda t: (t.credit_total, t.moyenne_totale))
        else:
            context['rang'] = sorted(
                Inscription.objects.filter(classe_id=self.object.id, annee_academique_id=self.object.annee_academique.id),
                key=lambda t: (t.moyenne3)
            )
            context['rang_annuel'] = sorted(Inscription.objects.filter(classe_id=self.object.id,annee_academique_id=self.object.annee_academique.id,),
                                        key=lambda t: t.moyenne_totale,)

        return context



@method_decorator([login_required, staff_required], name="dispatch")
class ProcesVerbalSemestre1(DetailView):
    model = Classe
    template_name = "evaluations/pv/semestre1.html"
    def get_context_data(self, **kwargs):
        context = super(ProcesVerbalSemestre1, self).get_context_data(**kwargs)
        maquette = Maquette.objects.filter(annee_academique=self.object.annee_academique, filiere=self.object.filiere, niveau=self.object.niveau).first()
        context["notes"] = Resultat.objects.filter(
            note__classe_id=self.kwargs.get("pk"),
            note__matiere__matiere__unite__semestre__exact="SEMESTRE 1"
            )
        context['maquette'] = maquette
        context['row'] = maquette.matiere_1_count +5
        return context


@method_decorator([login_required, staff_required], name="dispatch")
class ProcesVerbalSemestre2(DetailView):
    model = Classe
    template_name = "evaluations/pv/semestre2.html"
    def get_context_data(self, **kwargs):
        context = super(ProcesVerbalSemestre2, self).get_context_data(**kwargs)
        maquette = Maquette.objects.filter(annee_academique=self.object.annee_academique, filiere=self.object.filiere, niveau=self.object.niveau).first()
        context["notes"] = Resultat.objects.filter(
            note__classe_id=self.kwargs.get("pk"),
            note__matiere__matiere__unite__semestre__exact="SEMESTRE 2"
            )
        context['maquette'] = maquette
        context['row'] = maquette.matiere_2_count +5
        return context


@method_decorator([login_required, staff_required], name="dispatch")
class ProcesVerbalAnnuel(DetailView):
    model = Classe
    template_name = "evaluations/pv/annuel.html"
    def get_context_data(self, **kwargs):
        context = super(ProcesVerbalAnnuel, self).get_context_data(**kwargs)
        maquette = Maquette.objects.filter(annee_academique=self.object.annee_academique, filiere=self.object.filiere, niveau=self.object.niveau).first()

        context["notes"] = Resultat.objects.filter(
            note__classe_id=self.kwargs.get("pk"))
        context['maquette'] = maquette
        context['row'] = maquette.matiere_count + 5 
        return context
    
    
    
### statistiques

@method_decorator([login_required, staff_required], name="dispatch")
class StatistiquesSemestre1(DetailView):
    model = Classe
    template_name = "evaluations/stats/s1.html"
    def get_context_data(self, **kwargs):
        context = super(ProcesVerbalSemestre1, self).get_context_data(**kwargs)
        return context
