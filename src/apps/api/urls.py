from django.urls import path, include
from .views import CredentialCreateView, CredentialListView, CompanyListView

# credentials path
credential_urls = [
    path('create', CredentialCreateView.as_view()),
    path('list', CredentialListView.as_view()),
]

company_urls = [
    path('list', CompanyListView.as_view()),
]

urlpatterns = [
    path('credentials/', include(credential_urls)),
    path('companies/', include(company_urls))
]
