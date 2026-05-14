from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<int:pk>/', views.category_products, name='category_products'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),


    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorite/toggle/<int:pk>/', views.favorite_toggle, name='favorite_toggle'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/order/', views.create_order, name='create_order'),
    
    path('orders/', views.orders_list, name='orders'),


]
