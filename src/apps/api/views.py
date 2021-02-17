# django
#from django.shortcuts import render
#from django.contrib.auth.models import User
#from django.http import Http404
from django.db.models import Q

# rest_framework
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.fields import CurrentUserDefault
from rest_framework import viewsets
from rest_framework import permissions

# own
from apps.applications import models
from . import serializers

class BaseViewSet:
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head', 'options', 'post', 'put']


class CompanyViewSet(BaseViewSet, viewsets.ModelViewSet):
    queryset = models.Company.objects.all().order_by('id')
    serializer_class = serializers.CompanyListUrl
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Company.objects.all()
        
        # default
        return self.request.user.company_set.all()


class CredentialViewSet(BaseViewSet, viewsets.ModelViewSet):
    queryset = models.Credential.objects.all().order_by('id')
    serializer_class = serializers.CredentialListUrl

    def get_queryset(self):

        if self.request.user.is_superuser:
            return models.Credential.objects.all()

        # default
        _ac = self.request.user.company_set.all()
        return models.Credential.objects.filter(company__in=_ac)


class CredentialParameterViewSet(BaseViewSet, viewsets.ModelViewSet):
    queryset = models.CredentialParameter.objects.all().order_by('id')
    serializer_class = serializers.CredentialParameterListUrl

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.CredentialParameter.objects.all()
        
        # default
        _ac = self.request.user.company_set.all()
        return models.CredentialParameter.objects.filter(
            credential__company__in=_ac
        )
    


class SyncViewSet(BaseViewSet, viewsets.ModelViewSet):
    queryset = models.Sync.objects.all().order_by('id')
    serializer_class = serializers.SyncListUrl

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Sync.objects.all()

        # default
        _ac = self.request.user.company_set.all()
        return models.Sync.objects.filter(
            Q(origin__company__in=_ac) | Q(destiny__company__in=_ac)
        )

class SyncParameterViewSet(BaseViewSet, viewsets.ModelViewSet):
    queryset = models.SyncParameter.objects.all().order_by('id')
    serializer_class = serializers.SyncParameterListUrl

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.SyncParameter.objects.all()

        # default
        ac = self.request.user.company_set.all()
        return models.SyncParameter.objects.filter(
            Q(sync__origin__company__in=ac) | Q(sync__destiny__company__in=ac)
        )


class SyncHistoryViewSet(BaseViewSet, viewsets.ModelViewSet):
    queryset = models.SyncHistory.objects.all().order_by('id')
    serializer_class = serializers.SyncHistoryListUrl

    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.SyncHistory.objects.all()

        # default
        ac = self.request.user.company_set.all()
        return models.SyncHistory.objects.filter(
            Q(sync__origin__company__in=ac) | Q(sync__destiny__company__in=ac)
        )
