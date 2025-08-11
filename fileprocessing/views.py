from rest_framework.views import APIView
from .models import FileUpload, ActivityLog
from rest_framework.permissions import IsAuthenticated
from payment.models import PaymentTransaction
from payment.choices import StatusChoice
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer, ActivityLogSerializer
from rest_framework import generics
from utils.logger import ActivityLogger
from .tasks import count_words

class FileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def has_unused_payment(self, request):
        total_payment = PaymentTransaction.objects.filter(user=request.user, status=StatusChoice.PAID).count()
        total_file_upload = FileUpload.objects.filter(user=request.user).count()

        return total_payment > total_file_upload

    def post(self, request):
        if not self.has_unused_payment(request):
            return Response(
                {"detail": "Payment required. Please complete payment before uploading file"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file_upload = serializer.save(user=request.user)
            
            ActivityLogger.log_file_upload(request.user, serializer.data.get("filename"))
            count_words.delay(file_upload.file_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FileListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FileUploadSerializer
    queryset = FileUpload.objects.select_related("user")

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs

class ActivityLogList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer
    queryset = ActivityLog.objects.select_related("user")

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs