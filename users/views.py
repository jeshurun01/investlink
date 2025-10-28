from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
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


