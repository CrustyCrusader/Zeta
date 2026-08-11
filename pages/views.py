from django.http import HttpResponse
from django.shortcuts import render
from accounts.models import User


def home_view(request, *args, **kwargs):
    return render(request, "home.html", {})


def contact_view(request, *args, **kwargs):
    return render(request, "contact.html", {})


def about_view(request, *args, **kwargs):
    my_context = {
        "title": "abc this is about us",
        "this_is_true": True,
        "my_number": 123,
        "my_list": [1313, 4231, 312, "Abc"],
        "my_html": "<h1>Hello World</h1>",
    }
    return render(request, "about.html", my_context)


def social_view(request, *args, **kwargs):
    return HttpResponse("<h1>Social Page</h1>")


def user_search(request):
    query = request.GET.get("q", "").strip()

    users = User.objects.none()

    if query:
        users = User.objects.filter(
            username__icontains=query
        ).order_by("username")

    return render(
        request,
        "pages/user_search.html",
        {
            "query": query,
            "users": users,
        },
    )