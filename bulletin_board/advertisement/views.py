from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404, HttpResponseRedirect

from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from registration.forms import User

from .forms import PostForm, RespondForm, ResponsesFilterForm
from .models import Post, Response
from .filters import PostFilter

from datetime import datetime
from django.shortcuts import render, redirect
from .tasks import respond_send_email, respond_accept_send_email


class PostList(ListView):
    model = Post
    ordering = '-dateCreation'
    template_name = 'flatpages/post.html'
    context_object_name = 'post'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['tim_now'] = datetime.utcnow()

        return context


class PostDetail (DetailView):
    model = Post
    template_name = 'flatpages/article.html'
    context_object_name = 'posts'


class PostsDetail(View):
    def get(self, request, pk):
        ps = Post.objects.get(id=pk)
        return render(request, "flatpages/article.html", {'ps': ps})


class PostCreate (PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('advertisement.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'flatpages/post_create.html'
    context_object_name = 'postcreate'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super(PostCreate, self).form_valid(form)


class PostDelete (PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = ('advertisement.delete_post',)
    raise_exception = True
    model = Post
    template_name = 'flatpages/post_delete.html'
    context_object_name = 'postcreate'
    success_url = reverse_lazy('post_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404("You are not allowed to edit this Post")
        return super(PostDelete, self).dispatch(request, *args, **kwargs)


class PostUpdate (PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('advertisement.change_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'flatpages/post_edit.html'
    context_object_name = 'postcreate'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:

            raise Http404("You are not allowed to edit this Post")

        return super(PostUpdate, self).dispatch(request, *args, **kwargs)


class PostItem(DetailView):
    model = Post
    template_name = 'flatpages/post_item.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Response.objects.filter(author_id=self.request.user.id).filter(post_id=self.kwargs.get('pk')):
            context['respond'] = "Откликнулся"
        elif self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).author:
            context['respond'] = "Мое_объявление"
        return context


title = str("")


class Responses(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'flatpages/responses.html'
    context_object_name = 'responses'

    def get_context_data(self, **kwargs):
        context = super(Responses, self).get_context_data(**kwargs)
        global title
        if self.kwargs.get('pk') and Post.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Post.objects.get(id=self.kwargs.get('pk')).title)
            print(title)
        context['form'] = ResponsesFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            post_id = Post.objects.get(title=title)
            context['filter_responses'] = list(Response.objects.filter(post_id=post_id).order_by('-dateCreation'))
            context['response_post_id'] = post_id.id
        else:
            context['filter_responses'] = list(Response.objects.filter(post_id__author_id=self.request.user).order_by('-dateCreation'))
        context['myresponses'] = list(Response.objects.filter(author_id=self.request.user).order_by('-dateCreation'))
        return context

    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')

        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/responses')
        return self.get(request, *args, **kwargs)


class Respond(LoginRequiredMixin, CreateView):
    model = Response
    template_name = 'flatpages/respond.html'
    form_class = RespondForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        respond = form.save(commit=False)
        respond.author = User.objects.get(id=self.request.user.id)
        respond.post = Post.objects.get(id=self.kwargs.get('pk'))
        respond.save()
        respond_send_email.delay(respond_id=respond.id)
        return redirect(f'/post/{self.kwargs.get("pk")}')


@login_required
def response_accept(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.status = True
        response.save()
        respond_accept_send_email.delay(response_id=response.id)
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def response_delete(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.delete()
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')

