from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Avg
from decimal import Decimal
from .models import Project, ProjectDocument, ProjectFavorite, Investment, ProjectPerformance
from .forms import ProjectSubmissionForm, ProjectUpdateForm, ProjectValidationForm
from notifications.models import Notification
from core.models import ActivityLog


def project_list(request):
    """Liste des projets validés avec statistiques globales"""
    projects = Project.objects.filter(status='approved').select_related('owner')
    
    # Statistiques globales de la plateforme
    total_projects = projects.count()
    total_funding = projects.aggregate(total=Sum('funding_goal'))['total'] or 0
    
    # Calcul du ROI moyen global (basé sur les investissements confirmés)
    confirmed_investments = Investment.objects.filter(status='confirmed')
    avg_roi = Decimal('0')
    if confirmed_investments.exists():
        total_invested = confirmed_investments.aggregate(total=Sum('amount'))['total'] or 0
        total_current = confirmed_investments.aggregate(total=Sum('current_value'))['total'] or 0
        if total_invested > 0:
            avg_roi = ((total_current - total_invested) / total_invested) * 100
    
    # Statistiques par secteur
    sector_stats = []
    for sector_code, sector_name in Project.SECTOR_CHOICES:
        sector_projects = projects.filter(sector=sector_code)
        sector_count = sector_projects.count()
        sector_funding = sector_projects.aggregate(total=Sum('funding_goal'))['total'] or 0
        
        # ROI moyen du secteur
        sector_investments = confirmed_investments.filter(project__sector=sector_code)
        sector_roi = Decimal('0')
        if sector_investments.exists():
            sector_invested = sector_investments.aggregate(total=Sum('amount'))['total'] or 0
            sector_current = sector_investments.aggregate(total=Sum('current_value'))['total'] or 0
            if sector_invested > 0:
                sector_roi = ((sector_current - sector_invested) / sector_invested) * 100
        
        sector_stats.append({
            'code': sector_code,
            'name': sector_name,
            'count': sector_count,
            'funding': sector_funding,
            'roi': sector_roi,
        })
    
    # Trier les secteurs par nombre de projets
    sector_stats.sort(key=lambda x: x['count'], reverse=True)
    
    # Filtres
    sector = request.GET.get('sector')
    if sector:
        projects = projects.filter(sector=sector)
    
    search = request.GET.get('search')
    if search:
        projects = projects.filter(title__icontains=search)
    
    # Si l'utilisateur est un investisseur connecté, récupérer ses favoris
    user_favorites = []
    if request.user.is_authenticated and request.user.user_type == 'investisseur':
        user_favorites = list(
            ProjectFavorite.objects.filter(user=request.user).values_list('project_id', flat=True)
        )
    
    # Ajouter l'attribut is_favorite à chaque projet
    projects_list = []
    for project in projects:
        project.is_favorite = project.id in user_favorites
        projects_list.append(project)
    
    context = {
        'projects': projects_list,
        'sectors': Project.SECTOR_CHOICES,
        'total_projects': total_projects,
        'total_funding': total_funding,
        'avg_roi': avg_roi,
        'sector_stats': sector_stats,
        'selected_sector': sector,
    }
    return render(request, 'projects/list.html', context)


