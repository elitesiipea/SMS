# Open the Django shell by running:
# python manage.py shell

# Import necessary models
from evaluations.models import Note, Resultat

# Define the threshold values
MIN_AVERAGE = 1
MAX_AVERAGE = 10

# Query the Resultat instances with the given criteria
resultats_to_update = Resultat.objects.filter(
    note__classe__classe_universitaire=True,
    moyenne__lt=MAX_AVERAGE,
    moyenne__gt=MIN_AVERAGE
)

# Iterate through each Resultat and update the scores
for resultat in resultats_to_update:
    # Update scores to 10
    resultat.note_1 = 10
    resultat.note_2 = 10
    resultat.note_3 = 10
    resultat.note_partiel = 10
    
    # Save the updated Resultat instance
    resultat.save()

print(f"Updated {resultats_to_update.count()} Resultat instances.")