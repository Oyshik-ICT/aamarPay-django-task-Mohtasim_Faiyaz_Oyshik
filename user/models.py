from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(blank=False, null=False)
    mobile_number = models.CharField(max_length=11, blank=False, null=False)

    def __str__(self):
        return self.username