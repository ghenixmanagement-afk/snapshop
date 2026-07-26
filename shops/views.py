import json

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count, F
from django.db.models.functions import Coalesce, Random

from .branding import THEME_PRESETS, build_shop_branding
from .forms import ShopForm
from .models import ModerationLog, Shop
from products.models import Product


@login_required
def seller_dashboard(request):
    if request.user.role != 'SELLER':
        raise Http404()
    shop = Shop.objects.filter(owner=request.user).first()
    
    # Récupérer les produits avec ses analytics
    products = []
    if shop:
        products = shop.products.select_related('subcategory', 'subcategory__category').prefetch_related('analytics').all()
    
    products_count = len(products) if shop else 0
    return render(
        request,
        'shops/dashboard.html',
        {
            'shop': shop,
            'products': products,
            'products_count': products_count,
            'rejection_reason': shop.rejection_reason if shop else '',
        },
    )


@login_required
def create_or_edit_shop(request):
    if request.user.role != 'SELLER':
        raise Http404()
    shop = Shop.objects.filter(owner=request.user).first()
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            needs_revalidation = (not obj.pk) or (obj.status in {'DRAFT', 'REJECTED'})
            if needs_revalidation:
                obj.status = 'PENDING'
                obj.rejection_reason = ''
                obj.is_active = False
            elif shop:
                # Keep current activation state for already moderated shops.
                obj.is_active = shop.is_active
            obj.save()
            return redirect('seller_dashboard')
    else:
        form = ShopForm(instance=shop)
    
    days = [
        ('monday', 'Lundi'),
        ('tuesday', 'Mardi'),
        ('wednesday', 'Mercredi'),
        ('thursday', 'Jeudi'),
        ('friday', 'Vendredi'),
        ('saturday', 'Samedi'),
        ('sunday', 'Dimanche'),
    ]
    
    shop_branding = build_shop_branding(shop) if shop else None
    return render(request, 'shops/shop_form.html', {
        'form': form,
        'shop': shop,
        'days': days,
        'shop_branding': shop_branding,
        'theme_presets_json': json.dumps(THEME_PRESETS),
    })


def shop_public(request, slug):
    shop = get_object_or_404(Shop, slug=slug, is_active=True)
    
    # Tous les produits en stock
    all_products = shop.products.filter(in_stock=True).select_related('shop', 'subcategory', 'subcategory__category')
    
    # Produits phares (top 6) triés par engagement (vues × 3 + avis × 5 + favoris × 2) + Random
    trending_products = (
        all_products
        .annotate(
            _vc=Coalesce('analytics__views_count', 0),
            _rc=Count('review', distinct=True),
            _fc=Count('favorite', distinct=True),
        )
        .annotate(
            engagement=F('_vc') * 3 + F('_rc') * 5 + F('_fc') * 2,
        )
        .order_by('-engagement', Random())[:6]
    )
    
    shop_branding = build_shop_branding(shop)
    og_image = shop_branding['logo_url']
    if not og_image:
        first_product = all_products.first()
        if first_product and first_product.image:
            og_image = first_product.image.url

    return render(
        request,
        'shops/shop_public.html',
        {
            'shop': shop,
            'all_products': all_products,
            'trending_products': trending_products,
            'shop_branding': shop_branding,
            'shop_url': request.build_absolute_uri(),
            'og_image': og_image,
        },
    )


@login_required
def moderation_dashboard(request):
    if not request.user.is_staff:
        raise Http404()
    if request.method == 'POST':
        shop = get_object_or_404(Shop, pk=request.POST.get('shop_id'))
        action = request.POST.get('action')
        reason = request.POST.get('rejection_reason', '').strip()
        if action == 'approve':
            shop.status = 'ACTIVE'
            shop.is_active = True
            shop.rejection_reason = ''
            shop.save(update_fields=['status', 'is_active', 'rejection_reason'])
            ModerationLog.objects.create(
                shop=shop,
                actor=request.user,
                action=ModerationLog.ACTION_APPROVE,
                note='',
            )
        elif action == 'reject':
            final_reason = reason or 'Non conforme aux exigences de publication.'
            shop.status = 'REJECTED'
            shop.is_active = False
            shop.rejection_reason = final_reason
            shop.save(update_fields=['status', 'is_active', 'rejection_reason'])
            ModerationLog.objects.create(
                shop=shop,
                actor=request.user,
                action=ModerationLog.ACTION_REJECT,
                note=final_reason,
            )
        return redirect('moderation_dashboard')
    pending_shops = Shop.objects.filter(status='PENDING').select_related('owner').order_by('created_at')
    recent_reviewed = Shop.objects.exclude(status='PENDING').select_related('owner').order_by('-created_at')[:10]
    moderation_logs = ModerationLog.objects.select_related('shop', 'actor').order_by('-created_at')[:30]
    return render(
        request,
        'shops/moderation_dashboard.html',
        {
            'pending_shops': pending_shops,
            'recent_reviewed': recent_reviewed,
            'moderation_logs': moderation_logs,
        },
    )
