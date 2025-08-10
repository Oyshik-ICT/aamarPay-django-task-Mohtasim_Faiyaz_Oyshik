from django.db import models

class StatusChoice(models.TextChoices):
        PAID = "Paid", "Paid"
        PENDING = "Pending", "Pending"
        FAILED = "Failed", "Failed"
        EXPIRED = "Expired", "Expireds"