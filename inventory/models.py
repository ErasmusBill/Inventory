from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser,BaseUserManager

# Create your models here.

class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser model to handle user creation.
    """

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model to differentiate between admin and salesperson
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('salesperson', 'Salesperson'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.username
class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    stock_quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)],help_text="Current stock quantity")
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0)])
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(blank=True,null=True)

    def __str__(self):
        return self.product_name
    
    def update_quantity(self, quantity_change):
        """
        Method to update product quantity
        Can be used for sales, restocking, etc.
        """
        self.stock_quantity += quantity_change
        self.save()
    
class Category(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Sale(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True, related_name='sales') 
    date = models.DateTimeField(auto_now=True) 
    quantity_sold = models.PositiveIntegerField() 
    unit_price = models.DecimalField(max_digits=10,decimal_places=2, validators=[MinValueValidator(0)])
    total_sale = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_sold} units"
    
    def save(self, *args, **kwargs):
        self.total_sale = self.quantity_sold * self.unit_price
        super().save(*args, **kwargs)
