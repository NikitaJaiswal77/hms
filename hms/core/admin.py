from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Availability, Booking


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Availability)
admin.site.register(Booking)