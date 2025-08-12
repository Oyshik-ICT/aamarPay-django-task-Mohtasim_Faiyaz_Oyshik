import logging

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import CustomUser

logger = logging.getLogger(__name__)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "mobile_number", "password"]

        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        try:
            password = validated_data.pop("password")
            user = CustomUser.objects.create_user(password=password, **validated_data)
            return user
        except Exception as e:
            logger.error("Error creating user =>{e}", exc_info=True)
            raise

    def update(self, instance, validated_data):
        try:
            update_fields = []
            if "password" in validated_data:
                validated_data["password"] = make_password(validated_data["password"])

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
                update_fields.append(attr)

            instance.save(update_fields=update_fields)
            return instance
        except Exception as e:
            logger.error("Error updating user =>{e}", exc_info=True)
            raise
