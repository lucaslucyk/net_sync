from django.urls import path #, include
from .views import index

urlpatterns = [
    path('', index),
    #path('dashboard', index),
    path('credentials', index),
    path('syncs', index),
    path('sync-logs', index),
    path('profile', index),
    path('user-mgmt', index),
    path('help', index),
]
