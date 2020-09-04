from django.forms import ModelForm, PasswordInput, Textarea
from apps.applications import models


class CredentialParameterForm(ModelForm):
    class Meta:
        model = models.CredentialParameter
        fields = ('credential', 'key', 'value')
        widgets = {
            'value': PasswordInput(render_value=True),
        }


class SyncParameterForm(ModelForm):
    class Meta:
        model = models.SyncParameter
        fields = ('use_in', 'key', '_type', 'value')
        widgets = {
            'value': Textarea(),
        }
