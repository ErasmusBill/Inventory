from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Category, Sale
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model

class SignUpForm(UserCreationForm):
    """
    Custom SignUp Form with additional fields
    """
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('salesperson', 'Salesperson')
    ]
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES, 
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'user_type')

    def clean_email(self):
        """
        Validate email uniqueness
        """
        email = self.cleaned_data.get('email')
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Current Password', 
        widget=forms.PasswordInput
    )
    new_password1 = forms.CharField(
        label='New Password', 
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label='Confirm New Password', 
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match.")
        
        return cleaned_data

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'stock_quantity', 'price', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity is not None and stock_quantity < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        return stock_quantity

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price