from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'credentials', views.CredentialViewSet)
router.register(r'credential-parameters', views.CredentialParameterViewSet)
router.register(r'syncs', views.SyncViewSet)
router.register(r'sync-parameters', views.SyncParameterViewSet)
router.register(r'sync-history', views.SyncHistoryViewSet)

# # credentials path
# credential_urls = [
#     path('create', views.CredentialCreateView.as_view()),
#     path('list', views.CredentialListView.as_view(), name='credential-list'),
#     path(
#         'detail/<int:pk>',
#         views.CredentialDetailView.as_view(),
#         name='credential-detail'
#     ),
# ]

# company_urls = [
#     path('list', views.CompanyListView.as_view(), name='company-list'),
#     path(
#         'detail/<int:pk>',
#         views.CompanyDetailView.as_view(),
#         name='company-detail'
#     ),
# ]

urlpatterns = [
    # path('credentials/', include(credential_urls)),
    # path('companies/', include(company_urls)),
    path('v2.0/', include(router.urls))
]
