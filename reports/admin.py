from django.contrib import admin, messages

from .models import Report
from .moderation import hide_reported_object


@admin.action(description="Mark selected reports resolved")
def mark_resolved(modeladmin, request, queryset):
    updated = queryset.update(status=Report.Status.RESOLVED)
    modeladmin.message_user(request, f"Marked {updated} report(s) resolved.", messages.SUCCESS)


@admin.action(description="Dismiss selected reports")
def dismiss_reports(modeladmin, request, queryset):
    updated = queryset.update(status=Report.Status.DISMISSED)
    modeladmin.message_user(request, f"Dismissed {updated} report(s).", messages.SUCCESS)


@admin.action(description="Hide reported content and resolve reports")
def hide_content(modeladmin, request, queryset):
    hidden_count = 0
    for report in queryset.select_related("content_type"):
        target = report.content_object
        if target is not None and hide_reported_object(target):
            hidden_count += 1
            report.status = Report.Status.RESOLVED
            report.save(update_fields=["status", "updated"])

    modeladmin.message_user(
        request,
        f"Hidden {hidden_count} item(s) and resolved their reports.",
        messages.SUCCESS,
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "content_type", "object_id", "reason", "status", "created")
    list_filter = ("status", "reason", "content_type", "created")
    search_fields = ("reporter__username", "details")
    readonly_fields = ("reporter", "content_type", "object_id", "created", "updated")
    actions = (mark_resolved, dismiss_reports, hide_content)