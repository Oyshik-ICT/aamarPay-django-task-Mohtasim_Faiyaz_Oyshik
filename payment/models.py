from django.db import models
from user.models import CustomUser
from .choices import StatusChoice
import uuid

class PaymentTransaction(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="paymentTransactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    status = models.CharField(max_length=15, default=StatusChoice.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment_id is {self.payment_id}, user is {self.user.username}"

