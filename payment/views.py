from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import PaymentTransaction
from django.conf import settings
from .choices import StatusChoice
import json
import uuid
import requests
from rest_framework import status, generics
from .serializers import PaymentTransactionSerializer
from rest_framework.decorators import api_view

def get_base_url(request):
        protocol = "https" if request.is_secure() else "http"
        domain = request.get_host()
        return f"{protocol}://{domain}"

class InitiatePayment(APIView):
    permission_classes = [IsAuthenticated]

    def get_url_payload_header(self, request, transaction_id, base_url):
        url = settings.URL
        payload = json.dumps({
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
        "type": "json"
        })
        headers = {
        'Content-Type': 'application/json'
        }

        return url, payload, headers
    

    def post(self, request):
        user = request.user
        transaction_id = f"PAY_{uuid.uuid4().hex[:16]}"
        PaymentTransaction.objects.create(
            user = user,
            transaction_id = transaction_id
        )
        
        base_url = get_base_url(request)
        url, payload, headers = self.get_url_payload_header(request, transaction_id, base_url)
        response = requests.request("POST", url, headers=headers, data=payload)

        return Response(response.json())
    
class PaymentSuccessAPIView(APIView):
    def post(self, request):
        try:
            gateway_data = request.data
            trans_id = gateway_data.get("mer_txnid")
            pay_status = gateway_data.get("pay_status")

            if not all([gateway_data, trans_id, pay_status]):
                return Response(
                    {"detail": "Missing required parameters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                payment = PaymentTransaction.objects.get(transaction_id=trans_id)
            except PaymentTransaction.DoesNotExist:
                return Response(
                    {"detail": "Payment Transaction id is not found"},
                    status=status.HTTP_404_NOT_FOUND
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
                return Response({
                    "message": "Payment Successful",
                    "transaction_id": trans_id,
                    "file_upload_endpoint": f"{base_url}/api/upload/"
                })
            else:
                return Response({
                    "message": f"Payment is {pay_status}",
                    "transaction_id": trans_id,
                })

        except Exception as e:
            return Response(
                {"detail": "Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class PaymentFailureAPIView(APIView):
    def post(self, request):
        try:
            gateway_data = request.data
            trans_id = gateway_data.get("mer_txnid")

            if not all([gateway_data, trans_id]):
                return Response(
                    {"detail": "Missing required parameters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                payment = PaymentTransaction.objects.get(transaction_id=trans_id)
            except PaymentTransaction.DoesNotExist:
                return Response(
                    {"detail": "Payment Transaction id is not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            

            payment.gateway_response = gateway_data
            payment.status = StatusChoice.FAILED

            payment.save(update_fields=["status", "gateway_response"])
            base_url = get_base_url(request)

            return Response({
                    "message": "Payment is failed",
                })

        except Exception as e:
            return Response(
                {"detail": "Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])     
def payment_cancel(request):
    return Response({
        "detail": "Payment was canceled by user",
        "status": "cancelled"
    })

class TransctionsListView(generics.ListAPIView):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAdminUser]

        
