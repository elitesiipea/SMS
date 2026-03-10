from django.shortcuts import render, redirect , get_object_or_404
from .forms import NotificationForm
from decorators.decorators import staff_required
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.http import JsonResponse
from django.contrib import messages


@login_required
@staff_required
def create_notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La notification a été créée avec succès.")
            return redirect('list_notification')  # Rediriger vers la liste des notifications après la création
    else:
        form = NotificationForm()
    
    context = {'form': form, 'edit':False}
    return render(request, 'notifications/create_notification.html', context)

@login_required
@staff_required
def edit_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()
            messages.success(request, "La notification a été modifiée avec succès.")
            return redirect('list_notification')  # Rediriger vers la liste des notifications après la modification
    else:
        form = NotificationForm(instance=notification)
    
    context = {'form': form, 'notification': notification, 'edit': True}
    return render(request, 'notifications/create_notification.html', context)


@login_required
@staff_required
def list_notification(request):
    context = {
        'notifications' : Notification.objects.filter(active=True),
        "titre" : "Notifications",
        "info": "Liste",
        "info2" : "Notifications",
        
        "datatable": True,
    }

    return render(request, 'notifications/liste.html', context)


@login_required
@staff_required
def delete_notification(request,notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.delete()
    messages.success(request, "La notification a été supprimée  avec succès.")
    return redirect('list_notification') 


def notification_list_json(request):
    notifications = Notification.objects.all()
    notifications_data = [
        {
            'id': notification.id,
            'titre': notification.titre,
            'description': notification.description,
            'active': notification.active,
            'created': notification.created.strftime('%Y-%m-%d %H:%M:%S'),
            'date_update': notification.date_update.strftime('%Y-%m-%d %H:%M:%S')
        }
        for notification in notifications
    ]
    return JsonResponse({'notifications': notifications_data})



def notification_list_json_detail(request,pk):
    notification = get_object_or_404(Notification, pk=pk)
    notifications_data = [
        {
            'id': notification.id,
            'titre': notification.titre,
            'description': notification.description,
            'active': notification.active,
            'created': notification.created.strftime('%Y-%m-%d %H:%M:%S'),
            'date_update': notification.date_update.strftime('%Y-%m-%d %H:%M:%S')
        }
        
    ]
    return JsonResponse({'notifications': notifications_data})