def project_detail(request, slug):
    """Détail d'un projet - Accès restreint aux investisseurs connectés"""
    project = get_object_or_404(Project, slug=slug)
    
    # Vérifier l'accès : seuls les investisseurs connectés peuvent voir les détails complets
    has_full_access = False
    show_signup_modal = False
    
    if request.user.is_authenticated:
        if request.user.user_type == 'investisseur' or request.user.is_staff:
            has_full_access = True
        elif request.user.user_type == 'porteur':
            # Les porteurs peuvent voir leurs propres projets
            if project.owner == request.user:
                has_full_access = True
    else:
        # Non connecté : on affiche une version limitée avec modal
        show_signup_modal = True
    
    # Incrémenter le compteur de vues seulement pour les accès complets
    if has_full_access:
        project.views_count += 1
        project.save(update_fields=['views_count'])
    
    # Charger les documents seulement si accès complet
    documents = project.documents.all() if has_full_access else []
    
    # Vérifier si c'est un favori (pour les investisseurs connectés)
    is_favorite = False
    if request.user.is_authenticated and request.user.user_type == 'investisseur':
        is_favorite = ProjectFavorite.objects.filter(user=request.user, project=project).exists()
    
    context = {
        'project': project,
        'documents': documents,
        'has_full_access': has_full_access,
        'show_signup_modal': show_signup_modal,
        'is_favorite': is_favorite,
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


# ============================================================
# GESTION DES FAVORIS
# ============================================================

@login_required
@require_POST
def toggle_favorite(request, project_id):
    """Ajouter ou retirer un projet des favoris (AJAX)"""
    # Vérifier que l'utilisateur est un investisseur
    if request.user.user_type != 'investisseur':
        return JsonResponse({
            'success': False,
            'error': 'Seuls les investisseurs peuvent ajouter des favoris.'
        }, status=403)
    
    project = get_object_or_404(Project, id=project_id)
    
    # Vérifier que le projet est validé
    if project.status != 'approved':
        return JsonResponse({
            'success': False,
            'error': 'Ce projet n\'est pas encore validé.'
        }, status=400)
    
    # Toggle favori
    favorite, created = ProjectFavorite.objects.get_or_create(
        user=request.user,
        project=project
    )
    
    if not created:
        # Favori existe déjà, on le supprime
        favorite.delete()
        is_favorite = False
        # Décrémenter le compteur
        project.favorites_count = max(0, project.favorites_count - 1)
        project.save(update_fields=['favorites_count'])
    else:
        is_favorite = True
        # Incrémenter le compteur
        project.favorites_count += 1
        project.save(update_fields=['favorites_count'])
    
    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite,
        'favorites_count': project.favorites_count
    })


@login_required
def my_favorites(request):
    """Liste des projets favoris de l'investisseur"""
    # Vérifier que l'utilisateur est un investisseur
    if request.user.user_type != 'investisseur':
        messages.error(request, 'Cette page est réservée aux investisseurs.')
        return redirect('core:home')
    
    # Récupérer les favoris avec les projets
    favorites = ProjectFavorite.objects.filter(
        user=request.user
    ).select_related('project', 'project__owner').order_by('-created_at')
    
    # Filtres
    sector = request.GET.get('sector')
    if sector:
        favorites = favorites.filter(project__sector=sector)
    
    search = request.GET.get('search')
    if search:
        favorites = favorites.filter(project__title__icontains=search)
    
    # Statistiques
    total_favorites = favorites.count()
    total_investment_goal = sum(f.project.funding_goal for f in favorites)
    
    context = {
        'favorites': favorites,
        'total_favorites': total_favorites,
        'total_investment_goal': total_investment_goal,
        'sectors': Project.SECTOR_CHOICES,
    }
    return render(request, 'projects/my_favorites.html', context)


# ============================================================
# GESTION DES INVESTISSEMENTS
# ============================================================

@login_required
def declare_investment(request, project_id):
    """Déclarer un investissement dans un projet"""
    # Vérifier que l'utilisateur est un investisseur
    if request.user.user_type != 'investisseur':
        messages.error(request, 'Seuls les investisseurs peuvent déclarer des investissements.')
        return redirect('core:home')
    
    project = get_object_or_404(Project, id=project_id, status='approved')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        investment_date = request.POST.get('investment_date')
        notes = request.POST.get('notes', '')
        
        try:
            amount = Decimal(amount)
            if amount < project.min_investment:
                messages.error(
                    request,
                    f'Le montant minimum d\'investissement est de ${project.min_investment}'
                )
            else:
                # Créer l'investissement
                investment = Investment.objects.create(
                    investor=request.user,
                    project=project,
                    amount=amount,
                    investment_date=investment_date,
                    notes=notes,
                    status='pending'
                )
                
                # Notifier l'admin
                Notification.objects.create(
                    recipient=project.owner,
                    notification_type='investment',
                    title='Nouvel investissement déclaré',
                    message=f'{request.user.get_full_name()} a déclaré un investissement de ${amount} dans votre projet "{project.title}".'
                )
                
                messages.success(
                    request,
                    'Votre investissement a été déclaré avec succès ! Il sera validé par l\'administrateur.'
                )
                return redirect('projects:my_investments')
        except (ValueError, TypeError):
            messages.error(request, 'Montant invalide.')
    
    context = {
        'project': project,
    }
    return render(request, 'projects/declare_investment.html', context)


