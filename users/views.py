from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .forms import (
    ProjectOwnerRegistrationForm, 
    InvestorRegistrationForm,
    CustomAuthenticationForm,
    ProfileUpdateForm,
    ProjectOwnerProfileUpdateForm,
    InvestorProfileUpdateForm
)
from .models import User, ProjectOwnerProfile, InvestorProfile


def register_choice(request):
    """Page de choix du type de compte"""
    return render(request, 'users/register_choice.html')


def register_porteur(request):
    """Inscription pour porteur de projet"""
    if request.method == 'POST':
        form = ProjectOwnerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
    else:
        form = ProjectOwnerRegistrationForm()
    
    return render(request, 'users/register_porteur.html', {'form': form})


def register_investisseur(request):
    """Inscription pour investisseur"""
    if request.method == 'POST':
        form = InvestorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
    else:
        form = InvestorRegistrationForm()
    
    return render(request, 'users/register_investisseur.html', {'form': form})


def register(request):
    """Page d'inscription générique (redirige vers le choix)"""
    return redirect('users:register_choice')


def login_view(request):
    """Page de connexion"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Gérer "Se souvenir de moi"
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(request, f'Bienvenue, {user.get_full_name() or user.username} !')
                
                # Rediriger vers la page demandée ou dashboard
                next_url = request.GET.get('next', 'users:dashboard')
                return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('core:home')


@login_required
def dashboard(request):
    """Tableau de bord utilisateur"""
    user = request.user
    context = {
        'user': user,
    }
    
    # Ajouter des données spécifiques selon le type d'utilisateur
    if user.user_type == 'porteur':
        from projects.models import Project
        context['my_projects'] = Project.objects.filter(owner=user).order_by('-created_at')[:5]
        context['projects_count'] = Project.objects.filter(owner=user).count()
        context['approved_count'] = Project.objects.filter(owner=user, status='approved').count()
        context['pending_count'] = Project.objects.filter(owner=user, status__in=['submitted', 'under_review']).count()
    
    elif user.user_type == 'investisseur':
        from projects.models import ProjectFavorite, Project
        context['favorite_projects'] = ProjectFavorite.objects.filter(user=user).select_related('project')[:5]
        context['favorites_count'] = ProjectFavorite.objects.filter(user=user).count()
        context['available_projects'] = Project.objects.filter(status='approved').count()
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """Page de profil utilisateur"""
    user = request.user
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        
        # Formulaire spécifique selon le type d'utilisateur
        profile_form = None
        if user.user_type == 'porteur':
            # Créer le profil s'il n'existe pas
            porteur_profile, created = ProjectOwnerProfile.objects.get_or_create(user=user)
            profile_form = ProjectOwnerProfileUpdateForm(
                request.POST, 
                instance=porteur_profile
            )
        elif user.user_type == 'investisseur':
            # Créer le profil s'il n'existe pas
            investisseur_profile, created = InvestorProfile.objects.get_or_create(user=user)
            profile_form = InvestorProfileUpdateForm(
                request.POST, 
                instance=investisseur_profile
            )
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('users:profile')
    else:
        user_form = ProfileUpdateForm(instance=user)
        profile_form = None
        
        if user.user_type == 'porteur':
            # Créer le profil s'il n'existe pas
            porteur_profile, created = ProjectOwnerProfile.objects.get_or_create(user=user)
            profile_form = ProjectOwnerProfileUpdateForm(instance=porteur_profile)
        elif user.user_type == 'investisseur':
            # Créer le profil s'il n'existe pas
            investisseur_profile, created = InvestorProfile.objects.get_or_create(user=user)
            profile_form = InvestorProfileUpdateForm(instance=investisseur_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'users/profile.html', context)


# ============================================
# INTERFACE ADMINISTRATEUR
# ============================================

@staff_member_required
def admin_dashboard(request):
    """Dashboard administrateur avec statistiques globales"""
    from projects.models import Project
    from messaging.models import Message, Conversation
    from notifications.models import Notification
    
    # Statistiques utilisateurs
    total_users = User.objects.count()
    porteurs_count = User.objects.filter(user_type='porteur').count()
    investisseurs_count = User.objects.filter(user_type='investisseur').count()
    new_users_week = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    active_users_month = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Statistiques projets
    total_projects = Project.objects.count()
    pending_projects = Project.objects.filter(
        status__in=['submitted', 'under_review', 'revision_requested']
    ).count()
    approved_projects = Project.objects.filter(status='approved').count()
    rejected_projects = Project.objects.filter(status='rejected').count()
    
    # Statistiques par secteur
    projects_by_sector = Project.objects.values('sector').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Statistiques messagerie
    total_messages = Message.objects.count()
    total_conversations = Conversation.objects.count()
    messages_week = Message.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Statistiques notifications
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    # Activité récente (derniers utilisateurs)
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Projets récents
    recent_projects = Project.objects.order_by('-created_at')[:10].select_related('owner')
    
    # Messages récents
    recent_messages = Message.objects.order_by('-created_at')[:10].select_related(
        'sender', 'conversation'
    )
    
    context = {
        # Utilisateurs
        'total_users': total_users,
        'porteurs_count': porteurs_count,
        'investisseurs_count': investisseurs_count,
        'new_users_week': new_users_week,
        'active_users_month': active_users_month,
        
        # Projets
        'total_projects': total_projects,
        'pending_projects': pending_projects,
        'approved_projects': approved_projects,
        'rejected_projects': rejected_projects,
        'projects_by_sector': projects_by_sector,
        
        # Messagerie
        'total_messages': total_messages,
        'total_conversations': total_conversations,
        'messages_week': messages_week,
        
        # Notifications
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        
        # Activité récente
        'recent_users': recent_users,
        'recent_projects': recent_projects,
        'recent_messages': recent_messages,
    }
    
    return render(request, 'users/admin_dashboard.html', context)


@staff_member_required
def admin_users(request):
    """Gestion des utilisateurs"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filtres
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    is_active = request.GET.get('active')
    if is_active == 'true':
        users = users.filter(is_active=True)
    elif is_active == 'false':
        users = users.filter(is_active=False)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Statistiques
    total_count = User.objects.count()
    active_count = User.objects.filter(is_active=True).count()
    inactive_count = User.objects.filter(is_active=False).count()
    
    context = {
        'users': users,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
    }
    
    return render(request, 'users/admin_users.html', context)


