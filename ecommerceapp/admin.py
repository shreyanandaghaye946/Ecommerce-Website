from django.contrib import admin
from .models import Product ,UserProfile ,Order ,OrderItem,CartItem,Wishlist,Address


admin.site.register(Product)
admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(OrderItem)
admin.site.register(Address)