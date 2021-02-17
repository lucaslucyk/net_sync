from django.urls import path #, include
from .views import index

urlpatterns = [
    path('', index),
    path('login', index),
    path('logout', index),
    path('companies', index),
    path('credentials', index),
    path('syncs', index),
    path('sync-logs', index),
    path('profile', index),
    path('user-mgmt', index),
    path('help', index),
]
