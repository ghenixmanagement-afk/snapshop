import os
import django
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'snapshop.settings')
django.setup()

from products.models import Product

def migrate_images_to_webp():
    products = Product.objects.exclude(image='')
    total = products.count()
    print(f"--- Début de la conversion pour {total} produits ---")

    for i, product in enumerate(products):
        if not product.image:
            continue

        # On vérifie si c'est déjà un webp pour éviter de le traiter deux fois
        if product.image.name.lower().endswith('.webp'):
            print(f"[{i+1}/{total}] Passé : {product.name} est déjà en WebP.")
            continue

        try:
            # Ouverture de l'image
            img = Image.open(product.image.path)

            # Conversion RGB pour gérer la transparence
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Préparation du buffer
            output = BytesIO()
            img.save(output, format='WebP', quality=80)
            output.seek(0)

            # Nouveau nom de fichier
            old_path = product.image.path
            base_name = os.path.splitext(product.image.name)[0]
            new_name = f"{base_name}.webp"

            # Sauvegarde dans le modèle
            product.image.save(new_name, ContentFile(output.read()), save=True)

            # Optionnel : Supprimer l'ancien fichier physique (JPG/PNG) pour gagner de la place
            if os.path.exists(old_path) and not old_path.endswith('.webp'):
                os.remove(old_path)

            print(f"[{i+1}/{total}] Succès : {product.name} converti.")

        except Exception as e:
            print(f"[{i+1}/{total}] Erreur sur {product.name} : {e}")

    print("--- Migration terminée ---")

if __name__ == "__main__":
    migrate_images_to_webp()