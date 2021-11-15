from django.db import models
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import re
# Create your models here.

# accounts/models.py user_path 참고
def photo_path(instance, filename):
    from time import gmtime, strftime
    from random import choice
    import string
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    extension = filename.split('.')[-1]
    return '{}/{}/{}.{}'.format(strftime('post/%Y/%m/%d/'), instance.author.username, pid, extension)

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # imagekit 썸네일
    photo = ProcessedImageField(upload_to=photo_path,
                                processors=[ResizeToFill(600, 600)],
                                format='JPEG',
                                options={'quality': 90})
    
    content = models.CharField(max_length=100, help_text="최대 100자")
    
    # 생성 시각, 수정 시각
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # like, bookmark fields
    like_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='like_user_set', # post.like_user_set 으로 접근 가능
                                           through='Like')  
    bookmark_user_set = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                           blank=True,
                                           related_name='bookmark_user_set',# post.bookmark_user_set 으로 접근 가능
                                           through='Bookmark') # through : 중간 테이블 수동 지정
    
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.content
    
    @property
    def like_count(self):
        return self.like_user_set.count()
    
    @property
    def bookmark_count(self):
        return self.bookmark_user_set.count()
    

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # user, post는 유일해야함
        unique_together = (
            ('user', 'post')
        )
        
class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            ('user', 'post')
        )
        
        
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.content