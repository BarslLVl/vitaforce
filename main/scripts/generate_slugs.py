from main.models import Category
from django.utils.text import slugify

def generate_slugs():
    categories_without_slugs = Category.objects.filter(slug="")
    for category in categories_without_slugs:
        category.slug = slugify(category.name)
        category.save()
        print(f"Slug generated for category: {category.name} -> {category.slug}")

if __name__ == "__main__":
    generate_slugs()