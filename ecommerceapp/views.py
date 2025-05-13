from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Product, CartItem, Wishlist, Order, OrderItem, Address, UserProfile
from django.views.decorators.csrf import csrf_exempt

# ------------------- Public Pages -------------------

def home(request):
    products = Product.objects.all()
    return render(request, 'ecommerceapp/home.html', {'products': products})

def shop(request):
    products = Product.objects.all()
    return render(request, 'ecommerceapp/shop.html', {'products': products})

def about(request):
    return render(request, 'ecommerceapp/about.html')

def contact(request):
    return render(request, 'ecommerceapp/contact.html')

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'ecommerceapp/search_results.html', {'query': query, 'products': products})

# ------------------- Authentication -------------------

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
    
    return render(request, 'ecommerceapp/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')
    
    return render(request, 'ecommerceapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# ------------------- My Account -------------------

@login_required
def my_account(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    wishlist_items = Wishlist.objects.filter(user=request.user)

    return render(request, 'ecommerceapp/my_account.html', {
        'user': request.user,
        'addresses': addresses,
        'orders': orders,
        'wishlist_items': wishlist_items
    })

@login_required
def edit_profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        profile_pic = request.FILES.get('profile_pic')

        user.username = username
        user.email = email
        user.save()

        if profile_pic:
            profile.profile_pic = profile_pic
            profile.save()

        return redirect('my_account')

    return render(request, 'ecommerceapp/edit_profile.html', {
        'user': user,
        'profile': profile
    })

# ------------------- Wishlist -------------------

@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'ecommerceapp/wishlist.html', {'wishlist_items': items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, 'Added to wishlist.')
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    wishlist_item.delete()
    return redirect('wishlist')

# ------------------- Cart -------------------

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, 'ecommerceapp/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@require_POST
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    cart_item.quantity = cart_item.quantity + quantity if not created else quantity
    cart_item.save()
    messages.success(request, 'Product added to cart.')
    return redirect('cart')

@require_POST
@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
        messages.success(request, 'Cart updated.')
    else:
        item.delete()
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')



from django.db.models import Q
from .models import Product

def search_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else []

    return render(request, 'search_result.html', {
        'products': products,
        'query': query
    })



# ------------------- Buy Now / Checkout Flow -------------------

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists() if request.user.is_authenticated else False

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        request.session['checkout_product_id'] = product_id
        request.session['checkout_quantity'] = quantity
        return redirect('checkout_address', product_id=product.id)

    return render(request, 'ecommerceapp/product_detail.html', {
        'product': product,
        'is_in_wishlist': is_in_wishlist,
    })

def buy_now(request, product_id):
    try:
        Product.objects.get(id=product_id)  # validation
        return redirect('product_detail', product_id=product_id)
    except Product.DoesNotExist:
        return redirect('shop')

@login_required
def checkout_address(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    address = Address.objects.filter(user=request.user).first()

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        country = request.POST.get('country', 'India')
        quantity = int(request.POST.get('quantity', 1))

        if full_name and address_line:
            address_obj, _ = Address.objects.update_or_create(
                user=request.user,
                defaults={
                    'full_name': full_name,
                    'mobile': mobile,
                    'address_line': address_line,
                    'city': city,
                    'state': state,
                    'pincode': pincode,
                    'country': country
                }
            )
            request.session['checkout_address_id'] = address_obj.id
            request.session['checkout_quantity'] = quantity
            return redirect('checkout_payment', product_id=product.id)
        else:
            messages.error(request, "Full name and address are required.")

    return render(request, 'ecommerceapp/checkout_address.html', {
        'product': product,
        'address': address
    })

@login_required
def checkout_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    address_id = request.session.get('checkout_address_id')
    quantity = int(request.session.get('checkout_quantity', 1))

    if not address_id:
        return redirect('checkout_address', product_id=product.id)

    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        total_price = product.price * quantity

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total_price,
            payment_method=payment_method,
            is_ordered=True
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )

        # Clear session
        request.session.pop('checkout_address_id', None)
        request.session.pop('checkout_quantity', None)

        return redirect('thank_you', order_id=order.id)

    total_price = product.price * quantity
    return render(request, 'ecommerceapp/checkout_payment.html', {
        'product': product,
        'quantity': quantity,
        'address': address,
        'total_price': total_price
    })
@login_required
def confirm_order(request, product_id):
    return render(request, 'ecommerceapp/thank_you.html')

# ------------------- Final Thank You Page -------------------

@login_required
def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'ecommerceapp/thank_you.html', {'order': order})