@login_required
def my_investments(request):
    """Liste des investissements de l'investisseur"""
    # Vérifier que l'utilisateur est un investisseur
    if request.user.user_type != 'investisseur':
        messages.error(request, 'Cette page est réservée aux investisseurs.')
        return redirect('core:home')
    
    # Récupérer les investissements
    investments = Investment.objects.filter(
        investor=request.user
    ).select_related('project', 'project__owner').order_by('-investment_date')
    
    # Filtres
    status = request.GET.get('status')
    if status:
        investments = investments.filter(status=status)
    
    # Statistiques
    confirmed_investments = investments.filter(status='confirmed')
    stats = {
        'total_invested': confirmed_investments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0'),
        'total_investments': confirmed_investments.count(),
        'pending_count': investments.filter(status='pending').count(),
        'projects_count': confirmed_investments.values('project').distinct().count(),
    }
    
    # Calculer la valeur actuelle et le ROI
    total_current_value = Decimal('0')
    for investment in confirmed_investments:
        total_current_value += Decimal(str(investment.current_value))
    
    stats['current_value'] = total_current_value
    stats['total_roi'] = total_current_value - stats['total_invested']
    if stats['total_invested'] > 0:
        stats['roi_percentage'] = (stats['total_roi'] / stats['total_invested']) * 100
    else:
        stats['roi_percentage'] = 0
    
    context = {
        'investments': investments,
        'stats': stats,
        'status_choices': Investment.STATUS_CHOICES,
    }
    return render(request, 'projects/my_investments.html', context)


@login_required
def financial_dashboard(request):
    """Dashboard des états financiers mensuels de l'investisseur"""
    # Vérifier que l'utilisateur est un investisseur
    if request.user.user_type != 'investisseur':
        messages.error(request, 'Cette page est réservée aux investisseurs.')
        return redirect('core:home')
    
    # Récupérer les investissements confirmés
    investments = Investment.objects.filter(
        investor=request.user,
        status='confirmed'
    ).select_related('project').order_by('-investment_date')
    
    # Statistiques globales
    total_invested = investments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Calculer les valeurs actuelles et ROI
    portfolio_data = []
    total_current_value = Decimal('0')
    sector_distribution = {}
    
    for investment in investments:
        current_value = Decimal(str(investment.current_value))
        total_current_value += current_value
        
        portfolio_data.append({
            'investment': investment,
            'current_value': current_value,
            'roi_amount': investment.roi_amount,
            'roi_percentage': investment.roi_percentage,
        })
        
        # Distribution par secteur
        sector = investment.project.get_sector_display()
        if sector not in sector_distribution:
            sector_distribution[sector] = Decimal('0')
        sector_distribution[sector] += investment.amount
    
    # Calcul du ROI global
    total_roi = total_current_value - total_invested
    if total_invested > 0:
        roi_percentage = (total_roi / total_invested) * 100
    else:
        roi_percentage = 0
    
    # Préparer les données pour les graphiques
    sector_labels = list(sector_distribution.keys())
    sector_values = [float(v) for v in sector_distribution.values()]
    
    # Données d'évolution du portefeuille (simulation - à remplacer par des données réelles)
    # Pour l'instant, on utilise les dates d'investissement
    evolution_data = []
    cumulative_invested = Decimal('0')
    for investment in investments.order_by('investment_date'):
        cumulative_invested += investment.amount
        evolution_data.append({
            'date': investment.investment_date.strftime('%Y-%m-%d'),
            'invested': float(cumulative_invested),
            'value': float(cumulative_invested * Decimal('1.05'))  # Simulation +5%
        })
    
    context = {
        'investments': investments,
        'portfolio_data': portfolio_data,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_roi': total_roi,
        'roi_percentage': roi_percentage,
        'projects_count': investments.values('project').distinct().count(),
        'sector_labels': sector_labels,
        'sector_values': sector_values,
        'evolution_data': evolution_data,
    }
    return render(request, 'projects/financial_dashboard.html', context)


# ============================================================
# ADMINISTRATION - VALIDATION DES INVESTISSEMENTS
# ============================================================

