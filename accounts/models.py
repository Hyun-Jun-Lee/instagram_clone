from django.db import models
from django.conf import settings
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
# Create your models here.

# user가 업로드한 이미지 파일 경로 생헝하고 반환해주는 함수
def user_path(instance, filename):
    from random import choice
    import string
    # 8번 반복해서 문자 불러오기
    arr = [choice(string.ascii_letters) for _ in range(8)]
    pid = ''.join(arr)
    # 파일 확장면 분리해서 저장
    extension = filename.split('.')[-1]
    return 'accounts/{}/{}.{}'.format(instance.user.username, pid, extension)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField('별명', max_length=30, unique=True)
    # 간단한 자기소개 blank 가능
    info = models.CharField(max_length=200, blank=True)
    # 프로필 사진 / ProcessedImageField: 원본 이미지를 재가공하여 저장 (원본x, 썸네일o)
    picture = ProcessedImageField(upload_to=user_path,
                                processors=[ResizeToFill(150,150)], # 사이즈조절 imagekit
                                format='JPEG',
                                options={'quality': 90},
                                blank=True,
                                )
    # 성별 선택창 / 왼쪽이 DB에 저장되는 이름, 오른쪽이 user 보이는 이름
    GENDER_C = (
        ('선택안함', '선택안함'),
        ('여성', '여성'),
        ('남성', '남성'),
    )
    
    gender = models.CharField('성별(선택사항)',
                             max_length=10,
                             choices=GENDER_C,
                             default='N')
    
    def __str__(self):
        return self.nickname