from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from products.models import Category, Favorite, Product, SubCategory
from shops.models import Shop

from .catalog import (
    annotate_engagement_and_order,
    build_catalog_queryset,
    serialize_product,
)


def _parse_decimal(value):
    if not value or not str(value).strip():
        return None
    try:
        return Decimal(str(value).strip().replace(',', '.'))
    except (InvalidOperation, ValueError):
        return None


def home(request):
    city = request.GET.get('city', '').strip()
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_subcategory = request.GET.get('subcategory', '').strip()
    price_min = _parse_decimal(request.GET.get('price_min'))
    price_max = _parse_decimal(request.GET.get('price_max'))

    shops_qs = Shop.objects.filter(is_active=True)
    if city:
        shops_qs = shops_qs.filter(city=city)
    shops = shops_qs[:8]

    base_products_qs = Product.objects.filter(shop__in=shops_qs, in_stock=True).select_related(
        'shop', 'subcategory', 'subcategory__category'
    )
    products_qs = base_products_qs
    if selected_category:
        category_obj = Category.objects.filter(slug=selected_category, is_active=True).first()
        if category_obj:
            # Include both new relational data and legacy text-only category rows.
            products_qs = products_qs.filter(
                Q(subcategory__category=category_obj)
                | Q(subcategory__isnull=True, category__iexact=category_obj.name)
            )
        else:
            # Backward compatibility with old query string values.
            products_qs = products_qs.filter(category__iexact=selected_category)
    if selected_subcategory:
        subcategory_obj = SubCategory.objects.filter(slug=selected_subcategory, is_active=True).first()
        if subcategory_obj:
            products_qs = products_qs.filter(subcategory=subcategory_obj)
    if price_min is not None:
        products_qs = products_qs.filter(price__gte=price_min)
    if price_max is not None:
        products_qs = products_qs.filter(price__lte=price_max)
    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__icontains=search_query)
            | Q(shop__name__icontains=search_query)
        )
    catalog_total_products = products_qs.count()

    # Libellés lisibles pour le récapitulatif des filtres (interface catalogue).
    city_display = None
    if city:
        city_display = dict(Shop.CITY_CHOICES).get(city, city)
    category_display = None
    if selected_category:
        cat_row = Category.objects.filter(slug=selected_category, is_active=True).first()
        category_display = cat_row.name if cat_row else selected_category
    subcategory_display = None
    if selected_subcategory:
        sub_row = SubCategory.objects.filter(slug=selected_subcategory, is_active=True).select_related(
            "category"
        ).first()
        if sub_row:
            subcategory_display = f"{sub_row.category.name} — {sub_row.name}"
        else:
            subcategory_display = selected_subcategory

    catalog_filter_summary = []
    if search_query:
        catalog_filter_summary.append(
            {"label": "Recherche textuelle", "value": f"« {search_query} » (nom produit, description, categorie ou nom de boutique)"}
        )
    if city_display:
        catalog_filter_summary.append({"label": "Zone", "value": f"Boutiques situees a {city_display}"})
    if category_display:
        catalog_filter_summary.append({"label": "Categorie", "value": category_display})
    if subcategory_display:
        catalog_filter_summary.append({"label": "Sous-categorie", "value": subcategory_display})
    if price_min is not None:
        catalog_filter_summary.append({"label": "Prix minimum", "value": f"{price_min:g} FCFA"})
    if price_max is not None:
        catalog_filter_summary.append({"label": "Prix maximum", "value": f"{price_max:g} FCFA"})
    catalog_sort_label = (
        # "Priorite aux produits les plus consultes (vues), commentes (avis) et ajoutes aux favoris ; "
        # "ordre legerement varie pour garder un catalogue diversifie."
    )
    catalog_has_active_filters = bool(catalog_filter_summary)
    product_results_count = catalog_total_products

    # Build category/subcategory tree from admin-managed subcategories.
    # Source of truth: /admin/products/subcategory/
    db_categories = (
        Category.objects.filter(
            is_active=True,
            subcategories__is_active=True,
        )
        .distinct()
        .order_by("name")
    )
    legacy_category_values = (
        base_products_qs.filter(subcategory__isnull=True)
        .exclude(category__isnull=True)
        .exclude(category__exact="")
        .values_list("category", flat=True)
        .distinct()
    )
    legacy_category_names = sorted({c.strip() for c in legacy_category_values if c and c.strip()}, key=str.lower)

    subcategories_qs = (
        SubCategory.objects.filter(is_active=True, category__is_active=True)
        .select_related("category")
        .order_by("category__name", "name")
    )
    sub_map = {}
    for sub in subcategories_qs:
        sub_map.setdefault(sub.category_id, []).append(sub)

    category_tree = []
    categories = []
    for cat in db_categories:
        categories.append(cat)
        category_tree.append(
            {
                "name": cat.name,
                "value": cat.slug,
                "is_legacy": False,
                "subcategories": sub_map.get(cat.id, []),
            }
        )

    existing_db_names = {cat.name.lower() for cat in db_categories}
    for legacy_name in legacy_category_names:
        if legacy_name.lower() not in existing_db_names:
            category_tree.append(
                {
                    "name": legacy_name,
                    "value": legacy_name,
                    "is_legacy": True,
                    "subcategories": [],
                }
            )

    # Keep old context key for compatibility elsewhere.
    subcategories = [sub for group in category_tree for sub in group["subcategories"]]

    return render(
        request,
        'home.html',
        {
            'shops': shops,
            'selected_city': city,
            'search_query': search_query,
            'selected_category': selected_category,
            'selected_subcategory': selected_subcategory,
            'price_min': request.GET.get('price_min', '').strip(),
            'price_max': request.GET.get('price_max', '').strip(),
            'cities': Shop.CITY_CHOICES,
            'categories': categories,
            'subcategories': subcategories,
            'category_tree': category_tree,
            'catalog_filter_summary': catalog_filter_summary,
            'catalog_sort_label': catalog_sort_label,
            'catalog_has_active_filters': catalog_has_active_filters,
            'product_results_count': product_results_count,
            'catalog_total_products': catalog_total_products,
            'catalog_feed_url': reverse('catalog_feed'),
        },
    )


@require_GET
def catalog_feed(request):
    """JSON pagine pour infinite scroll (tri engagement + diversite)."""
    try:
        offset = max(0, int(request.GET.get("offset", 0)))
        limit = min(max(1, int(request.GET.get("limit", 12))), 48)
    except ValueError:
        offset, limit = 0, 12
    qs = annotate_engagement_and_order(build_catalog_queryset(request))
    total = qs.count()
    page = qs[offset : offset + limit]
    products = [serialize_product(request, p) for p in page]
    return JsonResponse(
        {
            "products": products,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(products) < total,
            "next_offset": offset + len(products),
        }
    )


@login_required
def dashboard(request):
    if getattr(request.user, 'role', 'CUSTOMER') == 'SELLER':
        return redirect('seller_dashboard')
    favorites_count = request.user.favorite_set.count()
    reviews_count = request.user.review_set.count()
    favorite_items = (
        Favorite.objects.filter(user=request.user)
        .select_related('product', 'product__shop')
        .order_by('-id')[:8]
    )
    return render(
        request,
        'accounts/customer_dashboard.html',
        {
            'favorites_count': favorites_count,
            'reviews_count': reviews_count,
            'favorite_items': favorite_items,
        },
    )