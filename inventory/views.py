from django.shortcuts import render,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .forms import SignUpForm,ChangePasswordForm,AddProductForm
from django.contrib.auth import update_session_auth_hash
from .models import *
from django.db.models import Sum, F,DecimalField,Q,Avg
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.contrib.auth.models import Permission, Group

@require_http_methods(["POST"])
def user_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': 'You have successfully logged in'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@require_http_methods(["POST"])
def user_logout(request):
    logout(request)
    return JsonResponse({'success': 'You have successfully logged out'}, status=200)

@require_http_methods(["POST"])
def user_signup(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return JsonResponse({'success': 'You have successfully created an account'}, status=201)
    else:
        return JsonResponse({'errors': form.errors}, status=400)

@require_http_methods(["POST"])
def user_change_password(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    password_form = ChangePasswordForm(user=request.user, data=request.POST)
    if password_form.is_valid():
        password_form.save()
        update_session_auth_hash(request, password_form.user)
        return JsonResponse({'success': 'You have successfully changed your password'}, status=200)
    else:
        return JsonResponse({'errors': password_form.errors}, status=400)
    
    
#Product Manipulateion,add,delete and update    

@require_http_methods(["POST"])
def add_product(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    add_product_form = AddProductForm(request.POST, request.FILES)
    if add_product_form.is_valid():
        product = add_product_form.save()
        return JsonResponse({
            'success': 'You have successfully added a product',
            'product_id': product.id
        }, status=201)  
    else:
        return JsonResponse({'errors': add_product_form.errors}, status=400)

@require_http_methods(["POST"])
def update_product(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        product = Product.objects.get(id=product_id)
        
        update_product_form = AddProductForm(request.POST,request.FILES, instance=product)
        
        if update_product_form.is_valid():
            updated_product = update_product_form.save()
            return JsonResponse({'success': 'You have successfully updated the product','product_id': updated_product.id}, status=200)
        else:
            return JsonResponse({'errors': update_product_form.errors}, status=400)
    except Product.DoesNotExist:
        return JsonResponse({
            'error': 'Product not found'
        }, status=404)
    
@require_http_methods(["DELETE"])
def delete_product(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return JsonResponse({'success': 'You have successfully deleted the product'}, status=200)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while deleting the product','details': str(e)}, status=500)


def calculate_daily_sales_by_product(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    today = timezone.now().date()
    
    daily_product_sales = Sale.objects.filter(date__date=today).values(
        'product__id',
        'product__product_name'
    ).annotate(
        total_quantity_sold=Sum('quantity_sold'),
        total_sales=Sum('total_sale'),
        average_price=Avg('unit_price')
    ).order_by('-total_sales')
    
    return JsonResponse({
        'date': today,
        'product_sales': list(daily_product_sales)
    })
    
@require_http_methods(['GET'])
def home(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    sale = Sale.objects.all()   
    return JsonResponse({'sale.product_name':'sale.product_name','unit_price':'unit_price'})

@require_http_methods(['GET'])
def search(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    searched = request.GET.get('searched', '')
    if not searched:
        return JsonResponse({'error': 'Search query is empty'}, status=400)

    products = Product.objects.filter(
        Q(product_name__icontains=searched) | 
        Q(description__icontains=searched)
    ).values('id', 'product_name', 'description', 'price', 'stock_quantity')
    
    return JsonResponse({
        'products': list(products)
    })
    
@require_http_methods(['GET'])
def detail_product(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    product = get_object_or_404(Product, pk=product_id)
    return JsonResponse({
        'id': product.id,
        'product_name': product.product_name,
        'description': product.description,
        'price': str(product.price),
        'stock_quantity': product.stock_quantity,
        'category': product.category_set.first().name if product.category_set.exists() else None
    })

    