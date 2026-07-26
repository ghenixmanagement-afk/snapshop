import os
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

from shops.models import Shop
from accounts.models import CustomUser

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Categorie"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            candidate = base_slug
            index = 1
            while Category.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{index}"
                index += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category__name", "name"]
        unique_together = [("category", "name")]
        verbose_name = "Sous-categorie"
        verbose_name_plural = "Sous-categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.category.name}-{self.name}")
            candidate = base_slug
            index = 1
            while SubCategory.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{index}"
                index += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} > {self.name}"


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=130, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=50)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 1. Gestion de la catégorie parente via la sous-catégorie
        if self.subcategory:
            self.category = self.subcategory.category.name

        # 2. Génération automatique du Slug unique
        if not self.slug:
            base_slug = slugify(f'{self.shop.name}-{self.name}')
            candidate = base_slug
            index = 1
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base_slug}-{index}'
                index += 1
            self.slug = candidate

        # 3. Conversion de l'image en WebP avant la sauvegarde
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)

                # Conversion en RGB si nécessaire (pour gérer la transparence PNG vers WebP)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Buffer mémoire
                output = BytesIO()
                img.save(output, format='WebP', quality=80)
                output.seek(0)

                # Changement du nom de fichier
                filename = os.path.splitext(self.image.name)[0]
                self.image.save(f"{filename}.webp", ContentFile(output.read()), save=False)

            except Exception as e:
                # Log l'erreur si nécessaire, mais laisse Django continuer
                print(f"Erreur conversion WebP: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user} - {self.product}'


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user} - {self.product}'


class ProductAnalytics(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='analytics')
    views_count = models.PositiveIntegerField(default=0)
    whatsapp_clicks = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Analytics for {self.product}'