@staff_member_required
def admin_user_detail(request, user_id):
    """Détail d'un utilisateur avec possibilité d'activation/désactivation"""
    user_obj = get_object_or_404(User, id=user_id)
    
    from projects.models import Project
    from messaging.models import Message
    
    # Statistiques de l'utilisateur
    if user_obj.user_type == 'porteur':
        projects_count = Project.objects.filter(owner=user_obj).count()
        approved_projects = Project.objects.filter(owner=user_obj, status='approved').count()
    else:
        projects_count = 0
        approved_projects = 0
    
    messages_sent = Message.objects.filter(sender=user_obj).count()
    
    # Projets de l'utilisateur
    user_projects = Project.objects.filter(owner=user_obj).order_by('-created_at')[:10] if user_obj.user_type == 'porteur' else []
    
    context = {
        'user_obj': user_obj,
        'projects_count': projects_count,
        'approved_projects': approved_projects,
        'messages_sent': messages_sent,
        'user_projects': user_projects,
    }
    
    return render(request, 'users/admin_user_detail.html', context)


@staff_member_required
def admin_toggle_user_status(request, user_id):
    """Activer/Désactiver un utilisateur"""
    if request.method == 'POST':
        user_obj = get_object_or_404(User, id=user_id)
        
        # Ne pas permettre de se désactiver soi-même
        if user_obj == request.user:
            messages.error(request, 'Vous ne pouvez pas modifier votre propre statut.')
            return redirect('users:admin_user_detail', user_id=user_id)
        
        # Toggle le statut
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        
        status = 'activé' if user_obj.is_active else 'désactivé'
        messages.success(request, f'Le compte de {user_obj.get_full_name()} a été {status}.')
        
        return redirect('users:admin_user_detail', user_id=user_id)
    
    return redirect('users:admin_users')


@staff_member_required
def admin_delete_user(request, user_id):
    """Supprimer un utilisateur"""
    if request.method == 'POST':
        user_obj = get_object_or_404(User, id=user_id)
        
        # Ne pas permettre de se supprimer soi-même
        if user_obj == request.user:
            messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
            return redirect('users:admin_user_detail', user_id=user_id)
        
        # Ne pas permettre de supprimer un super admin
        if user_obj.is_superuser:
            messages.error(request, 'Vous ne pouvez pas supprimer un compte super administrateur.')
            return redirect('users:admin_user_detail', user_id=user_id)
        
        user_name = user_obj.get_full_name()
        user_obj.delete()
        
        messages.success(request, f'Le compte de {user_name} a été supprimé définitivement.')
        return redirect('users:admin_users')
    
    return redirect('users:admin_users')


@staff_member_required
def admin_change_user_type(request, user_id):
    """Changer le type d'utilisateur (porteur <-> investisseur)"""
    if request.method == 'POST':
        user_obj = get_object_or_404(User, id=user_id)
        
        # Ne pas permettre de modifier son propre type
        if user_obj == request.user:
            messages.error(request, 'Vous ne pouvez pas modifier votre propre type de compte.')
            return redirect('users:admin_user_detail', user_id=user_id)
        
        new_type = request.POST.get('new_type')
        
        if new_type not in ['porteur', 'investisseur']:
            messages.error(request, 'Type de compte invalide.')
            return redirect('users:admin_user_detail', user_id=user_id)
        
        old_type = user_obj.get_user_type_display()
        user_obj.user_type = new_type
        user_obj.save()
        
        messages.success(
            request,
            f'Le type de compte de {user_obj.get_full_name()} a été changé de {old_type} à {user_obj.get_user_type_display()}.'
        )
        
        return redirect('users:admin_user_detail', user_id=user_id)
    
    return redirect('users:admin_users')
