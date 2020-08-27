from django.contrib import admin
from apps.applications import models
from apps.applications import forms

# Register your models here.

# @admin.register(models.CredentialParameter)
# class CredentialParametersAdmin(admin.ModelAdmin):

#     #fields = ('credential', 'key', 'value')
#     list_display = ('credential', 'key', 'value')

#     form = forms.CredentialParameterForm


class CredParametersInLine(admin.StackedInline):
    model = models.CredentialParameter
    extra = 0
    ordering = ("credential__application", 'key')
    form = forms.CredentialParameterForm

    #autocomplete_fields = ["credential"]


@admin.register(models.Credential)
class CredentialAdmin(admin.ModelAdmin):

    inlines = [CredParametersInLine]
    list_display = ('application', 'comment')
    search_fields = ["application", "comment"]
    #autocomplete_fields = ['application']


# @admin.register(models.SyncParameter)
# class SyncParametersAdmin(admin.ModelAdmin):

#     fields = ('sync', 'use_in', 'key', 'value')
#     list_display = ('sync', 'use_in', 'key', 'value')


class SyncParamsInline(admin.StackedInline):
    model = models.SyncParameter
    extra = 0
    ordering = ("sync__synchronize", 'key')
    form = forms.SyncParameterForm


@admin.register(models.Sync)
class SyncsAdmin(admin.ModelAdmin):

    inlines = [SyncParamsInline]
    fields = ('synchronize', 'origin', 'destiny')
    list_display = ('synchronize', 'origin', 'destiny', 'is_valid')

    autocomplete_fields = ["origin", "destiny"]

    actions = ['execute']

    def execute(self, request, queryset):
        for sync in queryset:
            sync.run()

    execute.short_description = "Execute"

@admin.register(models.SyncHistory)
class SyncHistoryAdmin(admin.ModelAdmin):

    readonly_fields = ["sync", "ok", "date_time", "error"]
    list_display = ["sync", "date_time", "ok"]

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

