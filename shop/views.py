from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from .models import Category, Product,Cart, CartItem, Order, OrderItem, Favorite
from .forms import CustomUserCreationForm, ProfileForm, CommentForm
from django.views.generic import DetailView



def logout_view(request):
    logout(request)
    return redirect('shop:product_list')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop:product_list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    search = request.GET.get('search')

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(
            Favorite.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if search:
        products = products.filter(title__icontains=search)


    sort = request.GET.get('sort')

    if sort == 'name_asc':
        products = products.order_by('title')
    elif sort == 'name_desc':
        products = products.order_by('-title')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'new':
        products = products.order_by('-id')

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': categories,
        'favorite_ids': favorite_ids,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


def category_products(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()
    return render(request, 'shop/category_products.html', {
        'category': category,
        'products': products
    })

def profile(request):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    return render(request, 'shop/profile.html', {
        'user': request.user
    })

def profile_edit(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('shop:profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'shop/profile_edit.html', {'form': form})

from .models import Favorite, Product

def favorite_toggle(request, pk):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        fav.delete()

    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

def favorites_list(request):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    favorites = Favorite.objects.filter(user=request.user).select_related('product')

    return render(request, 'shop/favorites_list.html', {
        'favorites': favorites
    })

def favorite_remove(request, pk):
    fav = Favorite.objects.filter(pk=pk, user=request.user).first()
    if fav:
        fav.delete()
    return redirect('shop:favorites_list')



class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.product = self.object
            comment.save()

        return redirect('shop:product_detail', pk=self.object.pk)



# -----------------------------
# ДОБАВИТЬ В КОРЗИНУ
# -----------------------------
def add_to_cart(request, pk):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    product = get_object_or_404(Product, pk=pk)

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1
        item.save()

    return redirect('shop:cart')


# -----------------------------
# СТРАНИЦА КОРЗИНЫ
# -----------------------------
def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    total = sum(i.product.price * i.quantity for i in items)

    return render(request, 'shop/cart.html', {
        'items': items,
        'total': total
    })


# -----------------------------
# УДАЛИТЬ ТОВАР ИЗ КОРЗИНЫ
# -----------------------------
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('shop:cart')


# -----------------------------
# ОФОРМИТЬ ЗАКАЗ
# -----------------------------
def create_order(request):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        return redirect('shop:cart')

    order = Order.objects.create(
        user=request.user,
        status='Новый',
        total_price=sum(i.product.price * i.quantity for i in items)
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    items.delete()

    return redirect('shop:orders')


# -----------------------------
# СПИСОК ЗАКАЗОВ ПОЛЬЗОВАТЕЛЯ
# -----------------------------
def orders_list(request):
    if not request.user.is_authenticated:
        return redirect('shop:login')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'shop/orders.html', {
        'orders': orders
    })

def cart_increment(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect('shop:cart')


def cart_decrement(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('shop:cart')

