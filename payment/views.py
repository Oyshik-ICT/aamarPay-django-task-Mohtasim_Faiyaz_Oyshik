import json
import logging
import uuid

import requests
from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import CustomUser
from utils.logger import ActivityLogger

from .choices import StatusChoice
from .models import PaymentTransaction
from .serializers import PaymentTransactionSerializer

logger = logging.getLogger(__name__)


def get_base_url(request):
    """
    Build the base url for current request
    """
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()
    return f"{protocol}://{domain}"


class InitiatePayment(APIView):
    """
    API view to initiate a payment request to the aamarPay payment gateway
    """

    permission_classes = [IsAuthenticated]

    def get_url_payload_header(self, request, transaction_id, base_url):
        """
        Prepare for payment gateway request URL, payloads and headers
        """
        url = settings.URL
        payload = json.dumps(
            {
                "store_id": settings.STORE_ID,
                "tran_id": transaction_id,
                "success_url": f"{base_url}/api/payment/success/",
                "fail_url": f"{base_url}/api/payment/failure/",
                "cancel_url": f"{base_url}/api/payment/cancel/",
                "amount": "100.0",
                "currency": "BDT",
                "signature_key": settings.SIGNATURE_KEY,
                "desc": "Merchant Registration Payment",
                "cus_name": request.user.username,
                "cus_email": request.user.email,
                "cus_phone": request.user.mobile_number,
                "type": "json",
            }
        )
        headers = {"Content-Type": "application/json"}

        return url, payload, headers

    def post(self, request):
        try:
            user = request.user
            transaction_id = f"PAY_{uuid.uuid4().hex[:16]}"
            PaymentTransaction.objects.create(user=user, transaction_id=transaction_id)

            base_url = get_base_url(request)
            url, payload, headers = self.get_url_payload_header(
                request, transaction_id, base_url
            )
            response = requests.request("POST", url, headers=headers, data=payload)

            return Response(response.json())
        except Exception as e:
            logger.error(
                f"Error initiating payment for user {request.user.id}=> {e}",
                exc_info=True,
            )
            return Response(
                {"detail": "Failed to initiate payment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PaymentSuccessAPIView(APIView):
    """
    API view to handle successful payment callback from aamarPay payment gateway
    """

    def post(self, request):
        try:
            gateway_data = request.data
            trans_id = gateway_data.get("mer_txnid")
            pay_status = gateway_data.get("pay_status")
            user_name = gateway_data.get("cus_name")

            if not all([gateway_data, trans_id, pay_status, user_name]):
                return Response(
                    {"detail": "Missing required parameters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = CustomUser.objects.get(username=user_name)

            try:
                payment = PaymentTransaction.objects.get(transaction_id=trans_id)
            except PaymentTransaction.DoesNotExist:
                return Response(
                    {"detail": "Payment Transaction id is not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            payment.gateway_response = gateway_data

            if pay_status == "Successful":
                payment.status = StatusChoice.PAID
            elif pay_status == "Expired":
                payment.status = StatusChoice.EXPIRED
            else:
                payment.status = StatusChoice.PENDING

            payment.save(update_fields=["status", "gateway_response"])
            base_url = get_base_url(request)

            if pay_status == "Successful":
                ActivityLogger.log_payment_info(user, trans_id, pay_status)
                return Response(
                    {
                        "message": "Payment Successful",
                        "transaction_id": trans_id,
                        "file_upload_endpoint": f"{base_url}/api/upload/",
                    }
                )
            else:
                return Response(
                    {
                        "message": f"Payment is {pay_status}",
                        "transaction_id": trans_id,
                    }
                )

        except Exception as e:
            logger.error(f"Error in payment success view=> {e}", exc_info=True)
            return Response(
                {"detail": "Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentFailureAPIView(APIView):
    """
    API view to handle failed payment callback from aamarPay payment gateway
    """

    def post(self, request):
        try:
            gateway_data = request.data
            trans_id = gateway_data.get("mer_txnid")
            user_name = gateway_data.get("cus_name")

            if not all([gateway_data, trans_id, user_name]):
                return Response(
                    {"detail": "Missing required parameters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = CustomUser.objects.get(username=user_name)

            try:
                payment = PaymentTransaction.objects.get(transaction_id=trans_id)
            except PaymentTransaction.DoesNotExist:
                return Response(
                    {"detail": "Payment Transaction id is not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            payment.gateway_response = gateway_data
            payment.status = StatusChoice.FAILED

            payment.save(update_fields=["status", "gateway_response"])
            ActivityLogger.log_payment_info(user, trans_id, "Failed")

            return Response(
                {
                    "message": "Payment is failed",
                }
            )

        except Exception as e:
            logger.error(f"Error in payment failure view=> {e}", exc_info=True)
            return Response(
                {"detail": "Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["GET"])
def payment_cancel(request):
    """
    API endpoint for when a payment is cancelled by a user
    """
    return Response({"detail": "Payment was canceled by user", "status": "cancelled"})


class TransctionsListView(generics.ListAPIView):
    """
    API view to list all payment transactions(Admin Only)
    """

    queryset = PaymentTransaction.objects.select_related("user").order_by("-timestamp")
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAdminUser]
