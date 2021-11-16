from django.contrib.auth import get_user_model
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count

# Create your views here.

def post_list(request, tag=None):
    posts = Post.objects.all()
    # CommentForm html로 넘겨주기위해
    comment_form = CommentForm()
    
    # tag로 검색되엇을 때 tag에 해당하는 포스트만 가져오기
    if tag:
        # 위에서 받아온 tag를 대소문자 구분없이 tag_set_name으로 검색
        post_list = Post.objects.filter(tag_set__name__iexact=tag) \
        .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                            'author__profile__follower_user', 'author__profile__follower_user__from_user') \
        .select_related('author__profile') # 1대1 관계에서만 가능
    else: # 아니라면 모든 post
        post_list = Post.objects.all() \
            .prefetch_related('tag_set', 'like_user_set__profile', 'comment_set__author__profile',
                              'author__profile__follower_user', 'author__profile__follower_user__from_user') \
            .select_related('author__profile')
    
    # 로그인 상태이면 username 저장, user 모델 내용 확인, profile저장
    if request.user.is_authenticated:
        username = request.user
        user = get_object_or_404(get_user_model(), username=username)
        user_profile = user.profile
        
        # following한 사람들의 피드 받아오기
        follow_set = request.user.profile.get_following
        follow_post_list = Post.objects.filter(author__profile__in=follow_set)
        
        paginator = Paginator(post_list, 3)
        page_num = request.POST.get('page')
        
        try:
            posts = paginator.page(page_num)
        except PageNotAnInteger: # page 파라미터가 int가 아니면 page(1)로 바꿈
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        # Ajax 통신이 들어왔을 때 동작(무한스크롤 가능하도록)
        if request.is_ajax(): 
            return render(request, 'post/post_list_ajax.html', {
                'posts': posts,
                'comment_form': comment_form,
        })
            
        # post_list로 POST 요청이 오면, 검색어 tag외에 필요없는 문자를 제거한 tag_cloan으로 바꾸고 \
            # 이를 추가한 post_search url로 연결
        if request.method == 'POST':
            tag = request.POST.get('tag')
            tag_clean = ''.join(e for e in tag if e.isalnum())
            return redirect('post:post_search', tag_clean)     
           
        return render(request, 'post/post_list.html', {
            'user_profile': user_profile,
            'posts': posts,
            'comment_form': comment_form,
            'follow_post_list': follow_post_list,
        })
        

        
    # 로그인상태가 아니면 post 내용만 보이도록
    else:
        return render(request, 'post/post_list.html', {
            'posts': posts,
            'comment_form': comment_form,
        })

@login_required  
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # user 정보를 넣은 뒤에 저장해야 하므로 지금은 commit=false
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # post의 tag도 같이 저장
            post.tag_save()
            messages.info(request, 'posting이 완료되었습니다')
            return redirect('post:post_list')
    else:
        form = PostForm()
    return render(request, 'post/post_new.html', {
        'form': form,
    })
    
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.warning(request, '잘못된 접근입니다')
        return redirect('post:post_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, '수정완료')
            return redirect('post:post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'post/post_edit.html', {
        'post': post,
        'form': form,
    })
    
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user or request.method == 'GET':
        messages.warning(request, '잘못된 접근입니다.')
        return redirect('post:post_list')

    if request.method == 'POST':
        post.delete()
        messages.success(request, '삭제완료')
        return redirect('post:post_list')

@login_required
@require_POST
def post_like(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_like, post_like_created = post.like_set.get_or_create(user=request.user)

    if not post_like_created:
        post_like.delete()
        message = "좋아요 취소"
    else:
        message = "좋아요"

    context = {'like_count': post.like_count,
               'message': message}
    # json.dumps() : python 객체 json으로 만들기
    return HttpResponse(json.dumps(context), content_type="application/json")

@login_required
@require_POST
def post_bookmark(request):
    pk = request.POST.get('pk', None)
    post = get_object_or_404(Post, pk=pk)
    post_bookmark, post_bookmark_created = post.bookmark_set.get_or_create(user=request.user)

    if not post_bookmark_created:
        post_bookmark.delete()
        message = "북마크 취소"
    else:
        message = "북마크"

    context = {'bookmark_count': post.bookmark_count,
               'message': message}

    return HttpResponse(json.dumps(context), content_type="application/json") 

@login_required
def comment_new(request):
    pk = request.POST.get('pk')
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return render(request, 'post/comment_new_ajax.html', {
                'comment': comment,   
            })
    return redirect("post:post_list")

# detail page에 댓글 달기 기능 추가할 때
@login_required
def comment_new_detail(request):
    pk = request.POST.get('pk')
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return render(request, 'post/comment_new_detail_ajax.html', {
                'comment': comment,
            })


@login_required
def comment_delete(request):
    pk = request.POST.get('pk')
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == 'POST' and request.user == comment.author:
        comment.delete()
        message = '삭제완료'
        status = 1
    
    else:
        message = '잘못된 접근입니다'
        status = 0
        
    return HttpResponse(json.dumps({'message': message, 'status': status, }), content_type="application/json")