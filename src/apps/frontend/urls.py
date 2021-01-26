from django.urls import path #, include
from .views import index

urlpatterns = [
    path('', index),
    path('credentials', index),
    path('credentials/list/', index)
]
