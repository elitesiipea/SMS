# from django.test import TestCase
# from django.urls import reverse
# from datetime import date
# from authentication.models import User
# from gestion_academique.models import Etablissement, AnneeAcademique
# from inscription.models import Inscription

# class HomeViewTest(TestCase):
#     """
#     Test de la vue `home` pour s'assurer qu'elle renvoie les bons contextes et comportements
#     en fonction des permissions et rôles de l'utilisateur.
#     """

#     def setUp(self):
#         """
#         Configuration de l'environnement avant chaque test.
#         """
#         # Création de l'établissement et d'un utilisateur
#         self.etablissement = Etablissement.objects.create(nom="Test Etablissement")
#         self.annee_academique = AnneeAcademique.objects.create(
#             etablissement=self.etablissement,
#             annee_debut=2024,
#             annee_fin=2025
#         )

#         # Création d'un utilisateur (enseignant)
#         self.user_teacher = User.objects.create_user(
#             email="teacher@test.com",
#             password="password123",
#             nom="Teacher",
#             prenom="One",
#             etablissement=self.etablissement,
#             is_staff=True,  # Utilisateur autorisé à accéder au site
#             is_teacher=True  # Cet utilisateur est un enseignant
#         )

#         # Création d'un étudiant
#         self.user_student = User.objects.create_user(
#             email="student@test.com",
#             password="password123",
#             nom="Student",
#             prenom="One",
#             etablissement=self.etablissement,
#             is_student=True  # Cet utilisateur est un étudiant
#         )

#         # Inscription d'un étudiant
#         self.inscription = Inscription.objects.create(
#             etudiant=self.user_student,
#             annee_academique=self.annee_academique,
#             confirmed=True
#         )

#     def test_home_view_authenticated_teacher(self):
#         """
#         Test si la vue home fonctionne pour un utilisateur enseignant authentifié.
#         """
#         self.client.login(username="teacher@test.com", password="password123")
        
#         response = self.client.get(reverse('home'))
        
#         # Vérifie que la page se charge avec le code 200
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'administration/uses/index.html')  # Vérifie que le bon template est utilisé
#         self.assertContains(response, "Accueil")  # Vérifie que la page contient "Accueil"
#         self.assertContains(response, "Tableau de Bord")  # Vérifie que la page contient "Tableau de Bord"
        
#         # Vérifie que le nombre d'étudiants est correct
#         self.assertIn('etudiants', response.context)
#         self.assertEqual(response.context['etudiants'].count(), 1)  # Un seul étudiant inscrit

#     def test_home_view_authenticated_student(self):
#         """
#         Test si la vue home fonctionne pour un utilisateur étudiant authentifié.
#         """
#         self.client.login(username="student@test.com", password="password123")
        
#         response = self.client.get(reverse('home'))
        
#         # Vérifie que la page se charge avec le code 200
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'administration/uses/index.html')  # Vérifie que le bon template est utilisé
#         self.assertContains(response, "Accueil")  # Vérifie que la page contient "Accueil"
#         self.assertContains(response, "Tableau de Bord")  # Vérifie que la page contient "Tableau de Bord"
        
#         # Vérifie que le nombre d'étudiants est correct (ce devrait être 1 pour l'exemple)
#         self.assertIn('etudiants', response.context)
#         self.assertEqual(response.context['etudiants'].count(), 1)

#     def test_home_view_without_login(self):
#         """
#         Test si l'accès à la vue home échoue lorsque l'utilisateur n'est pas connecté.
#         """
#         response = self.client.get(reverse('home'))
        
#         # Vérifie que l'utilisateur est redirigé vers la page de login
#         self.assertRedirects(response, '/accounts/login/?next=/')  # Redirection attendue si non connecté

#     def test_home_view_with_annee_id(self):
#         """
#         Test si la vue home prend en compte l'ID de l'année académique et filtre les étudiants.
#         """
#         self.client.login(username="teacher@test.com", password="password123")
        
#         response = self.client.get(reverse('home'), {'annee_id': self.annee_academique.id})
        
#         # Vérifie que la page se charge avec le code 200
#         self.assertEqual(response.status_code, 200)
        
#         # Vérifie que les étudiants de l'année académique sélectionnée sont bien récupérés
#         self.assertIn('etudiants', response.context)
#         self.assertEqual(response.context['etudiants'].count(), 1)  # Un étudiant inscrit dans cette année

#     def test_home_view_inscription_count(self):
#         """
#         Test si le nombre d'inscriptions du jour est correct.
#         """
#         # Connexion de l'utilisateur
#         self.client.login(username="teacher@test.com", password="password123")
        
#         # Réalisation d'une inscription d'étudiant
#         Inscription.objects.create(
#             etudiant=self.user_student,
#             annee_academique=self.annee_academique,
#             confirmed=True,
#             created=date.today()  # Simulation d'une inscription aujourd'hui
#         )
        
#         # Requête GET vers la vue home
#         response = self.client.get(reverse('home'))
        
#         # Vérifie que le nombre d'inscriptions du jour est correctement comptabilisé
#         self.assertEqual(response.context['inscriptions_du_jour'], 2)  # Le nombre d'inscriptions du jour doit être 2

#     def test_home_view_teacher_should_see_students(self):
#         """
#         Vérifie que l'enseignant voit bien les étudiants inscrits dans l'année académique.
#         """
#         self.client.login(username="teacher@test.com", password="password123")
        
#         response = self.client.get(reverse('home'))
        
#         # Vérifie que l'enseignant voit bien la liste des étudiants
#         self.assertIn('etudiants', response.context)
#         self.assertEqual(response.context['etudiants'].count(), 1)  # L'enseignant doit voir un étudiant
