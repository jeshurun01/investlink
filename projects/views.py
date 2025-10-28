from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Project, ProjectDocument
from .forms import ProjectSubmissionForm, ProjectUpdateForm, ProjectValidationForm
from notifications.models import Notification


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
    
    # Calculer les statistiques
    submitted_count = projects.filter(status='submitted').count()
    approved_count = projects.filter(status='approved').count()
    rejected_count = projects.filter(status='rejected').count()
    
    context = {
        'projects': projects,
        'submitted_count': submitted_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
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


# ============================================================================
# VUES DE VALIDATION ADMIN
# ============================================================================

@staff_member_required
def admin_pending_projects(request):
    """Liste des projets en attente de validation"""
    # Récupérer tous les projets sauf ceux approuvés
    projects = Project.objects.filter(
        status__in=['submitted', 'under_review', 'revision_requested']
    ).select_related('owner').order_by('status', '-created_at')
    
    # Statistiques
    stats = {
        'submitted': projects.filter(status='submitted').count(),
        'under_review': projects.filter(status='under_review').count(),
        'revision_requested': projects.filter(status='revision_requested').count(),
        'total': projects.count(),
    }
    
    context = {
        'projects': projects,
        'stats': stats,
    }
    return render(request, 'projects/admin_pending.html', context)


@staff_member_required
def admin_validate_project(request, slug):
    """Valider ou rejeter un projet"""
    project = get_object_or_404(Project, slug=slug)
    
    if request.method == 'POST':
        form = ProjectValidationForm(request.POST, instance=project)
        if form.is_valid():
            previous_status = project.status
            project = form.save(commit=False)
            
            # Si le projet est validé, définir la date de publication
            if project.status == 'approved' and previous_status != 'approved':
                project.published_at = timezone.now()
            
            project.save()
            
            # Créer une notification pour le porteur
            notification_messages = {
                'approved': f'Félicitations ! Votre projet "{project.title}" a été validé et est maintenant visible publiquement.',
                'rejected': f'Votre projet "{project.title}" a été refusé. Raison : {project.rejection_reason}',
                'revision_requested': f'Des révisions sont demandées pour votre projet "{project.title}". Consultez les notes administratives pour plus de détails.',
                'under_review': f'Votre projet "{project.title}" est en cours d\'examen par notre équipe.',
            }
            
            notification_types = {
                'approved': 'project_approved',
                'rejected': 'project_rejected',
                'revision_requested': 'project_revision',
                'under_review': 'project_submitted',
            }
            
            if project.status in notification_messages:
                Notification.objects.create(
                    recipient=project.owner,
                    notification_type=notification_types[project.status],
                    title=f'Mise à jour du statut de votre projet',
                    message=notification_messages[project.status],
                    link=project.get_absolute_url()
                )
            
            messages.success(
                request,
                f'Le projet "{project.title}" a été mis à jour avec le statut : {project.get_status_display()}'
            )
            return redirect('projects:admin_pending')
    else:
        form = ProjectValidationForm(instance=project)
    
    # Charger les documents du projet
    documents = project.documents.all()
    
    context = {
        'project': project,
        'form': form,
        'documents': documents,
    }
    return render(request, 'projects/admin_validate.html', context)


@staff_member_required
def admin_all_projects(request):
    """Liste de tous les projets (pour les administrateurs)"""
    projects = Project.objects.all().select_related('owner').order_by('-created_at')
    
    # Filtres
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)
    
    sector = request.GET.get('sector')
    if sector:
        projects = projects.filter(sector=sector)
    
    # Statistiques globales
    stats = {
        'total': Project.objects.count(),
        'submitted': Project.objects.filter(status='submitted').count(),
        'under_review': Project.objects.filter(status='under_review').count(),
        'approved': Project.objects.filter(status='approved').count(),
        'rejected': Project.objects.filter(status='rejected').count(),
        'revision_requested': Project.objects.filter(status='revision_requested').count(),
    }
    
    context = {
        'projects': projects,
        'stats': stats,
        'status_choices': Project.STATUS_CHOICES,
        'sectors': Project.SECTOR_CHOICES,
    }
    return render(request, 'projects/admin_all_projects.html', context)



