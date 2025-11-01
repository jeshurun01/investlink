from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .forms import ContactForm
from .models import BlogPost, BlogCategory, ActivityLog


def home(request):
    """Page d'accueil"""
    return render(request, 'core/home.html')


def about(request):
    """Page À propos"""
    return render(request, 'core/about.html')


def blog(request):
    """Page Blog - Liste des articles"""
    # Récupérer les filtres
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    tag = request.GET.get('tag')
    
    # Base queryset - seulement les articles publiés
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category')
    
    # Filtre par catégorie
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Filtre par recherche
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filtre par tag
    if tag:
        posts = posts.filter(tags__icontains=tag)
    
    # Pagination
    paginator = Paginator(posts, 9)  # 9 articles par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Récupérer toutes les catégories pour le filtre
    categories = BlogCategory.objects.all()
    
    # Articles récents (sidebar)
    recent_posts = BlogPost.objects.filter(status='published')[:5]
    
    # Tags populaires (tous les tags uniques)
    all_tags = set()
    for post in BlogPost.objects.filter(status='published'):
        all_tags.update(post.get_tags_list())
    popular_tags = sorted(list(all_tags))[:10]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'recent_posts': recent_posts,
        'popular_tags': popular_tags,
        'search_query': search_query,
        'current_category': category_slug,
        'current_tag': tag,
    }
    
    return render(request, 'core/blog.html', context)


def blog_detail(request, slug):
    """Page détail d'un article de blog"""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Incrémenter le compteur de vues
    post.increment_views()
    
    # Articles similaires (même catégorie)
    related_posts = BlogPost.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'core/blog_detail.html', context)


def contact(request):
    """Page Contact avec formulaire"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Créer un message de contact dans la base de données
            from .models import ContactMessage
            
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Log de l'action
            ActivityLog.log(
                user=request.user if request.user.is_authenticated else None,
                action='create',
                entity_type='message',
                entity_id=contact_message.id,
                entity_name=f"{contact_message.name} - {contact_message.subject}",
                description=f"Nouveau message de contact reçu",
                request=request
            )
            
            messages.success(
                request, 
                'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.'
            )
            return redirect('core:contact')
    else:
        # Pré-remplir le formulaire si l'utilisateur est connecté
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name(),
                'email': request.user.email,
                'phone': getattr(request.user, 'phone', ''),
            }
        form = ContactForm(initial=initial_data)
    
    return render(request, 'core/contact.html', {'form': form})


def faq(request):
    """Page FAQ"""
    return render(request, 'core/faq.html')


def terms(request):
    """Page CGU"""
    return render(request, 'core/terms.html')


def privacy(request):
    """Page Politique de confidentialité"""
    return render(request, 'core/privacy.html')


def legal(request):
    """Page Mentions légales"""
    return render(request, 'core/legal.html')


# ============================================
# VUES ADMIN - GESTION DU CONTENU
# ============================================

def is_admin(user):
    """Vérifie si l'utilisateur est admin"""
    return user.is_authenticated and user.user_type == 'admin'


@login_required
@user_passes_test(is_admin)
def admin_content_dashboard(request):
    """Dashboard de gestion du contenu"""
    # Statistiques
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(status='published').count()
    draft_posts = BlogPost.objects.filter(status='draft').count()
    total_categories = BlogCategory.objects.count()
    
    # Articles récents
    recent_posts = BlogPost.objects.select_related('author', 'category').order_by('-created_at')[:10]
    
    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_categories': total_categories,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'core/admin_content_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_blog_posts(request):
    """Liste des articles de blog (admin)"""
    # Filtres
    status = request.GET.get('status', '')
    category_id = request.GET.get('category', '')
    search = request.GET.get('q', '')
    
    posts = BlogPost.objects.select_related('author', 'category').order_by('-created_at')
    
    if status:
        posts = posts.filter(status=status)
    
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(excerpt__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = BlogCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_status': status,
        'current_category': category_id,
        'search_query': search,
    }
    
    return render(request, 'core/admin_blog_posts.html', context)


