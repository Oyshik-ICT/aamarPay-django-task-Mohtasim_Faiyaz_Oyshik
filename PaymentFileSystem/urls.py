"""
URL configuration for PaymentFileSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from payment.views import InitiatePayment, PaymentSuccessAPIView, PaymentFailureAPIView, payment_cancel, TransctionsListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", include("user.urls.token_urls")),
    path("api/register/", include("user.urls.regi_urls")),
    path("api/user/", include("user.urls.user_urls")),
    path("api/initiate-payment/", InitiatePayment.as_view(), name="initiate-payment"),
    path("api/payment/success/", PaymentSuccessAPIView.as_view(), name="payment-success"),
    path("api/payment/failure/", PaymentFailureAPIView.as_view(), name="payment-failure"),
    path("api/payment/cancel/", payment_cancel, name="payment-cancel"),
    path("api/transactions/", TransctionsListView.as_view(), name="transactions-list"),
]
