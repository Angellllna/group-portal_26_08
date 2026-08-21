from django.views.generic import ListView, DetailView
from django.db.models import Count, Max
from django.core.paginator import Paginator
from .models import ForumCategory, ForumThread, ForumPost


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