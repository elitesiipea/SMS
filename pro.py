from inscription.models import Inscription
from evaluations.models import Resultat

    # Get all inscriptions with niveau BTS 1 or BTS 2
print("*************************WELCOME******************")
inscriptions = Inscription.objects.filter(
        niveau__nom__in=["BTS 1", "BTS 2"]
)
    
    # Filter inscriptions based on moyenne_totale
inscriptions_to_update = [
        inscription for inscription in inscriptions
        if inscription.moyenne_totale >= 10
]
    
for inscription in inscriptions_to_update:
        # Get all results related to the current inscription where moyenne is less than 10
        results = Resultat.objects.filter(
            etudiant=inscription,
            moyenne__lt=10
        )
        
        for result in results:
            # Update note_1, note_2, note_3, and note_partiel to 10
            result.note_1 = 11
            result.note_2 = 11
            result.note_3 = 11
            result.note_partiel = 11
            
            # Save the updated result
            result.save()
            print(f"Updated Result ID {result.id} for Student ID {result.etudiant.id}")

