from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from blog.forms import BlogpostForm, BlogCategoryForm
from blog.models import Category, Tags, Post
import datetime
import json
import math


# Create your views here.


@login_required
def admin_category_list(request):
    blog_categories = Category.objects.all()
    return render(request, 'admin/blog/blog-category-list.html', {'blog_categories': blog_categories})


@login_required
def new_blog_category(request):
    if request.method == 'POST':
        validate_blogcategory = BlogCategoryForm(request.POST)
        if validate_blogcategory.is_valid():
            validate_blogcategory.save()
            data = {'error': False, 'response': 'Blog category created'}
        else:
            data = {'error': True, 'response': validate_blogcategory.errors}
        return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')

    if request.user.is_superuser:
        c = {}
        c.update(csrf(request))
        return render(request, 'admin/blog/blog-category.html', {'csrf_token': c['csrf_token']})
    else:
        return render_to_response('admin/accessdenied.html')


@login_required
def edit_category(request, category_slug):
    blog_category = get_object_or_404(Category, slug=category_slug)
    if request.method == 'POST':
        validate_blogcategory = BlogCategoryForm(request.POST, instance=blog_category)
        if validate_blogcategory.is_valid():
            validate_blogcategory.save()
            data = {'error': False, 'response': 'Blog category updated'}
        else:
            data = {'error': True, 'response': validate_blogcategory.errors}
        return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')

    if request.user.is_superuser:
        c = {}
        c.update(csrf(request))
        return render(request, 'admin/blog/blog-category-edit.html',
                      {'blog_category': blog_category, 'csrf_token': c['csrf_token']})
    else:
        return render_to_response('admin/accessdenied.html')


@login_required
def delete_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    if request.user.is_superuser:
        category.delete()
        return HttpResponseRedirect('/blog/category-list/')
    else:
        return render_to_response('admin/accessdenied.html')


def site_blog_home(request):
    items_per_page = 10
    if "page" in request.GET:
        if not request.GET.get('page').isdigit():
            raise Http404
        page = int(request.GET.get('page', 1))
    else:
        page = 1

    posts = Post.objects.filter(status='P')
    no_pages = int(math.ceil(float(posts.count()) / items_per_page))
    blog_posts = posts.order_by('-updated_on')[(page - 1) * items_per_page:page * items_per_page]

    c = {}
    c.update(csrf(request))
    return render(request, 'site/blog/index.html', {'current_page': page, 'last_page': no_pages,
                                                    'posts': blog_posts, 'csrf_token': c['csrf_token']})


def blog_article(request, slug):
    blog_post = get_object_or_404(Post, slug=slug)
    blog_posts = Post.objects.filter(status='P')[:3]
    # fb = requests.get('http://graph.facebook.com/?id=https://micropyramid.com//blog/'+slug)
    # tw = requests.get('http://urls.api.twitter.com/1/urls/count.json?url=https://micropyramid.com//blog/'+slug)
    # r2=requests.get('https://plusone.google.com/_/+1/fastbutton?url= https://keaslteuzq.localtunnel.me/blog/'+slug)
    # ln = requests.get('https://www.linkedin.com/countserv/count/share?url=https://micropyramid.com/blog/'+slug+'&format=json')
    minified_url = ''
    '''
    if 'HTTP_HOST' in request.META.keys():
        minified_url = google_mini('https://' + request.META['HTTP_HOST'] + reverse('micro_blog:blog_article', kwargs={'slug': slug}), 'AIzaSyDFQRPvMrFyBNouOLQLyOYPt-iHG0JVxss')

    linkedin = {}
    linkedin.update(ln.json())
    facebook = {}
    facebook.update(fb.json() if fb else {})
    twitter = {}
    twitter.update(tw.json())
    fbshare_count = 0
    twshare_count = 0
    lnshare_count = 0
    try:
        if facebook['shares']:
            fbshare_count = facebook['shares']
    except Exception:
        pass
    try:
        if twitter['count']:
            twshare_count = twitter['count']
    except Exception:
        pass
    try:
        if linkedin['count']:
            lnshare_count = linkedin['count']
    except Exception:
        pass
        '''
    c = {}
    c.update(csrf(request))
    return render(request, 'site/blog/article.html', {'csrf_token': c['csrf_token'],
                                                      'post': blog_post, 'posts': blog_posts,
                                                      # 'fbshare_count': fbshare_count,'twshare_count': twshare_count, 'lnshare_count': lnshare_count,
                                                      'minified_url': minified_url}
                  )


def blog_tag(request, slug):
    tag = get_object_or_404(Tags, slug=slug)
    blog_posts = Post.objects.filter(tags__in=[tag], status="P").order_by('-updated_on')
    items_per_page = 6
    if "page" in request.GET:
        if not request.GET.get('page').isdigit():
            raise Http404
        page = int(request.GET.get('page'))
    else:
        page = 1
    no_pages = int(math.ceil(float(blog_posts.count()) / items_per_page))
    blog_posts = blog_posts[(page - 1) * items_per_page:page * items_per_page]
    if not blog_posts:
        raise Http404
    c = {}
    c.update(csrf(request))
    return render(request, 'site/blog/index.html', {'current_page': page,
                                                    'last_page': no_pages, 'posts': blog_posts,
                                                    'csrf_token': c['csrf_token']})


