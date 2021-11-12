# Generated by Django 3.2.9 on 2021-11-12 14:27

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(max_length=30, unique=True, verbose_name='별명')),
                ('info', models.CharField(blank=True, max_length=200)),
                ('picture', imagekit.models.fields.ProcessedImageField(blank=True, upload_to=accounts.models.user_path)),
                ('gender', models.CharField(choices=[('선택안함', '선택안함'), ('여성', '여성'), ('남성', '남성')], default='N', max_length=10, verbose_name='성별(선택사항)')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
