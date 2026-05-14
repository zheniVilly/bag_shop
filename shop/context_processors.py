
from .models import Category

def menu_categories(request):
    return {
        'menu_categories': Category.objects.filter(pk__isnull=False)
    }

