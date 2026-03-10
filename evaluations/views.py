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
from django.db.models import Avg, Prefetch, Q, FloatField, Sum
from collections import defaultdict

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
        context = super().get_context_data(**kwargs)
        classe = self.object

        notes_semestre1 = Resultat.objects.filter(
            note__classe=classe,
            note__matiere__matiere__unite__semestre="SEMESTRE 1"
        ).select_related(
            "etudiant",
            "note__matiere__matiere__unite",
            "note__matiere__matiere"
        )
        
        inscriptions = Inscription.objects.filter(
            classe=classe,
            annee_academique=classe.annee_academique,
        ).select_related("etudiant__utilisateur", "filiere").prefetch_related(
            Prefetch(
                "insription_note", 
                queryset=notes_semestre1,
                to_attr="notes_semestre1",
            )
        )

        is_universitaire = self.object.classe_universitaire

        unite_notes = defaultdict(lambda: {"total_points": 0, "total_coefs": 0})
        for n in notes_semestre1:
            ue_id = n.note.matiere.matiere.unite_id
            coef = n.note.matiere.matiere.coefficient
            # 🐞 Correction ici : Le calcul des points d'unité doit aussi utiliser le coef.
            unite_notes[(n.etudiant_id, ue_id)]["total_points"] += n.moyenne * coef
            unite_notes[(n.etudiant_id, ue_id)]["total_coefs"] += coef

        moyennes_unites = {
            (et, ue): round(data["total_points"] / data["total_coefs"], 2) if data["total_coefs"] else 0
            for (et, ue), data in unite_notes.items()
        }
        
        for ins in inscriptions:
            notes = getattr(ins, "notes_semestre1", [])
            total_points_global = 0
            total_coefs_global = 0
            credit_total = 0
            ues_etudiant = {}

            for n in notes:
                ue = n.note.matiere.matiere.unite
                n.moyenne_unite_vue = moyennes_unites.get((n.etudiant_id, ue.id), 0)

                # 🐞 Correction ici : Le total des points doit toujours utiliser le coefficient.
                # La distinction pro/universitaire se fait sur la division finale.
                total_points_global += n.moyenne * n.note.matiere.matiere.coefficient
                total_coefs_global += n.note.matiere.matiere.coefficient

                if ue.id not in ues_etudiant:
                    credit_ue = getattr(ue, "credit", 0)
                    if not credit_ue:
                        credit_ue = sum(m.coefficient for m in ue.matieres.all())
                    ues_etudiant[ue.id] = {
                        "moyenne_ue": n.moyenne_unite_vue,
                        "credit_ue": credit_ue,
                        "matieres_valides": [],
                    }
                
                if n.moyenne >= 10:
                    ues_etudiant[ue.id]["matieres_valides"].append(
                        n.note.matiere.matiere.coefficient
                    )
            
            for ue_id, data in ues_etudiant.items():
                if is_universitaire:
                    if data["moyenne_ue"] >= 10:
                        credit_total += data["credit_ue"]
                    else:
                        credit_total += sum(data["matieres_valides"])
                else:
                    credit_total += sum(data["matieres_valides"])

            ins.credit_semestre1 = credit_total
            # 🐞 Correction ici : Utilisez le total_coefs_global qui est correct pour les deux
            # Mais la moyenne finale pour les universitaires doit être divisée par 30
            if is_universitaire:
                ins.moyenne1_semestre1 = round(total_points_global / 30, 2) if total_points_global else 0
            else:
                ins.moyenne1_semestre1 = round(total_points_global / total_coefs_global, 2) if total_coefs_global > 0 else 0
            
            ins.total_semestre1 = total_points_global
        
        if is_universitaire:
            rang_key = lambda t: (t.credit_semestre1, t.moyenne1_semestre1)
        else:
            rang_key = lambda t: t.moyenne1_semestre1

        inscriptions_rang = sorted(inscriptions, key=rang_key, reverse=True)
        for i, ins in enumerate(inscriptions_rang, start=1):
            ins.rang = i
        
        inscriptions_alpha = sorted(
            inscriptions,
            key=lambda t: (
                t.etudiant.utilisateur.nom.lower(),
                t.etudiant.utilisateur.prenom.lower()
            )
        )
        
        if inscriptions:
            moyenne_plus_forte = max(ins.moyenne1_semestre1 for ins in inscriptions)
            moyenne_plus_faible = min(ins.moyenne1_semestre1 for ins in inscriptions)
            moyenne_generale = round(sum(ins.moyenne1_semestre1 for ins in inscriptions) / len(inscriptions), 2)
        else:
            moyenne_plus_forte = moyenne_plus_faible = moyenne_generale = 0

        context.update({
            "notes": notes_semestre1,
            "rang_liste": inscriptions_rang,
            "bulletin_liste": inscriptions_alpha,
            "classe": classe,
            "titre": f"BULLETINS SEMESTRE 1 {classe}",
            "info": "BULLETINS SEMESTRE 1",
            "info2": f"BULLETINS SEMESTRE 1 {classe}",
            "datatable": False,
            "moyenne_plus_forte": moyenne_plus_forte,
            "moyenne_plus_faible": moyenne_plus_faible,
            "moyenne_generale": moyenne_generale,
        })
        return context

             


