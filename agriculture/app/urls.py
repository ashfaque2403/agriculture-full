from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('about',views.about,name='about'),
    path('shop',views.shop,name='shop'),
    path('shop-detail/', views.shop_detail, name='shop_detail'),

    path('cart', views.cart,name='cart'),
    path('checkout', views.checkout,name='checkout'),
    path('start_order', views.start_order,name='start_order'),
    path('checkout', views.checkout,name='checkout'),


    path('my-account', views.myaccount,name='myaccount'),
    path('wishlist', views.wishlist,name='wishlist'),
    path('gallery', views.gallery,name='gallery'),
    path('contact-us', views.contactus,name='contact'),
    path('register_farmer',views.register_farmer,name='register_farmer'),
    path('farmer_login',views.farmer_login,name='farmer_login'),
    path('register_user', views.register_user,name='register'),
    path('user_login', views.user_login,name='login'),
    path('adash',views.adash),
    path('admin_home',views.admin_home,name='admin_home'),
    path('vw_farmer', views.vw_farmer),
    path('vwconsumer', views.vwconsumer),
    path('vwproduct', views.vwproduct),
    path('vworder', views.vworder,name="order"),
    path('fdash', views.fdash,name="address"),
    path('my-product', views.admindash,name='my_products'),
    path('admin-consumer', views.adminconsumer,name='admin_consumer'),
    path('admin-farmer', views.adminfarmer,name='admin_farmer'),
    path('admin-order', views.adminorder,name='admin_order'),
    path('admin-product', views.adminproduct,name='admin_product'),


    




    #functions 

    path('add/<int:id>/',views.add_to_cart,name='add'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:cart_item_id>/',views.remove_from_cart,name='remove'),

    #Authentication

    path('login',views.LoginView,name='login'),
    path('register/',views.register_view,name='register'),
    path('farmer-register/',views.farmer_register_view,name='farmer_register'),
    path('logout/',views.logout_view,name='logout'),
    path('contact/', views.contact_us, name='contact_us'),
    path('send-email/', views.send_email, name='send_email'),


    #place order
    path('order-success/', views.order_success, name='order_success_url'),
]