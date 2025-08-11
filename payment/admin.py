from django.contrib import admin
from .models import PaymentTransaction

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'transaction_id', 'gateway_response', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['user__username', 'transaction_id']

    def has_delete_permission(self, request, obj = None):
        return False
    def has_change_permission(self, request, obj = None):
        return False