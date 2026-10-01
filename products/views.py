from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from .forms import ProductForm
from .models import Product
from bookmarks.utils import is_bookmarked_by


@login_required
@require_http_methods(["GET", "POST"])
def product_create_view(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        return redirect(product)

    return render(
        request,
        "products/product_create.html",
        {"form": form, "editing": False},
    )


@login_required
@require_http_methods(["GET", "POST"])
def product_update_view(request, id):
    product = get_object_or_404(Product, id=id, owner=request.user)
    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(product)

    return render(
        request,
        "products/product_create.html",
        {"form": form, "editing": True, "product": product},
    )


def product_list_view(request):
    products = Product.objects.select_related("owner").filter(is_hidden=False)
    query = request.GET.get("q", "").strip()
    kind = request.GET.get("kind", "all")
    sort_by = request.GET.get("sort", "featured")

    if query:
        products = products.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(owner__username__icontains=query)
        )

    valid_kinds = {"all", *Product.Kind.values}
    if kind not in valid_kinds:
        kind = "all"
    if kind != "all":
        products = products.filter(kind=kind)

    ordering = {
        "featured": ("-featured", "title"),
        "price-low": ("price", "title"),
        "price-high": ("-price", "title"),
        "title": ("title",),
    }
    if sort_by not in ordering:
        sort_by = "featured"
    products = products.order_by(*ordering[sort_by])

    page_obj = Paginator(products, 12).get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "products/product_list.html",
        {
            "products": page_obj.object_list,
            "page_obj": page_obj,
            "listing_count": page_obj.paginator.count,
            "search_query": query,
            "active_kind": kind,
            "sort_by": sort_by,
            "query_string": query_params.urlencode(),
        },
    )


def product_detail_view(request, id):
    products = Product.objects.select_related("owner")
    if request.user.is_authenticated:
        products = products.filter(Q(is_hidden=False) | Q(owner=request.user))
    else:
        products = products.filter(is_hidden=False)
    product = get_object_or_404(products, id=id)
    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
            "is_bookmarked": is_bookmarked_by(request.user, product),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def product_delete_view(request, id):
    product = get_object_or_404(Product, id=id, owner=request.user)
    if request.method == "POST":
        product.delete()
        return redirect("products:product-list")
    return render(request, "products/product_delete.html", {"object": product})