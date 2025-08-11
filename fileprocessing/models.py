from django.db import models
from user.models import CustomUser
from .choices import StatusChoice
import uuid

class FileUpload(models.Model):
    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="file_uploads")
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=100)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=StatusChoice.choices, default=StatusChoice.PROCESSING)
    word_count = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"file id is = {self.file_id}, uploaded by {self.user.username}"

class ActivityLog(models.Model):
    activity_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=50)
    metadata = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity id: {self.activity_id}, user: {self.user.username}"

