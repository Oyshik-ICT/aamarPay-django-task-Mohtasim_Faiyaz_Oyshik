from django.urls import path, include
from ..views import UserViewset


urlpatterns = [
    path('', UserViewset.as_view({'post': 'create'}), name='register'),
]