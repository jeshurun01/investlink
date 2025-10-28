from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Project, ProjectDocument
from .forms import ProjectSubmissionForm, ProjectUpdateForm


def project_list(request):
    """Liste des projets validés"""
    projects = Project.objects.filter(status='approved').select_related('owner')
    
    # Filtres
    sector = request.GET.get('sector')
    if sector:
        projects = projects.filter(sector=sector)
    
    search = request.GET.get('search')
    if search:
        projects = projects.filter(title__icontains=search)
    
    context = {
        'projects': projects,
        'sectors': Project.SECTOR_CHOICES,
    }
    return render(request, 'projects/list.html', context)


def project_detail(request, slug):
    """Détail d'un projet"""
    project = get_object_or_404(Project, slug=slug)
    
    # Incrémenter le compteur de vues
    project.views_count += 1
    project.save(update_fields=['views_count'])
    
    # Charger les documents
    documents = project.documents.all()
    
    context = {
        'project': project,
        'documents': documents,
    }
    return render(request, 'projects/detail.html', context)


@login_required
def submit_project(request):
    """Soumettre un nouveau projet"""
    # Vérifier que l'utilisateur est un porteur de projet
    if request.user.user_type != 'porteur':
        messages.error(request, 'Seuls les porteurs de projets peuvent soumettre des projets.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Créer le projet
                    project = form.save(commit=False)
                    project.owner = request.user
                    project.status = 'submitted'
                    project.save()
                    
                    # Gérer les documents
                    # Business Plan
                    if form.cleaned_data.get('business_plan'):
                        ProjectDocument.objects.create(
                            project=project,
                            document_type='business_plan',
                            file=form.cleaned_data['business_plan'],
                            title='Business Plan'
                        )
                    
                    # Documents financiers
                    financial_files = request.FILES.getlist('financial_documents')
                    for file in financial_files:
                        ProjectDocument.objects.create(
                            project=project,
                            document_type='financial',
                            file=file,
                            title=file.name
                        )
                    
                    # Documents juridiques
                    legal_files = request.FILES.getlist('legal_documents')
                    for file in legal_files:
                        ProjectDocument.objects.create(
                            project=project,
                            document_type='legal',
                            file=file,
                            title=file.name
                        )
                    
                    messages.success(
                        request, 
                        f'Votre projet "{project.title}" a été soumis avec succès ! '
                        'Il sera examiné par notre équipe dans les prochains jours.'
                    )
                    return redirect('users:dashboard')
            
            except Exception as e:
                messages.error(request, f'Une erreur est survenue lors de la soumission : {str(e)}')
    else:
        form = ProjectSubmissionForm()
    
    return render(request, 'projects/submit.html', {'form': form})


@login_required
def edit_project(request, slug):
    """Modifier un projet"""
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    
    # Vérifier que le projet peut être modifié
    if project.status == 'approved':
        messages.error(request, 'Vous ne pouvez pas modifier un projet déjà validé.')
        return redirect('projects:my_projects')
    
    if request.method == 'POST':
        form = ProjectUpdateForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Le projet "{project.title}" a été mis à jour avec succès.')
            return redirect('projects:my_projects')
    else:
        form = ProjectUpdateForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'projects/edit.html', context)


@login_required
def my_projects(request):
    """Liste des projets du porteur connecté"""
    if request.user.user_type != 'porteur':
        messages.error(request, 'Cette page est réservée aux porteurs de projets.')
        return redirect('core:home')
    
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'projects': projects,
    }
    return render(request, 'projects/my_projects.html', context)


@login_required
def delete_project(request, slug):
    """Supprimer un projet (uniquement si non validé)"""
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    
    if project.status == 'approved':
        messages.error(request, 'Vous ne pouvez pas supprimer un projet validé.')
        return redirect('projects:my_projects')
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Le projet "{project_title}" a été supprimé.')
        return redirect('projects:my_projects')
    
    return render(request, 'projects/confirm_delete.html', {'project': project})


