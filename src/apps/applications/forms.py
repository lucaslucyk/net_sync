from django.forms import ModelForm, PasswordInput, HiddenInput
from apps.applications import models


class CredentialParameterForm(ModelForm):
    class Meta:
        model = models.CredentialParameter
        fields = ('credential', 'key', 'value')
        widgets = {
            'value': PasswordInput(render_value=True),
        }
