import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render

from fileprocessing.models import ActivityLog, FileUpload
from payment.models import PaymentTransaction

logger = logging.getLogger(__name__)


@staff_member_required
def dashboard(request):
    """
    Render dashboard page, showing all user's files, payments and activity logs. Only staff member can do this .
    """
    try:
        files = FileUpload.objects.all().order_by("-upload_time")
        payments = PaymentTransaction.objects.all().order_by("-timestamp")
        activities = ActivityLog.objects.all().order_by("-timestamp")

        context = {"files": files, "payments": payments, "activities": activities}

        return render(request, "dashboard/dashboard.html", context)
    except Exception as e:
        logger.error(f"Error fetch dashboard data=> {e}", exc_info=True)
        return JsonResponse({"message": "Error loading dashboard data"}, status=500)
