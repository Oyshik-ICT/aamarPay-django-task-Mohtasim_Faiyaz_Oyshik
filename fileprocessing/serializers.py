from rest_framework import serializers
from .models import FileUpload, ActivityLog

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ["file_id", "user", "file", "filename", "upload_time", "status", "word_count"]

        extra_kwargs = {
            "file_id": {"read_only": True},
            "user": {"read_only": True},
            "upload_time": {"read_only": True},
            "status": {"read_only": True},
            "word_count": {"read_only": True}
        }

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ["activity_id", "user", "action", "metadata", "timestamp"]