@staff_member_required
def admin_pending_investments(request):
    """Liste des investissements en attente de validation"""
    # Récupérer tous les investissements
    investments = Investment.objects.all().select_related(
        'investor', 'project', 'project__owner'
    ).order_by('status', '-created_at')
    
    # Filtres
    status = request.GET.get('status')
    if status:
        investments = investments.filter(status=status)
    
    project_id = request.GET.get('project')
    if project_id:
        investments = investments.filter(project_id=project_id)
    
    # Statistiques
    stats = {
        'pending': Investment.objects.filter(status='pending').count(),
        'confirmed': Investment.objects.filter(status='confirmed').count(),
        'rejected': Investment.objects.filter(status='rejected').count(),
        'total': Investment.objects.count(),
        'total_amount_pending': Investment.objects.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0'),
        'total_amount_confirmed': Investment.objects.filter(status='confirmed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0'),
    }
    
    # Liste des projets pour le filtre
    projects_with_investments = Project.objects.filter(
        investments__isnull=False
    ).distinct().order_by('title')
    
    context = {
        'investments': investments,
        'stats': stats,
        'status_choices': Investment.STATUS_CHOICES,
        'projects': projects_with_investments,
    }
    return render(request, 'projects/admin_pending_investments.html', context)


@staff_member_required
def admin_validate_investment(request, investment_id):
    """Valider ou rejeter un investissement"""
    investment = get_object_or_404(
        Investment.objects.select_related('investor', 'project'),
        id=investment_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        previous_status = investment.status
        
        if action == 'confirm':
            investment.status = 'confirmed'
            investment.validated_at = timezone.now()
            investment.admin_notes = admin_notes
            investment.save()
            
            # Mettre à jour le financement actuel du projet
            project = investment.project
            project.current_funding += investment.amount
            project.save(update_fields=['current_funding'])
            
            # Log de l'action
            ActivityLog.log(
                user=request.user,
                action='validate',
                entity_type='investment',
                entity_id=investment.id,
                entity_name=f'{investment.investor.get_full_name()} - {investment.project.title}',
                description=f'Validation d\'un investissement de ${investment.amount} (Projet: {investment.project.title})',
                request=request
            )
            
            # Notifier l'investisseur
            Notification.objects.create(
                recipient=investment.investor,
                notification_type='investment_confirmed',
                title='Investissement confirmé',
                message=f'Votre investissement de ${investment.amount} dans le projet "{investment.project.title}" a été confirmé par l\'administrateur.',
                link=f'/projects/investments/'
            )
            
            # Notifier le porteur de projet
            Notification.objects.create(
                recipient=investment.project.owner,
                notification_type='investment_confirmed',
                title='Nouvel investissement confirmé',
                message=f'Un investissement de ${investment.amount} dans votre projet "{investment.project.title}" a été confirmé.',
                link=investment.project.get_absolute_url()
            )
            
            messages.success(
                request,
                f'L\'investissement de {investment.investor.get_full_name()} a été confirmé et le financement du projet a été mis à jour.'
            )
        
        elif action == 'reject':
            investment.status = 'rejected'
            investment.admin_notes = admin_notes
            investment.save()
            
            # Log de l'action
            ActivityLog.log(
                user=request.user,
                action='reject',
                entity_type='investment',
                entity_id=investment.id,
                entity_name=f'{investment.investor.get_full_name()} - {investment.project.title}',
                description=f'Rejet d\'un investissement de ${investment.amount} (Projet: {investment.project.title})',
                request=request
            )
            
            # Notifier l'investisseur
            Notification.objects.create(
                recipient=investment.investor,
                notification_type='investment_rejected',
                title='Investissement rejeté',
                message=f'Votre investissement de ${investment.amount} dans le projet "{investment.project.title}" a été rejeté. Raison: {admin_notes if admin_notes else "Non spécifiée"}',
                link=f'/projects/investments/'
            )
            
            messages.warning(
                request,
                f'L\'investissement de {investment.investor.get_full_name()} a été rejeté.'
            )
        
        return redirect('projects:admin_pending_investments')
    
    context = {
        'investment': investment,
    }
    return render(request, 'projects/admin_validate_investment.html', context)
