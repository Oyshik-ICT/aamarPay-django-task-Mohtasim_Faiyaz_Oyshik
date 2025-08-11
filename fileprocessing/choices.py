from django.db import models

class StatusChoice(models.TextChoices):
        PROCESSING = "Processing", "Processing"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"