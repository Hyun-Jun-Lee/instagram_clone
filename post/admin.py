from django import forms
from django.contrib import admin
from .models import Post, Like, Bookmark, Comment

# Register your models here.



class PostForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = Post
        fields = '__all__'

# TabularInline : django.contrib.admin이 제공하는 같은 admin page에서 다른 model을 edit할 수 있는 ability를 부여

class LikeInline(admin.TabularInline):
    model = Like
    
class CommentInline(admin.TabularInline):
    model = Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'nickname', 'content', 'created_at']
    list_display_links = ['author', 'nickname', 'content']
    form = PostForm
    inlines = [LikeInline, CommentInline]
    
    def nickname(request, post):
        return post.author.profile.nickname
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'content', 'author', 'created_at']
    list_display_links = ['post', 'content', 'author']  
    
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'created_at']
    list_display_links = ['post', 'user']
    
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'created_at']
    list_display_links = ['post', 'user']    
    
