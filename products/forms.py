from django import forms

from .models import Product, Review, SubCategory


class ProductForm(forms.ModelForm):
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.filter(is_active=True).select_related("category"),
        required=False,
        empty_label="Choisir une sous-categorie",
        label="Categorie / Sous-categorie",
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'subcategory', 'in_stock']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subcategory"].queryset = SubCategory.objects.filter(is_active=True).select_related("category")
        self.fields["subcategory"].label_from_instance = lambda obj: f"{obj.category.name} > {obj.name}"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
