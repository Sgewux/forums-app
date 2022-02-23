from django.shortcuts import render

from .models import Forum

def show_forums(request):
    like = request.GET.get('q', None)
    if like:
        return render(request, 'forums/forums.html',{
            'forums_list': Forum.objects.filter(name__icontains = like)
        })
    else:
        return render(request, 'forums/forums.html', {
            'forums_list': Forum.objects.all()
        })