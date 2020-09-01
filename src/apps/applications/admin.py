from django.contrib import admin
from apps.applications import models
from apps.applications import forms
from django.contrib import messages

# Register your models here.

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

class SyncParamsInline(admin.StackedInline):
    model = models.SyncParameter
    extra = 0
    ordering = ("sync__synchronize", 'key')
    form = forms.SyncParameterForm


@admin.register(models.Sync)
class SyncsAdmin(admin.ModelAdmin):

    inlines = [SyncParamsInline]
    fields = (
        'synchronize', 'origin', 'destiny', 'cron_expression', 'active',
        'status', 'get_last_run', 'get_next_run', 'needs_run'
    )
    list_display = (
        'synchronize', 'origin', 'destiny', 'active', 'is_valid', 'status',
        'get_last_run', 'get_next_run', 'needs_run'
    )
    readonly_fields = ['get_last_run', 'get_next_run', 'needs_run', 'status']
    autocomplete_fields = ['origin', 'destiny']
    list_filter = ['synchronize', 'origin', 'destiny', 'active', 'status', ]
    search_fields = [
        'synchronize', 'origin__application', 'destiny__application', 'status'
    ]

    actions = ['execute']

    def execute(self, request, queryset):
        correct = True

        for sync in queryset:
            # execute and eval result
            if not sync.run():
               correct = False 
                
        if correct:
            messages.add_message(
                request,
                messages.SUCCESS,
                'Tasks were completed.'
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                'One or more tasks could not be executed.'
        )

    execute.short_description = "Execute"

@admin.register(models.SyncHistory)
class SyncHistoryAdmin(admin.ModelAdmin):

    readonly_fields = [
        "sync", "get_origin", "get_destiny", "start_time", "end_time", "ok",
        "message"
    ]
    list_display = [
        "sync", "get_origin", "get_destiny", "start_time", "end_time", "ok"
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

