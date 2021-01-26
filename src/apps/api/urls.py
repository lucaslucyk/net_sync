from django.urls import path, include
from .views import CredentialCreateView, CredentialListView

# credentials path
credential_urls = [
    path('create', CredentialCreateView.as_view()),
    path('list', CredentialListView.as_view()),
]

urlpatterns = [
    path('credentials/', include(credential_urls)),
]
