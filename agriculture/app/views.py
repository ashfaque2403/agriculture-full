from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Product,Cart,CartItem,CustomUser,OrderItem,Order,Category,Address
from django.http import HttpResponseRedirect

from django.http import JsonResponse,HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect

from django.contrib.auth import logout
from django.contrib.auth import authenticate,login
from django.contrib.auth import update_session_auth_hash

from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from django.db.models import Q
from django.http import HttpResponse
from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from django.http import Http404

from .models import Address, CartItem
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem 
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings



def index(request):
    # Check if the user is a farmer to determine product visibility
    if hasattr(request.user, 'is_farmer') and request.user.is_farmer:
        product = Product.objects.filter(user=request.user)
    else:
        product = Product.objects.all()

    cart_items = None
    total_cart_items = 0
    total_price = 0
    search = request.GET.get('search')

    if search:
        product = product.filter(Q(name__icontains=search))

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)
        total_cart_items = cart_items.count()

        for cart_item in cart_items:
            cart_item.total_price = cart_item.product.price * cart_item.quantity
            total_price += cart_item.total_price  # Aggregate total price from cart items

    # Calculate total amount from cart items if they exist
    total_amount = sum(cart_item.total_price for cart_item in cart_items) if cart_items else 0

    context = {
        'product': product,
        'total_amount': total_amount,
        'search': search,
        'cart_items': cart_items,
        'total_cart_items': total_cart_items,
    }
    return render(request, 'index.html', context)


def about(re):
    return render(re,'about.html')




def shop(re):
    product = Product.objects.all()
    cart_items = CartItem.objects.all()
    total_cart_items = cart_items.count()
    category_obj=Category.objects.all()
    sort_option=re.GET.get('sorted')
    search = re.GET.get('search')
    categories = re.GET.getlist('category') # Update the parameter name here to 'amentities'

    if sort_option == '2':  # High Price → Low Price
        product = product.order_by('-price')
    elif sort_option == '3':  # Low Price → High Price
        product = product.order_by('price')

    if search:
        product = product.filter(
            Q(name__icontains=search)|
            Q(category__name__icontains=search)
        )
    
    if categories:
        product = product.filter(category__name__in=categories)
        

    total_price = 0

    for cart_item in cart_items: 
        cart_item.total_price = cart_item.product.price * cart_item.quantity
        total_price += cart_item.total_price  # Count the total number of cart items

    total_carted_items = cart_items.count()
    total_amount = sum(cart_item.total_price for cart_item in cart_items)

    context = {
        'product': product,
        'category_obj': category_obj,
        'total_amount': total_amount,
        'cart_items': cart_items,
        'total_cart_items': total_cart_items,
        'search': search,
        'categories': categories,  # Add this count to the context
    }
    return render(re,'shop.html',context)

def shop_detail(request):
    if request.method == 'POST':
        if 'category_name' in request.POST:  # Handling Category Creation
            category_name = request.POST.get('category_name')
            if not Category.objects.filter(name=category_name).exists():
                Category.objects.create(name=category_name)
                messages.success(request, 'Category Created Successfully!')
            else:
                messages.error(request, 'Category already exists.')
        
        elif 'product_name' in request.POST:  # Handling Product Creation
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            category_name = request.POST.get('category')
            discount = request.POST.get('discount')
            image = request.FILES.get('image')

            category = Category.objects.get(name=category_name)  # Assumes category must already exist
            Product.objects.create(
                user=request.user,
                name=product_name,
                description=description,
                price=price,
                category=category,
                discount=discount,
                image=image
            )
            messages.success(request, 'Product Created Successfully!')
        
        return redirect('shop_detail')
    product = Product.objects.filter(user_id=request.user)
    return render(request, 'shop-detail.html',{'product':product})



def update_cart_item(request, item_id):
    try:
        quantity = int(request.POST.get('quantity'))
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.quantity = quantity
        cart_item.total_price = cart_item.product.price * quantity  # Ensure correct price calculation
        cart_item.save()
        return JsonResponse({'status': 'success', 'message': 'Quantity updated', 'total_price': cart_item.total_price})
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_price = 0
    total_discount = 0
   
