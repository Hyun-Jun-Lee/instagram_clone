from django.urls import path
from post import views

app_name = 'post'

urlpatterns = [
    path('', views.post_list, name="post_list"),
    path('new/', views.post_new, name='post_new'),
    path('edit/<int:pk>/', views.post_edit, name='post_edit'),
    path('delete/<int:pk>/', views.post_delete, name='post_delete'),
    
]