@method_decorator([login_required, staff_required], name="dispatch")
class Bulletins_Semestre2(DetailView):
    model = Classe
    template_name = "evaluations/bulletins/semestre2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classe = self.object

        inscriptions = Inscription.objects.filter(
            classe=classe,
            annee_academique=classe.annee_academique
        ).select_related("etudiant__utilisateur", "filiere")

        is_universitaire = self.object.classe_universitaire

        notes_qs = Resultat.objects.filter(
            Q(note__classe=classe),
            Q(note__matiere__matiere__unite__semestre__in=["SEMESTRE 1", "SEMESTRE 2"])
        ).select_related(
            "etudiant",
            "etudiant__etudiant__utilisateur",
            "note",
            "note__matiere__matiere__unite",
            "note__matiere__matiere"
        )

        notes_by_student = defaultdict(lambda: {"notes_s1": [], "notes_s2": []})
        for note in notes_qs:
            semestre = note.note.matiere.matiere.unite.semestre.upper()
            if semestre == "SEMESTRE 1":
                notes_by_student[note.etudiant_id]["notes_s1"].append(note)
            elif semestre == "SEMESTRE 2":
                notes_by_student[note.etudiant_id]["notes_s2"].append(note)

        bulletin_liste = []
        for ins in inscriptions:
            etudiant_id = ins.id
            notes_s1 = notes_by_student[etudiant_id]["notes_s1"]
            notes_s2 = notes_by_student[etudiant_id]["notes_s2"]

            # --- Calculs pour le Semestre 1 ---
            total_points_s1, total_coefs_s1, credit_total_s1 = 0, 0, 0
            ue_data_s1 = defaultdict(lambda: {'total_points': 0, 'total_coefs': 0, 'notes': []})
            if notes_s1:
                for n in notes_s1:
                    ue_id = n.note.matiere.matiere.unite.id
                    coef = n.note.matiere.matiere.coefficient
                    
                    total_points_s1 += n.moyenne * coef
                    total_coefs_s1 += coef

                    ue_data_s1[ue_id]['total_points'] += n.moyenne * coef
                    ue_data_s1[ue_id]['total_coefs'] += coef
                    ue_data_s1[ue_id]['notes'].append(n)
                
                # Calcul des crédits S1
                for ue_id, data in ue_data_s1.items():
                    ue_moyenne = round(data['total_points'] / data['total_coefs'], 2) if data['total_coefs'] else 0
                    if is_universitaire:
                        if ue_moyenne >= 10:
                            credit_total_s1 += data['total_coefs']
                        else:
                            credit_total_s1 += sum(n.note.matiere.matiere.coefficient for n in data['notes'] if n.moyenne >= 10)
                    else:
                        credit_total_s1 += sum(n.note.matiere.matiere.coefficient for n in data['notes'] if n.moyenne >= 10)

            moyenne1_semestre1 = round(total_points_s1 / 30, 2) if is_universitaire and total_points_s1 else (round(total_points_s1 / total_coefs_s1, 2) if total_coefs_s1 else 0)

            # --- Calculs pour le Semestre 2 ---
            total_points_s2, total_coefs_s2, credit_total_s2 = 0, 0, 0
            ue_data_s2 = defaultdict(lambda: {'total_points': 0, 'total_coefs': 0, 'notes': []})
            if notes_s2:
                for n in notes_s2:
                    ue_id = n.note.matiere.matiere.unite.id
                    coef = n.note.matiere.matiere.coefficient
                    
                    total_points_s2 += n.moyenne * coef
                    total_coefs_s2 += coef

                    ue_data_s2[ue_id]['total_points'] += n.moyenne * coef
                    ue_data_s2[ue_id]['total_coefs'] += coef
                    ue_data_s2[ue_id]['notes'].append(n)
                    
                # Calcul des crédits S2
                for ue_id, data in ue_data_s2.items():
                    ue_moyenne = round(data['total_points'] / data['total_coefs'], 2) if data['total_coefs'] else 0
                    if is_universitaire:
                        if ue_moyenne >= 10:
                            # 🐞 Correction ici : utilisez 'total_coefs' pour la cohérence
                            credit_total_s2 += data['total_coefs']
                        else:
                            credit_total_s2 += sum(n.note.matiere.matiere.coefficient for n in data['notes'] if n.moyenne >= 10)
                    else:
                        credit_total_s2 += sum(n.note.matiere.matiere.coefficient for n in data['notes'] if n.moyenne >= 10)
            
            moyenne2_semestre2 = round(total_points_s2 / 30, 2) if is_universitaire and total_points_s2 else (round(total_points_s2 / total_coefs_s2, 2) if total_coefs_s2 else 0)

            # --- Calculs annuels ---
            credit_total_calcule = credit_total_s1 + credit_total_s2
            moyenne_annuelle = round((moyenne1_semestre1 + moyenne2_semestre2) / 2, 2)

            # Création du dictionnaire pour le modèle
            etudiant_data = {
                'etudiant': ins.etudiant,
                'notes_semestre2': notes_s2,
                'moyenne1_semestre1': moyenne1_semestre1,
                'credit_semestre1': credit_total_s1,
                'moyenne2_semestre2': moyenne2_semestre2,
                'credit_semestre2': credit_total_s2,
                'credit_total_calcule': credit_total_calcule,
                'moyenne_annuelle': moyenne_annuelle,
                'total_points_s2': total_points_s2,
                'total_coefs_s2': total_coefs_s2
            }
            bulletin_liste.append(etudiant_data)

        # Le reste du code de classement...
        if is_universitaire:
            rang_key_s2 = lambda t: (t['credit_semestre2'], t['moyenne2_semestre2'])
            rang_key_annuel = lambda t: (t['credit_total_calcule'], t['moyenne_annuelle'])
        else:
            rang_key_s2 = lambda t: t['moyenne2_semestre2']
            rang_key_annuel = lambda t: t['moyenne_annuelle']

        inscriptions_rang_s2 = sorted(bulletin_liste, key=rang_key_s2, reverse=True)
        for i, data in enumerate(inscriptions_rang_s2, start=1):
            data['rang_s2'] = i

        inscriptions_rang_annuel = sorted(bulletin_liste, key=rang_key_annuel, reverse=True)
        for i, data in enumerate(inscriptions_rang_annuel, start=1):
            data['rang_annuel'] = i

        inscriptions_alpha = sorted(
            bulletin_liste,
            key=lambda t: (t['etudiant'].utilisateur.nom.lower(), t['etudiant'].utilisateur.prenom.lower())
        )

        moyenne_plus_forte_s2 = max(ins['moyenne2_semestre2'] for ins in bulletin_liste) if bulletin_liste else 0
        moyenne_plus_faible_s2 = min(ins['moyenne2_semestre2'] for ins in bulletin_liste) if bulletin_liste else 0
        moyenne_generale_s2 = round(sum(ins['moyenne2_semestre2'] for ins in bulletin_liste) / len(bulletin_liste), 2) if bulletin_liste else 0

        context.update({
            "bulletin_liste": inscriptions_alpha,
            "classe": classe,
            "titre": f"BULLETINS SEMESTRE 2 {classe}",
            "info": "BULLETINS SEMESTRE 2",
            "info2": f"BULLETINS SEMESTRE 2 {classe}",
            "datatable": False,
            "moyenne_plus_forte_s2": moyenne_plus_forte_s2,
            "moyenne_plus_faible_s2": moyenne_plus_faible_s2,
            "moyenne_generale_s2": moyenne_generale_s2,
        })
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
class ProcesVerbalBase(DetailView):
    model = Classe
    template_name = ""
    semestre = None
    row_attr = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classe = self.object

        # 🔹 Charger la maquette
        maquette = Maquette.objects.filter(
            annee_academique=classe.annee_academique,
            filiere=classe.filiere,
            niveau=classe.niveau
        ).first()

        # 🔹 Charger toutes les notes du semestre
        notes_qs = Resultat.objects.filter(note__classe=classe).select_related(
            "etudiant",
            "etudiant__etudiant",
            "etudiant__etudiant__utilisateur",
            "note",
            "note__matiere",
            "note__matiere__matiere",
            "note__matiere__matiere__unite"
        )
        if self.semestre:
            notes_qs = notes_qs.filter(note__matiere__matiere__unite__semestre=self.semestre)

        # 🔹 Charger inscriptions avec leurs notes
        inscriptions = Inscription.objects.filter(
            classe=classe,
            annee_academique=classe.annee_academique
        ).select_related(
            "etudiant__utilisateur",
            "filiere"
        ).prefetch_related(
            Prefetch("insription_note", queryset=notes_qs, to_attr="notes_semestre")
        )

        # 🔥 Vérifier si c’est une classe universitaire
        is_universitaire = self.object.classe_universitaire

        # ---- Calcul des moyennes d’UE ----
        from collections import defaultdict
        unite_notes = defaultdict(lambda: {"total": 0, "coef": 0})
        for n in notes_qs:
            ue_id = n.note.matiere.matiere.unite_id
            coef = n.note.matiere.matiere.coefficient
            unite_notes[(n.etudiant_id, ue_id)]["total"] += n.moyenne * (coef if is_universitaire else 1)
            unite_notes[(n.etudiant_id, ue_id)]["coef"] += (coef if is_universitaire else 1)

        moyennes_unites = {
            (et, ue): round(data["total"] / data["coef"], 2) if data["coef"] else 0
            for (et, ue), data in unite_notes.items()
        }

        for n in notes_qs:
            n.moyenne_unite_vue = moyennes_unites.get(
                (n.etudiant_id, n.note.matiere.matiere.unite_id), 0
            )

        # ---- Création d'une liste enrichie ----
        enriched_inscriptions = []

        for ins in inscriptions:
            notes = getattr(ins, "notes_semestre", [])

            # Moyenne générale
            total_points = 0
            total_coefs = 0
            for n in notes:
                if is_universitaire:
                    total_points += n.moyenne * n.note.matiere.matiere.coefficient
                    total_coefs += n.note.matiere.matiere.coefficient
                else:
                    total_points += n.moyenne
                    total_coefs += 1
            moyenne_semestre = round(total_points / total_coefs, 2) if total_coefs else 0

            # ---- Crédit avec la même logique que le bulletin ----
            credit_total = 0
            ues_etudiant = {}

            for n in notes:
                ue = n.note.matiere.matiere.unite
                n.moyenne_unite_vue = moyennes_unites.get((n.etudiant_id, ue.id), 0)

                if ue.id not in ues_etudiant:
                    credit_ue = getattr(ue, "credit", 0)
                    if not credit_ue:
                        credit_ue = sum(m.coefficient for m in ue.matieres.all())
                    ues_etudiant[ue.id] = {
                        "moyenne_ue": n.moyenne_unite_vue,
                        "credit_ue": credit_ue,
                        "matieres_valides": [],
                    }

                if n.moyenne >= 10:
                    ues_etudiant[ue.id]["matieres_valides"].append(
                        n.note.matiere.matiere.coefficient
                    )

            for ue_id, data in ues_etudiant.items():
                if is_universitaire:
                    if data["moyenne_ue"] >= 10:
                        credit_total += data["credit_ue"]
                    else:
                        credit_total += sum(data["matieres_valides"])
                else:
                    credit_total += sum(data["matieres_valides"])

            etudiant_data = {
                'etudiant': ins.etudiant,                       # <-- ins (Inscription) et non ins.etudiant
                'notes_semestre': notes,
                'moyenne1': moyenne_semestre,
                'credit_obtenues_notes_semestre_1': credit_total,
                'credit_notes_semestre_1': 30,         # fixe (ou récupère depuis la maquette si variable)
            }
            etudiant_data['decision'] = "ADMIS(E)" if etudiant_data['credit_obtenues_notes_semestre_1'] == 30 else "AJOURNE(E)"

            enriched_inscriptions.append(etudiant_data)

        # ---- Tri par rang ----
        if is_universitaire:
            rang_key = lambda t: (t['credit_obtenues_notes_semestre_1'], t['moyenne1'])
        else:
            rang_key = lambda t: t['moyenne1']

        pv_rang = sorted(enriched_inscriptions, key=rang_key, reverse=True)
        for i, etud in enumerate(pv_rang, start=1):
            etud['rang'] = i

        # ---- Tri alphabétique pour affichage ----
        pv_alpha = sorted(
            enriched_inscriptions,
            key=lambda t: (
                t['etudiant'].utilisateur.nom.lower(),
                t['etudiant'].utilisateur.prenom.lower()
            )
        )

        # ---- Contexte ----
        context.update({
            "maquette": maquette,
            "notes": notes_qs,
            "pv_rang": pv_rang,                  # classement par rang
            "bulletin_liste": pv_alpha,          # affichage alphabétique
            "classe": classe,
            "row": getattr(maquette, self.row_attr) + 5 if maquette and self.row_attr else 0,
        })
        return context