# add the cart items
    for cart_item in cart_items: 
        cart_item.total_discount = cart_item.product.discount * cart_item.quantity
        total_discount += cart_item.total_discount

    for cart_item in cart_items: 
        cart_item.total_price = cart_item.product.price * cart_item.quantity
        total_price += cart_item.total_price

    total_carted_items = cart_items.count()
    total_amount = sum(cart_item.total_price for cart_item in cart_items)
    discounted_amount=total_amount-total_discount

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_carted_items': total_carted_items,
        'total_amount': total_amount,
        'discounted_amount': discounted_amount,
    }
    return render(request,'cart.html',context)

#place Order



def order_success(request):
    return HttpResponse("Thank you for your order! We are processing it now.")



# add to the cart
@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    messages.success(request, 'added to the cart')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_from_cart(request,cart_item_id):
    cart_item=get_object_or_404(CartItem,id=cart_item_id)
    cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def logout_view(request):
    logout(request)
    return redirect(index)

def LoginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = CustomUser.objects.filter(username=username).first()

        if not user_obj:
            messages.warning(request, 'Account not found')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user_authenticated = authenticate(request, username=username, password=password)

        if not user_authenticated:
            messages.warning(request, 'Invalid password')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        print(f"Authenticated User: {user_authenticated}")

        login(request, user_authenticated)
        return redirect('/')

    return render(request, 'login.html')



