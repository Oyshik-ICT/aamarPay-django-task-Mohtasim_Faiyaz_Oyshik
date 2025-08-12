import logging

from rest_framework import serializers

from .models import ActivityLog, FileUpload

logger = logging.getLogger(__name__)


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = [
            "file_id",
            "user",
            "file",
            "filename",
            "upload_time",
            "status",
            "word_count",
        ]

        extra_kwargs = {
            "file_id": {"read_only": True},
            "user": {"read_only": True},
            "filename": {"read_only": True},
            "upload_time": {"read_only": True},
            "status": {"read_only": True},
            "word_count": {"read_only": True},
        }

    def create(self, validated_data):
        try:
            file = validated_data.get("file")
            validated_data["filename"] = file.name
            return super().create(validated_data)
        except Exception as e:
            logger.error(f"Error creating file upload instance=> {e}", exc_info=True)
            raise


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ["activity_id", "user", "action", "metadata", "timestamp"]