# ---- Classes filles ----
class ProcesVerbalSemestre1(ProcesVerbalBase):
    template_name = "evaluations/pv/semestre1.html"
    semestre = "SEMESTRE 1"
    row_attr = "matiere_1_count"

class ProcesVerbalSemestre2(ProcesVerbalBase):
    template_name = "evaluations/pv/semestre2.html"
    semestre = "SEMESTRE 2"
    row_attr = "matiere_2_count"

class ProcesVerbalAnnuel(ProcesVerbalBase):
    template_name = "evaluations/pv/annuel.html"
    semestre = None
    row_attr = "matiere_count"

  
    
### statistiques

@method_decorator([login_required, staff_required], name="dispatch")
class StatistiquesSemestre1(DetailView):
    model = Classe
    template_name = "evaluations/stats/s1.html"
    def get_context_data(self, **kwargs):
        context = super(ProcesVerbalSemestre1, self).get_context_data(**kwargs)
        return context

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .models import Resultat
from .forms import ResultatForm

class ResultatUpdateView(LoginRequiredMixin, UpdateView):
    """Vue pour modifier uniquement les notes et le statut de classement d'un étudiant"""
    model = Resultat
    form_class = ResultatForm
    template_name = "evaluations/resultat_update.html"
    
    def get_success_url(self):
        """Redirection après mise à jour"""
        return reverse_lazy('evaluation_details', kwargs={'pk': self.object.note.pk, 'classe_id': self.object.note.classe.pk})

    def get_object(self, queryset=None):
        """Récupère l'objet en s'assurant que l'utilisateur a les droits nécessaires"""
        return get_object_or_404(Resultat, pk=self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super(ResultatUpdateView, self).get_context_data(**kwargs)
        context["titre"] = f"Modifier {self.object}"
        context["info"] = "Modifier"
        context["info2"] = f"{self.object}"
        return context



