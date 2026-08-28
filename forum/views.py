from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Max
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from accounts.mixins import ModeratorOrAdminRequiredMixin

from .models import ForumCategory, ForumThread, ForumPost
from .forms import ForumThreadForm, ForumPostForm







class ForumHomeView(ListView):
    model = ForumCategory
    template_name = 'forum/forum_home.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return ForumCategory.objects.filter(is_active=True).annotate(
            threads_count=Count('threads', distinct=True),
            posts_count=Count('threads__posts', distinct=True),
            last_activity=Max('threads__posts__created_at')
        )


class CategoryDetailView(DetailView):
    model = ForumCategory
    template_name = 'forum/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        threads_list = self.object.threads.select_related('author').annotate(
            posts_count=Count('posts'),
            last_activity=Max('posts__created_at')
        ).order_by('-is_pinned', '-created_at')

        paginator = Paginator(threads_list, 10)
        page = self.request.GET.get('page')
        context['threads'] = paginator.get_page(page)
        return context


class ThreadDetailView(DetailView):
    model = ForumThread
    template_name = 'forum/thread_detail.html'
    context_object_name = 'thread'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts_list = self.object.posts.select_related('author').order_by('created_at')

        paginator = Paginator(posts_list, 15)
        page = self.request.GET.get('page')
        context['posts'] = paginator.get_page(page)
        return context



class ForumPostCreateView(LoginRequiredMixin, CreateView):
    model = ForumPost
    form_class = ForumPostForm
    template_name = "forum/post_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.thread = get_object_or_404(ForumThread, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.thread = self.thread
        return super().form_valid(form)

    def get_success_url(self):
        return self.thread.get_absolute_url()



class ForumThreadUpdateView(
    ModeratorOrAdminRequiredMixin,
    UpdateView
):
    model = ForumThread
    form_class = ForumThreadForm
    template_name = "forum/thread_update.html"

    def form_valid(self, form):
        messages.success(self.request, "Гілку успішно змінено.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("forum:category_detail", args=[self.object.category.slug])



class ForumThreadCreateView(
    ModeratorOrAdminRequiredMixin,
    CreateView
):
    model = ForumThread
    form_class = ForumThreadForm
    template_name = "forum/thread_create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Гілку успішно створено.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("forum:category_detail", args=[self.object.category.slug])


class ForumThreadDeleteView(
    ModeratorOrAdminRequiredMixin,
    DeleteView
):
    model = ForumThread
    template_name = "forum/thread_confirm_delete.html"

    def get_success_url(self):
        return reverse("forum:category_detail", args=[self.object.category.slug])

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Гілку успішно видалено.")
        return super().delete(request, *args, **kwargs)

class ForumPostUpdateView(LoginRequiredMixin, UpdateView):
    model = ForumPost
    fields = ["content"]
    template_name = "forum/post_update.html"

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            messages.error(request, "У вас немає прав для цієї дії.")
            return redirect(post.thread.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.edited = True
        messages.success(self.request, "Повідомлення успішно змінено.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.thread.get_absolute_url()

class ForumPostDeleteView(LoginRequiredMixin, DeleteView):
    model = ForumPost
    template_name = "forum/post_delete.html"

    def get_success_url(self):
        return self.object.thread.get_absolute_url()

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()

        # Автор може видаляти своє повідомлення
        if post.author == request.user:
            return super().dispatch(request, *args, **kwargs)

        messages.error(request, "У вас немає прав для цієї дії.")
        return redirect(post.thread.get_absolute_url())





    