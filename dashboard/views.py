from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from fileprocessing.models import FileUpload, ActivityLog
from payment.models import PaymentTransaction

@login_required
def dashboard(request):
    files = FileUpload.objects.all()
    payments = PaymentTransaction.objects.all()
    activities = ActivityLog.objects.all()

    context = {
        'files': files,
        'payments': payments,
        'activities': activities
    }

    return render(request, 'dashboard/dashboard.html', context)
