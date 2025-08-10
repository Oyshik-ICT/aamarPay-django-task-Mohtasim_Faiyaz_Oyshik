from rest_framework import serializers
from .models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ["payment_id", "user", "amount", "status", "transaction_id", "gateway_response", "timestamp"]