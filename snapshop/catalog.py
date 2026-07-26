"""
Logique catalogue partagée (page d'accueil + API feed JSON).
Tri par engagement (vues, avis, favoris) avec léger mélange aléatoire pour la diversité.
"""
from decimal import Decimal, InvalidOperation

from django.db.models import Count, F, Q
from django.db.models.functions import Coalesce, Random

from products.models import Category, Product, SubCategory
from shops.models import Shop


def parse_decimal(value):
    if not value or not str(value).strip():
        return None
    try:
        return Decimal(str(value).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


def get_catalog_request_params(request):
    return {
        "city": request.GET.get("city", "").strip(),
        "q": request.GET.get("q", "").strip(),
        "category": request.GET.get("category", "").strip(),
        "subcategory": request.GET.get("subcategory", "").strip(),
        "price_min": parse_decimal(request.GET.get("price_min")),
        "price_max": parse_decimal(request.GET.get("price_max")),
    }


def build_catalog_queryset(request):
    """Queryset produits filtré comme sur la home (sans tri final ni slice)."""
    p = get_catalog_request_params(request)
    shops_qs = Shop.objects.filter(is_active=True)
    if p["city"]:
        shops_qs = shops_qs.filter(city=p["city"])

    qs = Product.objects.filter(shop__in=shops_qs, in_stock=True).select_related(
        "shop", "subcategory", "subcategory__category"
    )

    if p["category"]:
        category_obj = Category.objects.filter(slug=p["category"], is_active=True).first()
        if category_obj:
            qs = qs.filter(
                Q(subcategory__category=category_obj)
                | Q(subcategory__isnull=True, category__iexact=category_obj.name)
            )
        else:
            qs = qs.filter(category__iexact=p["category"])
    if p["subcategory"]:
        subcategory_obj = SubCategory.objects.filter(slug=p["subcategory"], is_active=True).first()
        if subcategory_obj:
            qs = qs.filter(subcategory=subcategory_obj)
    if p["price_min"] is not None:
        qs = qs.filter(price__gte=p["price_min"])
    if p["price_max"] is not None:
        qs = qs.filter(price__lte=p["price_max"])
    if p["q"]:
        qs = qs.filter(
            Q(name__icontains=p["q"])
            | Q(description__icontains=p["q"])
            | Q(category__icontains=p["q"])
            | Q(shop__name__icontains=p["q"])
        )
    return qs


def annotate_engagement_and_order(qs):
    """
    Vues (consultations), avis (commentaires), favoris — score pondéré + Random() pour diversité.
    """
    qs = qs.annotate(
        _vc=Coalesce("analytics__views_count", 0),
        _rc=Count("review", distinct=True),
        _fc=Count("favorite", distinct=True),
    ).annotate(
        engagement=F("_vc") * 3 + F("_rc") * 5 + F("_fc") * 2,
    )
    return qs.order_by("-engagement", Random())


def serialize_product(request, product):
    image_url = None
    if product.image:
        image_url = request.build_absolute_uri(product.image.url)
    return {
        "slug": product.slug,
        "name": product.name,
        "price": str(product.price),
        "category": product.category,
        "shop_name": product.shop.name,
        "image_url": image_url,
    }
