from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import ReportForm
from .models import Report
from .utils import get_report_target_url, get_reportable_object


@login_required
@require_http_methods(["GET", "POST"])
def create_report(request, model_name, object_id):
    target = get_reportable_object(request.user, model_name, object_id)
    content_type = ContentType.objects.get_for_model(target)
    target_url = get_report_target_url(target)
    existing_report = Report.objects.filter(
        reporter=request.user,
        content_type=content_type,
        object_id=target.pk,
    ).exists()

    if request.method == "POST" and not existing_report:
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.content_type = content_type
            report.object_id = target.pk
            report.save()
            return render(
                request,
                "reports/submitted.html",
                {"target_url": target_url},
            )
    else:
        form = ReportForm()

    return render(
        request,
        "reports/create.html",
        {
            "form": form,
            "target": target,
            "existing_report": existing_report,
            "target_url": target_url,
        },
        status=409 if existing_report else 200,
    )