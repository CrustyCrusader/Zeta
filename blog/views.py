from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView,
)

from comments.forms import CommentForm
from comments.models import Comment

from .forms import ArticleModelForm
from .models import Article

class ArticleCreateView(LoginRequiredMixin, CreateView):
    template_name = "articles/article_create.html"
    form_class = ArticleModelForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleListView(ListView):
    template_name = "articles/article_list.html"

    def get_queryset(self):
        articles = Article.objects.all()

        print("BLOG ARTICLES:", list(
            articles.values_list("id", "title")
        ))

        return articles


class ArticleDetailView(DetailView):
    template_name = "articles/article_detail.html"

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(
            Article,
            id=self.kwargs.get("id"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        content_type = ContentType.objects.get_for_model(Article)

        context["content_type_id"] = content_type.id

        context["comments"] = (
            Comment.objects
            .filter(
                content_type=content_type,
                object_id=self.object.id,
            )
            .select_related("author")
        )

        context["comment_form"] = CommentForm()

        return context


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "articles/article_create.html"
    form_class = ArticleModelForm

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Article, id=id_)

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "articles/article_delete.html"

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Article, id=id_)

    def test_func(self):
        article = self.get_object()
        return article.author == self.request.user

    def get_success_url(self):
        return reverse("articles:article-list")