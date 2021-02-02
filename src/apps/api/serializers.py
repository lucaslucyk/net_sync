from rest_framework import serializers

from apps.applications import models

class CredentialSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Credential
        fields = [field.name for field in models.Credential._meta.fields]

class CompanySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Company
        #fields = ('id', 'name', 'country', 'phone')
        fields = [field.name for field in models.Company._meta.fields]
