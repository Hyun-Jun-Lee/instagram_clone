from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post
# Create your views here.

def post_list(request):
    posts = Post.objects.all()
    
    # 로그인 상태이면 username 저장, user 모델 내용 확인, profile저장
    if request.user.is_authenticated:
        username = request.user
        user = get_object_or_404(get_user_model(), username=username)
        user_profile = user.profile        
        return render(request, 'post/post_list.html', {
            'user_profile': user_profile,
            'posts': posts,
        })
    # 로그인상태가 아니면 post 내용만 보이도록
    else:
        return render(request, 'post/post_list.html', {
            'posts': posts,
        })