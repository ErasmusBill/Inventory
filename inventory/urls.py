from django.urls import path
from . import views

app_name = 'inventory'
urlpatterns = [
    # User Authentication
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('signup/', views.user_signup, name='user_signup'),
    path('change-password/', views.user_change_password, name='user_change_password'),
    
    # Product Manipulation
    path('add-product/', views.add_product, name='add_product'),
    path('update-product/<int:product_id>/', views.update_product, name='update_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Sales Calculation
    path('daily-sales/', views.calculate_daily_sales_by_product, name='calculate_daily_sales'),
]