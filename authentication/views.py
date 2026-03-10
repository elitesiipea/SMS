from django.shortcuts import render, redirect
from .models import User
from .forms import UserCreationForm
from decorators.decorators import staff_required, teacher_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

@login_required
@staff_required
def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.etablissement = request.user.etablissement
            user.is_staff = True
            user.save()

            # Envoi de l'e-mail à l'utilisateur avec image
            subject = f'Votre compte {request.user.etablissement} a été créé'
            context = {
                'user': user,
                'password': form.cleaned_data['password1'],
                'site_url': request.build_absolute_uri(reverse('login')),  # Redirigez vers la page de connexion
                'image_url': request.user.etablissement.logo.url,  # Changez le chemin vers votre image
            }
            html_message = render_to_string('auths/welcome_email_with_image.html', context)
            plain_message = strip_tags(html_message)

            email = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            email.attach_alternative(html_message, "text/html")

            email.send()

            messages.success(request, f"Utilisateur {user} ajouté avec succès")
            return redirect('list_user')  # Redirigez vers la liste des utilisateurs ou une autre page
    else:
        form = UserCreationForm()
    context = {
        "titre": "Nouvel Utilisateur",
        "info": "Nouvel Utilisateur",
        "info2": "Nouvel Utilisateur",
        "datatable": False,
        "form": form
    }
    return render(request, 'auths/register.html', context=context)


@login_required
@staff_required
def userList(request):
    context = {
        "titre" : "Utilisateurs",
        "info": "Liste",
        "info2" : "Utilisateurs",
        "datatable": True,
        "users" : User.objects.filter(etablissement=request.user.etablissement, is_student=False)
    }
    return render(request,'auths/user_list.html', context=context)



def redirection(request):
    if request.user.is_authenticated:
        if request.user.is_student:
            return redirect("student_home")
        elif request.user.is_staff:
            return redirect("admin-home")
        elif request.user.is_teacher:
            return redirect("teacher_home")
    return redirect("login")

    

