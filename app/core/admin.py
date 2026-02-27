from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _  # noqa

from core import models

# Register your models here.


class UserAdmin(BaseUserAdmin):
    """Define admin model for custom User model"""

    ordering = ['id']
    list_display = ['username', 'name', 'email', 'is_staff']

    # Customize the admin form layout
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    readonly_fields = ('last_login',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'name',
                       'is_staff', 'is_superuser', 'is_active'),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Product)
admin.site.register(models.Tag)
admin.site.register(models.Ingredients)
