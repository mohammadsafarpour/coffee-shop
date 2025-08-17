
from .models import Category

def categories_context(request):
    """
    این تابع تمام دسته‌بندی‌ها را دریافت کرده و به context اضافه می‌کند
    تا در تمام تمپلیت‌ها قابل دسترس باشند.
    """
    categories = Category.objects.all()
    return {'categories': categories}