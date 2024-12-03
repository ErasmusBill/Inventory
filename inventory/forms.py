from django import forms
from  .models import *
from django.contrib.auth.models import User

class SignUpForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password',widget=forms.PasswordInput)

    class Meta:
        model = User
        field = ['username','email','first_name','last_name']


        def cleaned_data(self):
            cd = self.cleaned_data
            if cd['password'] != cd['password2']:
                raise forms.ValidationError('Passwords don\'t match.')
            return cd['password2']
        

class ChangePasswordForm(forms.ModelForm):
    old_password = forms.CharField(label='Password',widget=forms.PasswordInput)
    new_password = forms.CharField(label='Password',widget=forms.PasswordInput)

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        field = ['product_name','quantity','price','date','image']