def register_view(request):
    if request.method == 'POST':
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if a user with the provided email already exists
        user_exists = CustomUser.objects.filter(email=email).exists()

        if user_exists:
            messages.warning(request, 'User with this email already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Create a new CustomUser
        user = CustomUser.objects.create(username=username, email=email,first_name=firstname,last_name=lastname)
        user.set_password(password)
        user.save()

        # Redirect to the login page
        return redirect('login')

    # If the request method is not POST, render the registration page
    return render(request, 'register.html')


def farmer_register_view(request):
    if request.method == 'POST':
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if a user with the provided email already exists
        user_exists = CustomUser.objects.filter(email=email).exists()

        if user_exists:
            messages.warning(request, 'User with this email already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Create a new CustomUser
        user = CustomUser.objects.create(username=username, email=email,first_name=firstname,last_name=lastname,is_farmer=True)
        user.set_password(password)
        user.save()

        # Redirect to the login page
        return redirect('login')

    # If the request method is not POST, render the registration page
    return render(request, 'farmer_register.html')




# from cart.cart import Cart




def start_order(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        zipcode = request.POST.get('zipcode')
        shipping_option = request.POST.get('shipping-option', 'Standard Delivery')

        # Convert float to Decimal
        speed_delivery_cost = Decimal('16.00') if shipping_option == 'Speed Delivery' else Decimal('0.00')

        # Fetch the cart associated with the current user
        user_cart = Cart.objects.filter(user=request.user).first()
        if not user_cart:
            messages.error(request, "No cart found for this user.")
            return redirect('cart')

        cart_items = CartItem.objects.filter(cart=user_cart)
        if not cart_items.exists():
            messages.error(request, "No items in cart.")
            return redirect('cart')

        # Calculating total price from cart items using Decimal for all arithmetic
        total_price = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
        total_discount = sum(Decimal(item.product.discount) * item.quantity for item in cart_items)
        total_cost = total_price - total_discount + speed_delivery_cost

        # Create Order
        try:
            order = Order.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                address=address,
                zipcode=zipcode,
                shipping_method=shipping_option,
                shipping_cost=speed_delivery_cost,
                total_cost=total_cost
            )
            # messages.success(request, "Order created successfully!")

            # Create OrderItems and update product stock
            for item in cart_items:
                product = item.product
                if product.stock_quantity >= item.quantity:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=Decimal(product.price) * item.quantity,
                        quantity=item.quantity,
                    )
                    # Update product stock quantity
                    product.stock_quantity -= item.quantity
                    product.save()
                else:
                    messages.warning(request, f"Not enough stock for product: {product.name}")
                    return redirect('cart')

            # Clear the cart
            cart_items.delete()
            # messages.success(request, "Order placed successfully!")
            return redirect('wishlist')
        except Exception as e:
            messages.error(request, f"An error occurred while placing the order: {e}")
            return redirect('cart')

    return render(request, 'cart.html')






def checkout(request):
    try:
        address = Address.objects.get(user=request.user)
    except Address.DoesNotExist:
        address = None  # Handle case where no address exists for the user

    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_price = 0
    total_discount = 0
    speed_delivery = 16
    normal_delivery = 0

    # Calculate discounts and total price
    for cart_item in cart_items:
        product_discount = cart_item.product.discount or 0  # Ensure there's a fallback if discount is None
        product_price = cart_item.product.price or 0  # Ensure there's a fallback if price is None
        cart_item.total_discount = product_discount * cart_item.quantity
        total_discount += cart_item.total_discount
        cart_item.total_price = product_price * cart_item.quantity
        total_price += cart_item.total_price

    total_carted_items = cart_items.count()
    total_amount = total_price - total_discount
    discounted_amount = total_amount
    final_amount_with_speed = discounted_amount + speed_delivery

    # Populate form data based on whether an address exists
    form_data = {
        'first_name': address.first_name if address else '',
        'last_name': address.last_name if address else '',
        'email': address.email if address else '',
        'address': address.address if address else '',
        'zipcode': address.zipcode if address else '',
    }

    context = {
        'cart_items': cart_items,
        'address': address,
        'form_data': form_data,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_carted_items': total_carted_items,
        'total_amount': total_amount,
        'discounted_amount': discounted_amount,
        'final_amount_with_speed': final_amount_with_speed,
        'speed_delivery': speed_delivery,
        'normal_delivery': normal_delivery
    }
    return render(request, 'checkout.html', context)


@login_required
def myaccount(re):
    return render(re,'my-account.html')
@login_required
def wishlist(request):
    cart_items = CartItem.objects.all()
    total_price = 0
    total_discount = 0
    speed_delivery = 16
    normal_delivery = 0

    # Calculate discounts and total price
    for cart_item in cart_items:
        cart_item.total_discount = cart_item.product.discount * cart_item.quantity
        total_discount += cart_item.total_discount
        cart_item.total_price = cart_item.product.price * cart_item.quantity
        total_price += cart_item.total_price

    total_carted_items = cart_items.count()
    total_amount = total_price - total_discount  # Adjusted to remove calculation redundancy
    discounted_amount = total_amount

    # Adding speed delivery to the context if needed dynamically
    final_amount_with_speed = discounted_amount + speed_delivery  # This is static and will be dynamic via JS

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_carted_items': total_carted_items,
        'total_amount': total_amount,
        'discounted_amount': discounted_amount,
        'final_amount_with_speed': final_amount_with_speed,
        'speed_delivery': speed_delivery,
        'normal_delivery': normal_delivery
    }
    return render(request, 'payment.html', context)

def gallery(re):
    return render(re,'gallery.html')

def contactus(re):
    return render(re,'contact-us.html')

