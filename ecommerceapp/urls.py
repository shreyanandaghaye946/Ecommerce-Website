from django.urls import path
from . import views

urlpatterns = [
    # 🏠 Core Pages
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('account/', views.my_account, name='my_account'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
     path('search/', views.search_products, name='search'),

    # 🛒 Cart Management
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # ⚡ Instant Purchase
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),

    # ❤️ Wishlist Management
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # 🔐 Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # 🔍 Product Search
    path('search/', views.search_products, name='search'),

    # 🧾 Checkout Flow
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('checkout/address/<int:product_id>/', views.checkout_address, name='checkout_address'),
    path('checkout/payment/<int:product_id>/', views.checkout_payment, name='checkout_payment'),
    path('checkout/confirm/<int:product_id>/', views.confirm_order, name='confirm_order'),

    # ✅ Thank You Page
    path('thank-you/<int:order_id>/', views.thank_you, name='thank_you'),
]
