# django
#from django.shortcuts import render
#from django.contrib.auth.models import User
#from django.http import Http404
from django.db.models import Q
#from django.http import HttpResponse

# rest_framework
# from rest_framework import generics, status
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.fields import CurrentUserDefault
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.renderers import HTMLFormRenderer
from rest_framework.decorators import action
from rest_framework.response import Response
# own
from apps.applications import models
from . import serializers

class BaseViewSet:
    permission_classes = [permissions.IsAuthenticated]
    #http_method_names = ['get', 'head', 'options', 'post', 'put', 'delete']

    @action(detail=False)
    def blank_form(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanyViewSet(BaseViewSet, viewsets.ModelViewSet):
    """
    list:
    ViewSet to list Companies of current user.

    create:
    ViewSet to create a new Company.

    blank_form:
    ViewSet to get a blank form for a new Company.

    read:
    ViewSet to get a Company detail.

    update:
    ViewSet to update a complete Company with form data.

    partial_update:
    ViewSet to partial update Company with form data.

    delete:
    ViewSet to delete a Company.
    """
    
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
