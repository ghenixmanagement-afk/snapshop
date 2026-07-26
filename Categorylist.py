import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snapshop.settings')
django.setup()

from products.models import Category, SubCategory

def seed():

    data = {
        "Téléphones & Accessoires": [
            "Smartphones",
            "Coques & Protections",
            "Chargeurs & Câbles",
            "Écouteurs & Casques"
        ],
        "Mode & Vêtements": [
            "Homme",
            "Femme",
            "Chaussures",
            "Accessoires"
        ],
        "Beauté & Cosmétiques": [
            "Maquillage",
            "Soins du visage",
            "Parfums",
            "Coiffure"
        ],
        "Électronique & Informatique": [
            "Ordinateurs",
            "Accessoires PC",
            "Gaming",
            "Stockage & Réseaux"
        ],
        "Électroménager": [
            "Cuisine",
            "Entretien maison",
            "Climatisation"
        ],
        "Auto & Moto": [
            "Pièces auto",
            "Accessoires voiture",
            "Huiles & entretien"
        ],
        "Alimentation & Supermarché": [
            "Produits locaux",
            "Boissons",
            "Snacks"
        ]
    }

    for cat_name, subs in data.items():
        category, created = Category.objects.get_or_create(name=cat_name)

        for sub in subs:
            SubCategory.objects.get_or_create(
                category=category,
                name=sub
            )

    print("✅ Catégories et sous-catégories insérées avec succès.")

if __name__ == "__main__":
    seed()