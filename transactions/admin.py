from django.contrib import admin
from .models import Transaction, User

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'name', 'phone', 'email', 'amount', 'transaction_date', 'status')
    search_fields = ('transaction_id', 'name', 'phone', 'email')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_type', 'email')
    search_fields = ('username', 'email')


# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     model = User
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('user_type',)}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('user_type',)}),
#     )