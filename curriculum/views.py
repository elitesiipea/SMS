from django.shortcuts import render, reverse, redirect
# Create your views here.
from decorators.decorators import student_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.forms import inlineformset_factory
from .models import Resume, Information, Data
from .forms import InformationForm, DataForm, ResumeForm
from django.contrib import messages

@login_required
@student_required
def student_cv(request):
    resume, created = Resume.objects.get_or_create(etudiant=request.user.etudiant)
    InformationFormSet = inlineformset_factory(Resume, Information, form=InformationForm, extra=0, can_delete=False)
    DataFormSet = inlineformset_factory(Resume, Data, form=DataForm, extra=0, can_delete=False)

    if request.method == 'POST':
        resume_form = ResumeForm(request.POST, instance=resume)
        info_formset = InformationFormSet(request.POST, instance=resume)
        data_formset = DataFormSet(request.POST, instance=resume)
        try:
            if resume_form.is_valid() and data_formset.is_valid() and info_formset.is_valid() :
                resume_form.save()
                info_formset.save()
                data_formset.save()
                messages.success(request, f'Données enregistrées avec succès !')
                return redirect('student_cv')
            else:
                # If the forms are not valid, display the error messages
                error_messages = []
                if not resume_form.is_valid():
                    error_messages.extend(resume_form.errors.values())
                if not data_formset.is_valid():
                    for form in data_formset:
                        if form.errors:
                            error_messages.extend(form.errors.values())
                
                for error_msg in error_messages:
                    messages.error(request, error_msg)
        except Exception as error:
            messages.error(request, error)
    else:
        resume_form = ResumeForm(instance=resume)
        info_formset = InformationFormSet(instance=resume)
        data_formset = DataFormSet(instance=resume)
    
    context = {
        'titre' : 'Mon Cv',
        'student_print' : True,
        'resume' : resume,
        'base_url' : request.build_absolute_uri('/'),
        'url': reverse('student_cv_shared', kwargs={'code': resume.etudiant.code_paiement})[1:],
       
        'resume_form': resume_form,
        'info_formset': info_formset,
        'data_formset': data_formset,
        'cv' : True

    }
    return render(request,'curriculum/cv.html', context=context)


def delete_info_or_data(request,element, pk):
    if element == "data":
        try:
            data = get_object_or_404(Data, pk=pk,resume__etudiant=request.user.etudiant)
            data.delete()
            messages.success(request, f'Données supprimée avec succès !')
        except:
            messages.success(request, f'Impossible supprimer cet élement !')
        return redirect('student_cv')

    if element == "info":
        try:
            data = get_object_or_404(Information, pk=pk,resume__etudiant=request.user.etudiant)
            data.delete()
            messages.success(request, f'Données supprimée avec succès !')
        except:
            messages.success(request, f'Impossible supprimer cet élement !')
        return redirect('student_cv')

    if element == "create_data":
        try:
            data = Data.objects.create(resume=request.user.etudiant.resume,nature="",intitule="")
        except:
            pass
        return redirect('student_cv')

    if element == "create_info":
        try:
            data = Information.objects.create(resume=request.user.etudiant.resume,nature="",intitule="",etablissement="", debut="", fin="", )
        except:
            pass
        return redirect('student_cv')


def student_cv_shared(request,code):
    resume, created = Resume.objects.get_or_create(etudiant__code_paiement=code)
    context = {
        'titre' : f'CV {resume.etudiant}',
        'student_print' : True,
        'resume' : resume,
        'shared' : True,
        
        
    }
    return render(request,'curriculum/cv.html', context=context)