def register_farmer(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        d=Farmer(name=name,email=email,password=password,confirm_password=confirm_password)
        d.save()
        messages.success(request,'profile details added')
    return render(request, 'farmerregister.html')

def farmer_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            data = Farmer.objects.get(email=email)
            if email == data.email and password == data.password:
                request.session['id'] = email
                return redirect(fdash)
            else:
                messages.error(request, 'Invalid email or password')
        except Exception:
            if email == 'admin' and password == 'admin':
                request.session['id1'] = email
                return redirect(adash)
            else:
                messages.error(request, 'Invalid email or Password')
    return render(request, 'farmerlogin.html')


def register_user(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        d = User(name=name, email=email, password=password, confirm_password=confirm_password)
        d.save()
        messages.success(request, 'profile details added')
    return render(request, 'userregister.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            data = User.objects.get(email=email)
            if email == data.email and password == data.password:
                request.session['id'] = email
                return redirect(udash)
            else:
                messages.error(request, 'Invalid email or password')
        except Exception:
            if email == 'admin' and password == 'admin':
                request.session['id1'] = email
                return redirect(adash)
            else:
                messages.error(request, 'Invalid email or Password')
    return render(request, 'userlogin.html')

def adash(re):
    return render(re,'admindash.html')

def admin_home(request):
    return render(request,'adminhome.html')


def vw_farmer(re):
    if 'id1' in re.session:
        data=Farmer.objects.all()
        print(data)
        return render(re,'view_farmer.html',{'d':data})
    return redirect(farmer_login)



def vwproduct(re):
    return render(re,'viewproduct.html')


def vwconsumer(re):
    return render(re,'viewconsumer.html')


 # Assuming these are your model imports

def vworder(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('action')

        if order_id:
            order = get_object_or_404(OrderItem, pk=order_id)
            if new_status in [status[0] for status in OrderItem.STATUS_CHOICES]:  # Check if new status is valid
                order.status = new_status
                order.save()
                messages.success(request, f"Order status updated to {new_status}.")
                return redirect('order')  # Make sure this matches your URL name
        else:
            messages.error(request, "Order ID not provided.")

    # For buyers: List OrderItems linked to Orders made by the user
    buyer_orders = OrderItem.objects.filter(order__user=request.user).order_by('-created_at')

    # For sellers: List OrderItems linked to Products managed by the user
    seller_orders = OrderItem.objects.filter(product__user=request.user).order_by('-created_at')

    return render(request, 'order.html', {'buyer_orders': buyer_orders, 'seller_orders': seller_orders})





def fdash(request):
    try:
        address = Address.objects.get(user=request.user)  # Get the unique address for the user
    except Address.DoesNotExist:
        address = None  # If no address exists, set address to None

    if request.method == "POST":
        # Fetch data from form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address_field = request.POST.get('address')  # Avoid name conflict with 'address' variable
        zipcode = request.POST.get('zipcode')

        if address:
            # Update existing address
            address.first_name = first_name
            address.last_name = last_name
            address.email = email
            address.address = address_field
            address.zipcode = zipcode
            address.save()
            messages.success(request, 'Address updated successfully!')
        else:
            # Create new address if none exists
            Address.objects.create(user=request.user, first_name=first_name, last_name=last_name, email=email, address=address_field, zipcode=zipcode)
            messages.success(request, 'Address added successfully!')

        return redirect('address')  # Redirect to the same page to avoid resubmission of form

    # Prepare form data if address exists; otherwise, use empty strings
    form_data = {
        'first_name': address.first_name if address else '',
        'last_name': address.last_name if address else '',
        'email': address.email if address else '',
        'address': address.address if address else '',
        'zipcode': address.zipcode if address else '',
    }

    return render(request, 'address.html', {'address': address, 'form_data': form_data})


def admindash(re):
    product = Product.objects.filter(user_id=re.user)
    return render(re,'my_products.html',{'product': product})

def adminfarmer(re):
    # Check if the user is a farmer
    if re.user.is_farmer:
        farmer = CustomUser.objects.all()  # Get all users (assuming you want to see all users if the admin is a farmer)
    else:
        farmer = CustomUser.objects.filter(is_farmer=True)  # Get only users who are farmers

    return render(re, 'admin_view_farmer.html', {'farmer': farmer})


def adminconsumer(re):
    farmer = CustomUser.objects.all()
    return render(re,'admin_view_cunsumer.html', {'farmer': farmer})

def adminproduct(re):
    product=Product.objects.all().order_by('-created_at')
    return render(re,'admin_view_product.html',{'product': product})

def adminorder(re):
    order=OrderItem.objects.all().order_by('-created_at')
    return render(re,'admin_view_order.html',{'order': order})



def contact_us(request):

    
    return render(request, 'contact_us.html')






def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')  # This is the recipient's email
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')

        recipient = email  # Use the recipient's email from the form

        sender_email = settings.DEFAULT_FROM_EMAIL  # Keep the sender's email from settings

        # Use send_mail function
        send_mail(
            subject,
            message,
            sender_email,
            [recipient],
            fail_silently=False,
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD,
            connection=None,
            html_message=None
        )

        return HttpResponse('Email sent successfully!')
