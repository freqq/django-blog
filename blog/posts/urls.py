from django.urls import path
from django.contrib import admin
from .views import (
    post_create,
    post_delete,
    post_detail,
    post_update,
    posts_list
) 

urlpatterns = [
    path('<int:id>/edit/', post_update, name='update'),
    path('', posts_list, name='list'),
    path('create/', post_create),
    path('<int:id>/delete/', post_delete, name='delete'),
    path('<int:id>/', post_detail, name='detail'),
]