from django.shortcuts import render
from django.http.response import HttpResponse


def index(request):
    # latest_featured_posts = {} #Post.objects.filter(status = 'P',featured_post = 'on').order_by('-created_on')[:2]
    return render(request, 'site/index.html')