from django.shortcuts import render, redirect
from .models import User
from .forms import UserCreationForm
from decorators.decorators import staff_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

# Création d'un nouvel utilisateur
@login_required
@staff_required
def create_user(request):
    """
    Vue permettant à un utilisateur staff de créer un nouvel utilisateur.
    Un email est envoyé à l'utilisateur avec ses informations d'accès.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)  # Formulaire de création d'utilisateur
        if form.is_valid():
            user = form.save(commit=False)
            user.etablissement = request.user.etablissement  # Assigner l'établissement de l'utilisateur actuel
            user.is_staff = True  # L'utilisateur créé sera un staff par défaut
            user.save()

            # Envoi de l'email de confirmation à l'utilisateur
            subject = f'Votre compte {request.user.etablissement} a été créé'
            context = {
                'user': user,
                'password': form.cleaned_data['password1'],  # Mot de passe de l'utilisateur
                'site_url': request.build_absolute_uri(reverse('login')),  # URL de la page de connexion
                'image_url': request.user.etablissement.logo.url,  # URL du logo de l'établissement
            }

            # Générer l'email en HTML et texte brut
            html_message = render_to_string('auths/welcome_email_with_image.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],  # Email du nouvel utilisateur
            )
            email.attach_alternative(html_message, "text/html")  # Attachement du message HTML à l'email

            email.send()  # Envoi de l'email

            # Message de succès
            messages.success(request, f"Utilisateur {user} ajouté avec succès")
            return redirect('list_user')  # Rediriger vers la liste des utilisateurs

    else:
        form = UserCreationForm()  # Formulaire vide au premier chargement

    context = {
        "titre": "Nouvel Utilisateur",  # Titre de la page
        "info": "Nouvel Utilisateur",  # Informations affichées sur la page
        "info2": "Nouvel Utilisateur",  # Sous-titre
        "datatable": False,  # Indiquer que ce n'est pas une page de tableau de données
        "form": form  # Formulaire à afficher
    }

    return render(request, 'auths/register.html', context=context)

# Liste des utilisateurs (non étudiants)
@login_required
@staff_required
def userList(request):
    """
    Vue affichant la liste des utilisateurs qui ne sont pas des étudiants.
    Cette vue est accessible uniquement par un utilisateur avec le rôle de staff.
    """
    context = {
        "titre": "Utilisateurs",  # Titre de la page
        "info": "Liste",  # Informations affichées sur la page
        "info2": "Utilisateurs",  # Sous-titre
        "datatable": True,  # Indiquer que c'est une page de tableau de données
        "users": User.objects.filter(etablissement=request.user.etablissement, is_student=False)  # Filtrage des utilisateurs
    }

    return render(request, 'auths/user_list.html', context=context)

# Redirection de l'utilisateur en fonction de son rôle
def redirection(request):
    """
    Rediriger l'utilisateur vers la page appropriée en fonction de son rôle :
    - Étudiant -> 'student_home'
    - Staff -> 'admin-home'
    - Enseignant -> 'teacher_home'
    """
    if request.user.is_authenticated:
        # Rediriger en fonction du type d'utilisateur
        if request.user.is_student:
            return redirect("student_home")  # Redirection vers la page des étudiants
        elif request.user.is_staff:
            return redirect("admin-home")  # Redirection vers la page du staff
        elif request.user.is_teacher:
            return redirect("teacher_home")  # Redirection vers la page des enseignants

    return redirect("login")  # Si l'utilisateur n'est pas authentifié, rediriger vers la page de connexion
