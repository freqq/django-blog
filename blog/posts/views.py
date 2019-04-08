from django.shortcuts import render, get_object_or_404, redirect, Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from comments.models import Comment
from comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from .utils import get_read_time

from .models import Post
from .forms import PostForm

def posts_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active().order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all().order_by("-timestamp")

    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(user__username__icontains=query)).distinct()

    paginator = Paginator(queryset_list, 5)
    page = request.GET.get('page')
    page_request_var = "page"
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        "page_request_var": page_request_var,
        "object_list": queryset,
        "today": today,
        "pages_number": range(1, queryset.paginator.num_pages+1)
    }
    return render(request, "post_list.html", context)


def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id
    }
    comment_form = CommentForm(request.POST or None, initial=initial_data)

    if comment_form.is_valid() and request.user.is_authenticated:
        c_type = comment_form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = comment_form.cleaned_data.get("object_id")
        content_data = comment_form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()

        new_comment = Comment.objects.get_or_create(
            user = request.user,
            content_type = content_type,
            object_id = obj_id,
            content = content_data,
            parent = parent_obj,
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = instance.comments

    context = {
        "title": instance.title,
        "instance": instance,
        "comments": comments,
        "comment_form": comment_form
    }
    return render(request, "post_detail.html", context)


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    if not request.user.is_authenticated:
       raise Http404

    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Post created.")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form
    }
    return render(request, "post_form.html", context)

def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404

    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.save() 
        messages.success(request, "Post updated.")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form": form
    }
    return render(request, "post_form.html", context)

def post_delete(request, id=None):
    if not request.user.is_staff or request.user.is_superuser:
        raise Http404

    instance = get_object_or_404(Post, id=id)
    instance.delete()
    messages.success(request, "Successfully deleted.")
    return redirect("list")
