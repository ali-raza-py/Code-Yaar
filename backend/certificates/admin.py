from django.contrib import admin, messages
from django.utils.html import format_html

from . import services
from .models import Certificate, CertificateEvent


class CertificateEventInline(admin.TabularInline):
    model = CertificateEvent
    extra = 0
    readonly_fields = ['action', 'performed_by', 'reason', 'snapshot', 'created_at']
    ordering = ('created_at', 'id')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = [
        'credential_id', 'student_name', 'course_title',
        'status_badge', 'final_score', 'issued_at', 'verify_link',
    ]
    list_filter = ['status', 'course', 'issued_at']
    search_fields = ['credential_id', 'public_id', 'student_name', 'course_title', 'user__username']
    readonly_fields = [
        'public_id', 'credential_id', 'user', 'course', 'enrollment',
        'course_title', 'issued_at', 'completion_verified_at', 'final_score',
        'policy_version', 'supersedes', 'issued_by', 'issued_automatically',
        'pdf_file', 'created_at', 'updated_at',
    ]
    actions = ['action_revoke', 'action_reissue']
    inlines = [CertificateEventInline]

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = {'active': '#15803d', 'revoked': '#b91c1c', 'superseded': '#a16207'}[obj.status]
        return format_html(
            '<span style="color:{c};font-weight:600">{label}</span>',
            c=color, label=obj.get_status_display(),
        )

    @admin.display(description='Verify')
    def verify_link(self, obj):
        return format_html('<a href="{}" target="_blank">open</a>', obj.verification_url())

    @admin.action(description='Revoke selected certificates (reason required)')
    def action_revoke(self, request, queryset):
        ok = 0
        for cert in queryset:
            if cert.status != Certificate.Status.ACTIVE:
                continue
            services.revoke_certificate(
                cert, performed_by=request.user,
                reason='Revoked via Django Admin.',
            )
            ok += 1
        self.message_user(request, f'{ok} certificate(s) revoked.', messages.SUCCESS)

    @admin.action(description='Reissue corrected certificate (supersedes original)')
    def action_reissue(self, request, queryset):
        ok = 0
        for cert in queryset:
            if cert.status == Certificate.Status.SUPERSEDED:
                continue
            try:
                services.reissue_corrected_certificate(
                    cert, performed_by=request.user,
                    reason='Corrected reissue via Django Admin.',
                )
                ok += 1
            except services.CertificateNotEligible:
                self.message_user(
                    request,
                    f'{cert.credential_id}: learner is no longer eligible; cannot reissue.',
                    messages.ERROR,
                )
        if ok:
            self.message_user(request, f'{ok} certificate(s) reissued.', messages.SUCCESS)

    def has_add_permission(self, request):
        # Certificates are only ever created through the verified issuance flow.
        return False


@admin.register(CertificateEvent)
class CertificateEventAdmin(admin.ModelAdmin):
    list_display = ['certificate', 'action', 'performed_by', 'created_at']
    list_filter = ['action']
    search_fields = ['certificate__credential_id', 'certificate__student_name', 'reason']
    readonly_fields = [f.name for f in CertificateEvent._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Audit events are append-only and immutable.
        return False
