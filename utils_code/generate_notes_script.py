import os
import sys
import django
import json
import random
from datetime import datetime

# Configurez Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMS.settings')
django.setup()

from django.db import transaction
from gestion_academique.models import Classe, AnneeAcademique
from enseignant.models import ContratEnseignant
from inscription.models import Inscription


def generate_notes_json():
    print("🚀 Génération du fichier JSON pour loaddata...")

    # Configuration
    etablissement_id = 1
    annee_academique_id = 1

    # Récupération des données
    classes = Classe.objects.filter(annee_academique__etablissement_id=etablissement_id)
    annee_academique = AnneeAcademique.objects.get(id=annee_academique_id)

    data = []
    note_pk = 1000  # Commencer à un PK élevé pour éviter les conflits
    resultat_pk = 5000

    for idx, classe in enumerate(classes, 1):
        print(f"[{idx}/{classes.count()}] Traitement de: {classe.nom}")

        # Contrats (matières) de la classe
        contrats = ContratEnseignant.objects.filter(classe=classe)

        # Étudiants de la classe
        inscriptions = Inscription.objects.filter(classe=classe, annee_academique=annee_academique)

        if not contrats.exists() or not inscriptions.exists():
            continue

        for contrat in contrats:
            print(f"   📚 Matière: {contrat.matiere.nom}")

            # Créer l'entrée Note
            note_data = {
                "model": "evaluations.note",
                "pk": note_pk,
                "fields": {
                    "classe": classe.id,
                    "matiere": contrat.id,
                    "use_note_1": True,
                    "use_note_2": True,
                    "use_note_3": True,
                    "use_note_partiel": True,
                    "partiel_uniquement": False,
                    "fichier": "",
                    "coefficient_note_partiel": 2 if classe.classe_universitaire else 1,
                    "coeeficient_matiere": contrat.matiere.coefficient,
                    "active": True,
                    "created": "2024-09-01T08:00:00Z",
                    "date_update": "2024-12-01T14:30:00Z"
                }
            }
            data.append(note_data)

            # Créer les résultats pour chaque étudiant
            for inscription in inscriptions:
                # Générer des notes réalistes
                def generate_note():
                    if random.random() < 0.7:
                        return round(random.uniform(8, 16), 2)
                    return round(random.uniform(0, 20), 2)

                note_1 = generate_note()
                note_2 = generate_note()
                note_3 = generate_note()
                note_partiel = generate_note()

                # Calcul de la moyenne (simplifié)
                moyenne_calculee = round((note_1 + note_2 + note_3 + note_partiel) / 4, 2)
                moyenne_coefficient_calculee = round(moyenne_calculee * contrat.matiere.coefficient, 2)

                resultat_data = {
                    "model": "evaluations.resultat",
                    "pk": resultat_pk,
                    "fields": {
                        "note": note_pk,
                        "etudiant": inscription.id,
                        "note_1": note_1,
                        "note_2": note_2,
                        "note_3": note_3,
                        "note_partiel": note_partiel,
                        "non_classe": random.random() < 0.03,
                        "session": "SESSION 1" if random.random() > 0.5 else "SESSION 2",
                        "active": True,
                        "created": "2024-12-01T14:30:00Z",
                        "date_update": "2024-12-01T14:30:00Z",
                        "moyenne": moyenne_calculee,
                        "moyenne_coefficient": moyenne_coefficient_calculee,
                        "moyenne_unite": moyenne_calculee  # Simplifié
                    }
                }
                data.append(resultat_data)
                resultat_pk += 1

            note_pk += 1

    # Sauvegarder dans un fichier JSON
    filename = "notes.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Fichier généré: {filename}")
    print(f"📊 Statistiques:")
    print(f"   - Total objets: {len(data)}")
    print(f"   - Notes: {sum(1 for item in data if item['model'] == 'evaluations.note')}")
    print(f"   - Résultats: {sum(1 for item in data if item['model'] == 'evaluations.resultat')}")

    return filename


if __name__ == '__main__':
    filename = generate_notes_json()

    # Instructions
    print("\n📋 Instructions:")
    print(f"1. Le fichier a été créé: {filename}")
    print("2. Placez-le dans le dossier fixtures/ de votre projet")
    print("3. Chargez les données avec:")
    print(f"   python manage.py loaddata {filename}")
    print("\n⚠️  Note: Assurez-vous que les IDs référencés existent dans votre base:")
    print("   - Les classes ID doivent exister")
    print("   - Les contrats (ContratEnseignant) ID doivent exister")
    print("   - Les inscriptions (Inscription) ID doivent exister")