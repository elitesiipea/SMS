# Exécutez ce script dans le shell
import json
import random
from datetime import datetime
from django.db import transaction
from gestion_academique.models import Classe, Matiere, AnneeAcademique
from enseignant.models import Enseignant, ContratEnseignant

# Récupérer toutes les classes de l'établissement ID 1
classes = Classe.objects.filter(annee_academique__etablissement_id=1)

# Récupérer tous les enseignants (ID 1 à 40)
enseignants = Enseignant.objects.filter(id__range=(1, 40))

# Récupérer l'année académique ID 1
annee_academique = AnneeAcademique.objects.get(id=1)

data = []
contrat_count = 0

with transaction.atomic():
    for classe in classes:
        print(f"Traitement de la classe: {classe}")

        # Chercher les matières via le niveau et filière
        matieres = Matiere.objects.filter(
            unite__maquette__filiere=classe.filiere,
            unite__maquette__niveau=classe.niveau,
            unite__maquette__annee_academique=classe.annee_academique
        ).distinct()

        if matieres.exists():
            for matiere in matieres:
                # Choisir un enseignant au hasard parmi les 40
                enseignant = random.choice(list(enseignants))

                volume_horaire = matiere.volume_horaire or random.choice([20, 30, 40, 50, 60])
                taux_horaire = matiere.taux_horaire or random.choice([5000, 6000, 7000, 8000])
                progression = random.choice([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

                support_depose = random.random() > 0.3
                syllabus_depose = random.random() > 0.3
                cahier_de_texte = random.random() > 0.5
                notes = random.random() > 0.5
                closed = progression >= 100

                contrat = ContratEnseignant(
                    annee_academique=annee_academique,
                    enseignant=enseignant,
                    filiere=classe.filiere,
                    niveau=classe.niveau,
                    classe=classe,
                    matiere=matiere,
                    description=f"Contrat pour {matiere.nom} en {classe.nom}",
                    volume_horaire=volume_horaire,
                    progression=progression,
                    taux_horaire=taux_horaire,
                    support_depose=support_depose,
                    syllabus_depose=syllabus_depose,
                    cahier_de_texte=cahier_de_texte,
                    notes=notes,
                    closed=closed,
                    created=datetime.now(),
                    date_update=datetime.now()
                )

                contrat.save()
                contrat_count += 1

                data.append({
                    "model": "enseignant.contratenseignant",
                    "pk": contrat.id,
                    "fields": {
                        "annee_academique": annee_academique.id,
                        "enseignant": enseignant.id,
                        "filiere": classe.filiere.id,
                        "niveau": classe.niveau.id,
                        "classe": classe.id,
                        "matiere": matiere.id,
                        "description": f"Contrat pour {matiere.nom} en {classe.nom}",
                        "volume_horaire": volume_horaire,
                        "progression": progression,
                        "taux_horaire": taux_horaire,
                        "support": None,
                        "syllabus": None,
                        "support_depose": support_depose,
                        "syllabus_depose": syllabus_depose,
                        "cahier_de_texte": cahier_de_texte,
                        "notes": notes,
                        "closed": closed,
                        "created": contrat.created.isoformat(),
                        "date_update": contrat.date_update.isoformat(),
                        "demande_accompte": False,
                        "demande_traitee": False,
                        "numero_cheque": "",
                        "cheque_retire": False
                    }
                })

        else:
            print(f"  Pas de matières trouvées pour {classe}")

# Sauvegarder dans un fichier JSON
with open('../../../fixtures/2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ {contrat_count} contrats générés et sauvegardés dans '2.json'")