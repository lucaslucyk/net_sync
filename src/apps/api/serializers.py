from rest_framework import serializers

from apps.applications import models

class CredentialSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Credential
        fields = ('id', 'application', 'comment')