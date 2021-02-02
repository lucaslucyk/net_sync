from django.shortcuts import render
from django.contrib.auth.models import User

#from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.fields import CurrentUserDefault

from apps.applications import models
from .serializers import CredentialSerializer, CompanySerializer


class CompanyListView(APIView):
    serializer_class = CompanySerializer

    def get(self, request, format=None):
        
        if request.user.is_superuser:
            _ac = models.Company.objects.all()
        else:
            _ac = request.user.company_set.all()

        # if no companies active
        if not _ac:
            return Response([], status=status.HTTP_204_NO_CONTENT)

        data = self.serializer_class(_ac, many=True).data
        return Response(data, status=status.HTTP_200_OK)

class CredentialListView(APIView):
    serializer_class = CredentialSerializer

    def get(self, request, format=None):
        
        if request.user.is_superuser:
            _ac = models.Company.objects.all()
            _cs = models.Credential.objects.all()
        else:
            _ac = request.user.company_set.all()
            _cs = models.Credential.objects.filter(company__in=_ac)

        # if no companies active
        if not _ac or not _cs:
            return Response([], status=status.HTTP_204_NO_CONTENT)

        data = self.serializer_class(_cs, many=True).data
        return Response(data, status=status.HTTP_200_OK)

class CredentialCreateView(generics.CreateAPIView):

    queryset = models.Credential.objects.all()
    serializer_class = CredentialSerializer


# class CredentialListView(generics.ListAPIView):

#     queryset = models.Credential.objects.all()
#     serializer_class = CredentialSerializer
