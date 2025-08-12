import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.choices import StatusChoice
from payment.models import PaymentTransaction
from utils.logger import ActivityLogger

from .models import ActivityLog, FileUpload
from .serializers import ActivityLogSerializer, FileUploadSerializer
from .tasks import count_words

logger = logging.getLogger(__name__)


class FileUploadAPIView(APIView):
    """
    API view to handle file uploads by Authenticated user.
    Allow file uploads only if the user paid for more uploads than they have already used
    """

    permission_classes = [IsAuthenticated]

    def has_unused_payment(self, request):
        """
        Check user have more paid transactions than file upload
        """
        try:
            total_payment = PaymentTransaction.objects.filter(
                user=request.user, status=StatusChoice.PAID
            ).count()
            total_file_upload = FileUpload.objects.filter(user=request.user).count()

            return total_payment > total_file_upload
        except Exception as e:
            logger.error(
                f"Error checking unused payment for user {request.user}=> {e}",
                exc_info=True,
            )
            return False

    def post(self, request):
        """
        Handle post request to upload file
        """
        try:
            if not self.has_unused_payment(request):
                return Response(
                    {
                        "detail": "Payment required. Please complete payment before uploading file"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer = FileUploadSerializer(data=request.data)
            if serializer.is_valid():
                file_upload = serializer.save(user=request.user)

                ActivityLogger.log_file_upload(
                    request.user, serializer.data.get("filename")
                )
                count_words.delay(file_upload.file_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error occure during file upload=> {e}", exc_info=True)
            return Response(
                {"detail": "Server error during file upload"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileListView(generics.ListAPIView):
    """
    API view to list upload files
    Staff user can see all files and regular user sees only their own
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FileUploadSerializer
    queryset = FileUpload.objects.select_related("user")

    def get_queryset(self):
        try:
            qs = super().get_queryset()
            user = self.request.user
            if not user.is_staff:
                qs = qs.filter(user=user)

            return qs
        except Exception as e:
            logger.error(f"Error occure fetching file list=> {e}", exc_info=True)
            return FileUpload.objects.none()


class ActivityLogList(generics.ListAPIView):
    """
    API view to list activity logs.
    Staff user can see all logs and regular user sees only their own
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer
    queryset = ActivityLog.objects.select_related("user")

    def get_queryset(self):
        try:
            qs = super().get_queryset()
            user = self.request.user
            if not user.is_staff:
                qs = qs.filter(user=user)

            return qs
        except Exception as e:
            logger.error(f"Error occure fetching logs list=> {e}", exc_info=True)
            return ActivityLog.objects.none()
