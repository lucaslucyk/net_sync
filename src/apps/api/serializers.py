# django
from rest_framework import serializers

# own
from apps.applications import models


class CompanyListUrl(serializers.HyperlinkedModelSerializer):
    #credentials = serializers.HyperlinkedModelSerializer(source='credential_set')
    class Meta:
        model = models.Company
        # fields = ('id', 'url', 'company', '')

        fields = [_f.name for _f in models.Company._meta.fields]
        fields.extend(['url', 'credential_set'])


class CredentialListUrl(serializers.HyperlinkedModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.name')
    app_display = serializers.ReadOnlyField(source='get_application_display')
    class Meta:
        model = models.Credential
        fields = [_f.name for _f in models.Credential._meta.fields]
        fields.extend([
            'url',
            'credentialparameter_set',
            'origin',
            'destiny',
            'company_name',
            'app_display'
        ])


class CredentialParameterListUrl(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CredentialParameter
        fields = [_f.name for _f in models.CredentialParameter._meta.fields]
        fields.append('url')


class SyncListUrl(serializers.HyperlinkedModelSerializer):
    
    origin_display = serializers.ReadOnlyField(source='origin.__str__')
    destiny_display = serializers.ReadOnlyField(source='destiny.__str__')
    status_display = serializers.ReadOnlyField(source='get_status_display')
    synchronize_display = serializers.ReadOnlyField(
        source='get_synchronize_display'
    )
    class Meta:
        model = models.Sync
        fields = [_f.name for _f in models.Sync._meta.fields]
        fields.extend([
            'url', 'syncparameter_set', 'origin_display', 'destiny_display',
            'status_display', 'synchronize_display'
        ])


class SyncParameterListUrl(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SyncParameter
        fields = [_f.name for _f in models.SyncParameter._meta.fields] + ['url']


class SyncHistoryListUrl(serializers.HyperlinkedModelSerializer):

    sync_display = serializers.ReadOnlyField(source='sync.__str__')

    class Meta:
        model = models.SyncHistory
        fields = [_f.name for _f in models.SyncHistory._meta.fields]
        fields.extend(['url', 'sync_display'])
