from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import BlogPost, Category
from .forms import BlogPostForm, CategoryForm


def is_admin(user):
    """Vérifie si l'utilisateur est admin"""
    return user.is_authenticated and user.user_type == 'admin'


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
    categories = Category.objects.all()
    
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
    
    return render(request, 'blog/blog.html', context)


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
    
    return render(request, 'blog/blog_detail.html', context)


# ============================================
# VUES ADMIN - GESTION DU BLOG
# ============================================

@login_required
@user_passes_test(is_admin)
def admin_content_dashboard(request):
    """Dashboard de gestion du contenu"""
    # Statistiques
    total_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(status='published').count()
    draft_posts = BlogPost.objects.filter(status='draft').count()
    total_categories = Category.objects.count()
    
    # Articles récents
    recent_posts = BlogPost.objects.select_related('author', 'category').order_by('-created_at')[:10]
    
    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_categories': total_categories,
        'recent_posts': recent_posts,
    }
    
    return render(request, 'blog/admin_content_dashboard.html', context)


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
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_status': status,
        'current_category': category_id,
        'search_query': search,
    }
    
    return render(request, 'blog/admin_blog_posts.html', context)


@login_required
@user_passes_test(is_admin)
def admin_blog_post_create(request):
    """Créer un nouvel article"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            
            messages.success(request, f"L'article '{post.title}' a été créé avec succès.")
            return redirect('blog:admin_blog_posts')
    else:
        form = BlogPostForm()
    
    return render(request, 'blog/admin_blog_post_form.html', {
        'form': form,
        'action': 'Créer',
    })


@login_required
@user_passes_test(is_admin)
def admin_blog_post_edit(request, post_id):
    """Modifier un article"""
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
            
            messages.success(request, f"L'article '{post.title}' a été modifié avec succès.")
            return redirect('blog:admin_blog_posts')
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'blog/admin_blog_post_form.html', {
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
        post.delete()
        
        messages.success(request, f"L'article '{title}' a été supprimé.")
        return redirect('blog:admin_blog_posts')
    
    return render(request, 'blog/admin_blog_post_confirm_delete.html', {'post': post})


@login_required
@user_passes_test(is_admin)
def admin_categories(request):
    """Liste des catégories"""
    categories = Category.objects.annotate(
        posts_count=Count('blog_posts')
    ).order_by('name')
    
    return render(request, 'blog/admin_categories.html', {
        'categories': categories,
    })


@login_required
@user_passes_test(is_admin)
def admin_category_create(request):
    """Créer une catégorie"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            
            messages.success(request, f"La catégorie '{category.name}' a été créée.")
            return redirect('blog:admin_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'blog/admin_category_form.html', {
        'form': form,
        'action': 'Créer',
    })


@login_required
@user_passes_test(is_admin)
def admin_category_edit(request, category_id):
    """Modifier une catégorie"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            
            messages.success(request, f"La catégorie '{category.name}' a été modifiée.")
            return redirect('blog:admin_categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'blog/admin_category_form.html', {
        'form': form,
        'category': category,
        'action': 'Modifier',
    })


@login_required
@user_passes_test(is_admin)
def admin_category_delete(request, category_id):
    """Supprimer une catégorie"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        
        messages.success(request, f"La catégorie '{name}' a été supprimée.")
        return redirect('blog:admin_categories')
    
    return render(request, 'blog/admin_category_confirm_delete.html', {'category': category})
