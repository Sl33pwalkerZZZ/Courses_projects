from django.contrib import admin, messages
from rest_framework.exceptions import APIException
from .models import CourseSettings, ImportPreview, LessonImageDescription, PublicationEvent, PublicationRequest
from .services import decide_publication


@admin.register(PublicationRequest)
class PublicationRequestAdmin(admin.ModelAdmin):
    list_display = ['course', 'requested_by', 'status', 'created_at', 'reviewed_by']
    list_filter = ['status']
    readonly_fields = ['course', 'requested_by', 'status', 'source_reviewed', 'assessment_reviewed', 'fingerprint', 'reviewed_by', 'created_at', 'reviewed_at']
    actions = ['approve_requests', 'reject_requests']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + (['note'] if obj and obj.status != 'pending' else [])

    @admin.action(description='Approve and publish reviewed courses', permissions=['change'])
    def approve_requests(self, request, queryset):
        self.decide(request, queryset, 'approve')

    @admin.action(description='Reject with saved feedback note', permissions=['change'])
    def reject_requests(self, request, queryset):
        self.decide(request, queryset, 'reject')

    def decide(self, request, queryset, decision):
        for review in queryset:
            try:
                decide_publication(request_id=review.pk, reviewer=request.user, decision=decision, note=review.note)
                self.message_user(request, f'{review.course}: {decision}')
            except APIException as error:
                self.message_user(request, str(error.detail), messages.ERROR)


@admin.register(PublicationEvent)
class PublicationEventAdmin(admin.ModelAdmin):
    list_display = ['request', 'actor', 'decision', 'created_at']
    readonly_fields = ['request', 'actor', 'decision', 'note', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