def blog_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    blog_posts = Post.objects.filter(category=category, status="P").order_by('-updated_on')
    items_per_page = 6
    if "page" in request.GET:
        if not request.GET.get('page').isdigit():
            raise Http404
        page = int(request.GET.get('page'))
    else:
        page = 1
    no_pages = int(math.ceil(float(blog_posts.count()) / items_per_page))
    blog_posts = blog_posts[(page - 1) * items_per_page:page * items_per_page]
    if not blog_posts:
        raise Http404
    c = {}
    c.update(csrf(request))
    return render(request, 'site/blog/index.html', {'current_page': page, 'last_page': no_pages,
                                                    'posts': blog_posts, 'csrf_token': c['csrf_token']})


def archive_posts(request, year, month):
    blog_posts = Post.objects.filter(status="P", updated_on__year=year, updated_on__month=month).order_by('-updated_on')
    items_per_page = 6
    if "page" in request.GET:
        if not request.GET.get('page').isdigit():
            raise Http404
        page = int(request.GET.get('page'))
    else:
        page = 1
    no_pages = int(math.ceil(float(blog_posts.count()) / items_per_page))
    blog_posts = blog_posts[(page - 1) * items_per_page:page * items_per_page]
    if not blog_posts:
        raise Http404
    c = {}
    c.update(csrf(request))
    return render(request, 'site/blog/index.html', {'current_page': page, 'last_page': no_pages,
                                                    'posts': blog_posts, 'csrf_token': c['csrf_token']})


@login_required
def admin_post_list(request):
    blog_posts = Post.objects.all().order_by('-created_on')
    return render(request, 'admin/blog/blog-posts.html', {'blog_posts': blog_posts})


@login_required
def new_post(request):
    if request.method == 'POST':
        validate_blog = BlogpostForm(request.POST)
        if validate_blog.is_valid():
            blog_post = validate_blog.save(commit=False)
            blog_post.user = request.user
            blog_post.meta_description = request.POST['meta_description']
            blog_post.status = 'D'
            if request.POST.get('status') == "P":
                if request.user.user_roles == "Admin" or request.user.is_special or request.user.is_superuser:
                    blog_post.status = 'P'

            elif request.POST.get('status') == "T":
                if request.user.user_roles == "Admin" or request.user.is_special or request.user.is_superuser:
                    blog_post.status = 'T'
            blog_post.save()
            if request.POST.get('tags', ''):
                tags = request.POST.get('tags')
                tags = tags.split(',')
                for tag in tags:
                    blog_tag = Tags.objects.filter(name=tag)
                    if blog_tag:
                        blog_tag = blog_tag[0]
                    else:
                        blog_tag = Tags.objects.create(name=tag)
                    blog_post.tags.add(blog_tag)

            blog_url = 'https://www.micropyramid.com/blog/view-post/' + str(blog_post.slug) + '/'
            message = '<p>New blog post has been created by ' + str(request.user) + ' with the name ' + str(
                blog_post.title) + ' in the category '
            message += str(
                blog_post.category.name) + '.</p>' + '<p>Please <a href="' + blog_url + '">click here</a> to view the blog post in the site.</p>'

            data = {'error': False, 'response': 'Blog Post created'}
        else:
            data = {'error': True, 'response': validate_blog.errors}
        return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')

    categories = Category.objects.all()
    c = {}
    c.update(csrf(request))
    return render(request, 'admin/blog/blog-new.html', {'categories': categories, 'csrf_token': c['csrf_token']})


@login_required
def edit_blog_post(request, blog_slug):
    if request.method == 'POST':
        current_post = get_object_or_404(Post, slug=blog_slug)
        validate_blog = BlogpostForm(request.POST, instance=current_post)
        if validate_blog.is_valid():
            blog_post = validate_blog.save(commit=False)
            blog_post.meta_description = request.POST['meta_description']
            blog_post.status = 'D'
            if request.POST.get('status') == "P":
                if request.user.user_roles == "Admin" or request.user.is_special or request.user.is_superuser:
                    blog_post.status = 'P'
            elif request.POST.get('status') == "T":
                if request.user.user_roles == "Admin" or request.user.is_special or request.user.is_superuser:
                    blog_post.status = 'T'
            blog_post.save()
            blog_post.tags.clear()
            if request.POST.get('tags', ''):
                for tag in blog_post.tags.all():
                    blog_post.tags.remove(tag)
                tags = request.POST.get('tags')
                tags = tags.split(',')
                for tag in tags:
                    blog_tag = Tags.objects.filter(name=tag)
                    if blog_tag:
                        blog_tag = blog_tag[0]
                    else:
                        blog_tag = Tags.objects.create(name=tag)

                    blog_post.tags.add(blog_tag)
            data = {'error': False, 'response': 'Blog Post edited'}
        else:
            data = {'error': True, 'response': validate_blog.errors}
        return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')

    blog_post = get_object_or_404(Post, slug=blog_slug)
    categories = Category.objects.all()
    if request.user.is_superuser or blog_post.user == request.user:
        c = {}
        c.update(csrf(request))
        return render(request, 'admin/blog/blog-edit.html',
                      {'blog_post': blog_post, 'categories': categories, 'csrf_token': c['csrf_token']})
    else:
        return render_to_response('admin/accessdenied.html')


@login_required
def delete_post(request, blog_slug):
    blog_post = get_object_or_404(Post, slug=blog_slug)
    if request.user == blog_post.user or request.user.is_superuser:
        blog_post.delete()
        data = {"error": False, 'message': 'Blog Post Deleted'}
    else:
        data = {"error": True, 'message': 'Admin or Owner can delete blog post'}
    return HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')


@login_required
def view_post(request, blog_slug):
    blog_post = get_object_or_404(Post, slug=blog_slug)
    return render(request, 'admin/blog/view_post.html', {'post': blog_post})


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