@login_required
@user_passes_test(is_admin)
def admin_blog_post_create(request):
    """Créer un nouvel article"""
    from .forms import BlogPostForm
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            
            # Log de l'action
            ActivityLog.log(
                user=request.user,
                action='create',
                entity_type='blog_post',
                entity_id=post.id,
                entity_name=post.title,
                description=f"Création de l'article '{post.title}'",
                request=request
            )
            
            messages.success(request, f"L'article '{post.title}' a été créé avec succès.")
            return redirect('core:admin_blog_posts')
    else:
        form = BlogPostForm()
    
    return render(request, 'core/admin_blog_post_form.html', {
        'form': form,
        'action': 'Créer',
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_post_edit(request, post_id):
    """Modifier un article"""
    from .forms import BlogPostForm
    
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            old_status = post.status
            post = form.save(commit=False)
            
            # Si on publie pour la première fois
            if post.status == 'published' and old_status == 'draft' and not post.published_at:
                post.published_at = timezone.now()
            
            post.save()
            
            # Log de l'action
            action = 'publish' if post.status == 'published' and old_status == 'draft' else 'update'
            ActivityLog.log(
                user=request.user,
                action=action,
                entity_type='blog_post',
                entity_id=post.id,
                entity_name=post.title,
                description=f"Modification de l'article '{post.title}'",
                request=request
            )
            
            messages.success(request, f"L'article '{post.title}' a été modifié avec succès.")
            return redirect('core:admin_blog_posts')
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'core/admin_blog_post_form.html', {
        'form': form,
        'post': post,
        'action': 'Modifier',
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_post_delete(request, post_id):
    """Supprimer un article"""
    post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        title = post.title
        post_id = post.id
        post.delete()
        
        # Log de l'action
        ActivityLog.log(
            user=request.user,
            action='delete',
            entity_type='blog_post',
            entity_id=post_id,
            entity_name=title,
            description=f"Suppression de l'article '{title}'",
            request=request
        )
        
        messages.success(request, f"L'article '{title}' a été supprimé.")
        return redirect('core:admin_blog_posts')
    
    return render(request, 'core/admin_blog_post_confirm_delete.html', {'post': post})


@login_required
@user_passes_test(is_admin)
def admin_categories(request):
    """Liste des catégories"""
    categories = BlogCategory.objects.annotate(
        posts_count=Count('posts')
    ).order_by('name')
    
    return render(request, 'core/admin_categories.html', {
        'categories': categories,
    })


@login_required
@user_passes_test(is_admin)
def admin_category_create(request):
    """Créer une catégorie"""
    from .forms import BlogCategoryForm
    
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            
            # Log
            ActivityLog.log(
                user=request.user,
                action='create',
                entity_type='blog_category',
                entity_id=category.id,
                entity_name=category.name,
                description=f"Création de la catégorie '{category.name}'",
                request=request
            )
            
            messages.success(request, f"La catégorie '{category.name}' a été créée.")
            return redirect('core:admin_categories')
    else:
        form = BlogCategoryForm()
    
    return render(request, 'core/admin_category_form.html', {
        'form': form,
        'action': 'Créer',
    })


@login_required
@user_passes_test(is_admin)
def admin_category_edit(request, category_id):
    """Modifier une catégorie"""
    from .forms import BlogCategoryForm
    
    category = get_object_or_404(BlogCategory, id=category_id)
    
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            
            # Log
            ActivityLog.log(
                user=request.user,
                action='update',
                entity_type='blog_category',
                entity_id=category.id,
                entity_name=category.name,
                description=f"Modification de la catégorie '{category.name}'",
                request=request
            )
            
            messages.success(request, f"La catégorie '{category.name}' a été modifiée.")
            return redirect('core:admin_categories')
    else:
        form = BlogCategoryForm(instance=category)
    
    return render(request, 'core/admin_category_form.html', {
        'form': form,
        'category': category,
        'action': 'Modifier',
    })


@login_required
@user_passes_test(is_admin)
def admin_category_delete(request, category_id):
    """Supprimer une catégorie"""
    category = get_object_or_404(BlogCategory, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category_id = category.id
        category.delete()
        
        # Log
        ActivityLog.log(
            user=request.user,
            action='delete',
            entity_type='blog_category',
            entity_id=category_id,
            entity_name=name,
            description=f"Suppression de la catégorie '{name}'",
            request=request
        )
        
        messages.success(request, f"La catégorie '{name}' a été supprimée.")
        return redirect('core:admin_categories')
    
    return render(request, 'core/admin_category_confirm_delete.html', {'category': category})


# ============================================
# VUES ADMIN - LOGS/ACTIVITÉS
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_activity_logs(request):
    """Page des logs d'activités"""
    # Filtres
    user_id = request.GET.get('user', '')
    action = request.GET.get('action', '')
    entity_type = request.GET.get('entity_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('q', '')
    
    logs = ActivityLog.objects.select_related('user').order_by('-created_at')
    
    # Appliquer les filtres
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    if action:
        logs = logs.filter(action=action)
    
    if entity_type:
        logs = logs.filter(entity_type=entity_type)
    
    if date_from:
        logs = logs.filter(created_at__date__gte=date_from)
    
    if date_to:
        logs = logs.filter(created_at__date__lte=date_to)
    
    if search:
        logs = logs.filter(
            Q(entity_name__icontains=search) |
            Q(description__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Pour les filtres
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(is_active=True).order_by('email')
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'action_choices': ActivityLog.ACTION_CHOICES,
        'entity_choices': ActivityLog.ENTITY_CHOICES,
        'current_user': user_id,
        'current_action': action,
        'current_entity_type': entity_type,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search,
    }
    
    
    return render(request, 'core/admin_activity_logs.html', context)


# ============================================
# VUES ADMIN - MESSAGES DE CONTACT
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_contact_messages(request):
    """Liste des messages de contact"""
    from .models import ContactMessage
    
    # Filtres
    status = request.GET.get('status', '')
    search = request.GET.get('q', '')
    
    messages_list = ContactMessage.objects.select_related('user').order_by('-created_at')
    
    if status:
        messages_list = messages_list.filter(status=status)
    
    if search:
        messages_list = messages_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(subject__icontains=search) |
            Q(message__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': ContactMessage.objects.count(),
        'new': ContactMessage.objects.filter(status='new').count(),
        'read': ContactMessage.objects.filter(status='read').count(),
        'in_progress': ContactMessage.objects.filter(status='in_progress').count(),
        'resolved': ContactMessage.objects.filter(status='resolved').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'status_choices': ContactMessage.STATUS_CHOICES,
        'current_status': status,
        'search_query': search,
        'stats': stats,
    }
    
    return render(request, 'core/admin_contact_messages.html', context)


@login_required
@user_passes_test(is_admin)
def admin_contact_message_detail(request, message_id):
    """Détail d'un message de contact"""
    from .models import ContactMessage
    
    contact_message = get_object_or_404(ContactMessage, id=message_id)
    
    # Marquer comme lu si nouveau
    if contact_message.status == 'new':
        contact_message.mark_as_read()
        ActivityLog.log(
            user=request.user,
            action='view',
            entity_type='message',
            entity_id=contact_message.id,
            entity_name=f"{contact_message.name} - {contact_message.subject}",
            description="Consultation du message de contact",
            request=request
        )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            admin_notes = request.POST.get('admin_notes', '')
            
            old_status = contact_message.status
            contact_message.status = new_status
            if admin_notes:
                contact_message.admin_notes = admin_notes
            
            if new_status == 'resolved':
                from django.utils import timezone
                contact_message.resolved_at = timezone.now()
            
            contact_message.save()
            
            # Log
            ActivityLog.log(
                user=request.user,
                action='update',
                entity_type='message',
                entity_id=contact_message.id,
                entity_name=f"{contact_message.name} - {contact_message.subject}",
                description=f"Changement de statut: {old_status} → {new_status}",
                request=request
            )
            
            messages.success(request, "Le statut du message a été mis à jour.")
            return redirect('core:admin_contact_message_detail', message_id=message_id)
    
    context = {
        'contact_message': contact_message,
        'status_choices': ContactMessage.STATUS_CHOICES,
    }
    
    return render(request, 'core/admin_contact_message_detail.html', context)


