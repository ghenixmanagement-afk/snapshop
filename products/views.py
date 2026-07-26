from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from shops.models import Shop
from .forms import ProductForm, ReviewForm
from .models import Favorite, Product, ProductAnalytics, Review


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('shop'), slug=slug, shop__is_active=True)
    analytics, _ = ProductAnalytics.objects.get_or_create(product=product)
    ProductAnalytics.objects.filter(pk=analytics.pk).update(views_count=F('views_count') + 1)
    reviews = Review.objects.filter(product=product).select_related('user')
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    message = quote(f"Bonjour, je suis interesse(e) par {product.name} vu sur SnapShop.")
    wa_link = f"https://wa.me/{product.shop.whatsapp_number}?text={message}" if product.shop.whatsapp_number else None
    image_url = product.image.url if product.image else None
    return render(
        request,
        'products/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
            'is_favorite': is_favorite,
            'wa_link': wa_link,
            'product_url': request.build_absolute_uri(),
            'og_image': image_url,
        },
    )


def whatsapp_redirect(request, slug):
    product = get_object_or_404(Product.objects.select_related('shop'), slug=slug, shop__is_active=True)
    if not product.shop.whatsapp_number:
        return redirect('product_detail', slug=slug)
    analytics, _ = ProductAnalytics.objects.get_or_create(product=product)
    ProductAnalytics.objects.filter(pk=analytics.pk).update(whatsapp_clicks=F('whatsapp_clicks') + 1)
    message = quote(f"Bonjour, je suis interesse(e) par {product.name} vu sur SnapShop.")
    return redirect(f"https://wa.me/{product.shop.whatsapp_number}?text={message}")


@login_required
def create_product(request):
    if request.user.role != 'SELLER':
        raise Http404()
    shop = get_object_or_404(Shop, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})


@login_required
def toggle_favorite(request, slug):
    product = get_object_or_404(Product, slug=slug, shop__is_active=True)
    obj, created = Favorite.objects.get_or_create(user=request.user, product=product)
    removed = False
    if not created:
        obj.delete()
        removed = True
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse(
            {
                'ok': True,
                'removed': removed,
                'favorites_count': Favorite.objects.filter(user=request.user).count(),
                'product_slug': product.slug,
            }
        )
    next_url = request.GET.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('product_detail', slug=slug)


@login_required
def create_or_update_review(request, slug):
    product = get_object_or_404(Product, slug=slug, shop__is_active=True)
    review = Review.objects.filter(user=request.user, product=product).first()
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.user = request.user
            new_review.product = product
            new_review.save()
    return redirect('product_detail', slug=slug)


@login_required
def seller_analytics(request):
    if request.user.role != 'SELLER':
        raise Http404()
    shop = get_object_or_404(Shop, owner=request.user)
    products = Product.objects.filter(shop=shop).order_by('-created_at')
    analytics_map = {
        a.product_id: a
        for a in ProductAnalytics.objects.filter(product__shop=shop)
    }
    rows = []
    for product in products:
        data = analytics_map.get(product.id)
        views_count = data.views_count if data else 0
        whatsapp_clicks = data.whatsapp_clicks if data else 0
        conversion_pct = None
        if views_count:
            conversion_pct = round((whatsapp_clicks / views_count) * 100, 1)
        rows.append(
            {
                'product': product,
                'views_count': views_count,
                'whatsapp_clicks': whatsapp_clicks,
                'conversion_pct': conversion_pct,
            }
        )
    totals = ProductAnalytics.objects.filter(product__shop=shop).aggregate(
        total_views=Sum('views_count'),
        total_clicks=Sum('whatsapp_clicks'),
    )
    total_views = totals.get('total_views') or 0
    total_clicks = totals.get('total_clicks') or 0
    overall_conversion_pct = None
    if total_views:
        overall_conversion_pct = round((total_clicks / total_views) * 100, 1)
    top_by_views = sorted(rows, key=lambda r: r['views_count'], reverse=True)[:5]
    top_by_clicks = sorted(rows, key=lambda r: r['whatsapp_clicks'], reverse=True)[:5]
    return render(
        request,
        'products/seller_analytics.html',
        {
            'shop': shop,
            'rows': rows,
            'total_views': total_views,
            'total_clicks': total_clicks,
            'overall_conversion_pct': overall_conversion_pct,
            'top_by_views': top_by_views,
            'top_by_clicks': top_by_clicks,
        },
    )


@login_required
def edit_product(request, product_id):
    """Modifier un produit (vendeur uniquement)"""
    if request.user.role != 'SELLER':
        raise Http404()
    
    shop = get_object_or_404(Shop, owner=request.user)
    product = get_object_or_404(Product, id=product_id, shop=shop)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/product_form.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    """Supprimer un produit (vendeur uniquement)"""
    if request.user.role != 'SELLER':
        raise Http404()
    
    shop = get_object_or_404(Shop, owner=request.user)
    product = get_object_or_404(Product, id=product_id, shop=shop)
    
    if request.method == 'POST':
        product.delete()
        return redirect('seller_dashboard')
    
    # Redirection simple si accès direct (pas de POST)
    return redirect('seller_dashboard')
