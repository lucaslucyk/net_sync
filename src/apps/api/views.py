from django.shortcuts import render
#from django.http import HttpResponse
from rest_framework import generics

from apps.applications import models
from .serializers import CredentialSerializer


class CredentialCreateView(generics.CreateAPIView):

    queryset = models.Credential.objects.all()
    serializer_class = CredentialSerializer


class CredentialListView(generics.ListAPIView):

    queryset = models.Credential.objects.all()
    serializer_class = CredentialSerializer
