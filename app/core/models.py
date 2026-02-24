"""
Database models.
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email),
                          username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password, **extra_fields):
        """Create and return a new superuser."""
        user = self.create_user(email, username, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']


class Product(models.Model):
    """Product model."""
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, default='')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
    )
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredients')

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name, price, user, description=''):
        """Create and return a new product attached to a user."""
        product = cls(name=name, price=price, user=user,
                      description=description)
        product.save()
        return product


class Tag(models.Model):
    """Tag model."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags',
    )

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Ingredients model."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ingredients',
    )

    def __str__(self):
        return self.name
