import logging

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth.models import User
from .serializers import UserSerializer

logger = logging.getLogger(__name__)


class CustomUserViewset(viewsets.ModelViewSet):
    """
    API endpoints to User objects
    - Anyone can create user
    - Authenticated user can view/update their own data
    - Staff can view/update all data
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        try:
            user = self.request.user
            qs = super().get_queryset()

            if not user.is_staff:
                qs = qs.filter(username=user)

            return qs
        except Exception as e:
            logger.error(
                f"Error occure in get_queryset method in UserViewset => {e}",
                exc_info=True,
            )
            return User.objects.none()