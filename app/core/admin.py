from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        ('Basic Info', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        ('Important dates', {'fields': ('last_login',)}),
    )


admin.site.register(models.User, UserAdmin)
