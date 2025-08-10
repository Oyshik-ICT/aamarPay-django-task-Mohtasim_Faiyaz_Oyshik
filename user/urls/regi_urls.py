from django.urls import path, include
from ..views import CustomUserViewset


urlpatterns = [
    path('', CustomUserViewset.as_view({'post': 'create'}), name='register'),
]