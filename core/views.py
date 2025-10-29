from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ContactForm
from .models import BlogPost, BlogCategory


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
            # Ici on pourrait envoyer un email
            # Pour l'instant on affiche juste un message de succès
            messages.success(
                request, 
                'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.'
            )
            return redirect('core:contact')
    else:
        form = ContactForm()
    
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

