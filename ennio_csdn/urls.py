"""ennio_csdn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from csdn.views import blog
from csdn.views import loginAndResister
from csdn.views import blog_manage

urlpatterns = [
    # 登录注册url
    path('admin/', admin.site.urls),
    path('login', LoginView.as_view(template_name="login.html")),
    path('exit', loginAndResister.exit),
    path('user/login', loginAndResister.login),
    path('user/register', loginAndResister.register),

    # 博客相关url
    path('', blog.index),       # 博客主界面
    path('write/blog', blog.write_blog),   # 写博客
    path('add/blog', blog.add_blog),       # 增加博客
    path('blog/details', blog.blog_details),   # 一篇博客的细节细节
    path('blog/index', blog.get_user_blogs),   # 某一个用户博客主界面
    path('blog/comment/add', blog.add_comment),       # 发布评论接口

    path('blog/like', blog.like),           # 点赞接口
    path('blog/unlike', blog.unlike),

    # 用户相关接口
    path('user/get/info', blog_manage.get_user_info),      # 用户主页的相关接口,ajax调用
    path('user/blog/manage', blog_manage.user_blog_manage),  # 用户博客管理主界面
    path('user/blog/sort/manage', blog_manage.user_blog_sort_manage),      # 用户博客分类管理
    path('user/blog/sort/add', blog_manage.user_blog_sort_add),            # 添加博客分类
    path('user/blog/delete', blog_manage.user_blog_delete),                # 删除博客
    path('user/blog/sort/delete', blog_manage.user_blog_sort_delete),      # 删除博客分类
    path('user/blog/change/index', blog_manage.user_change_blog_index),    # 修改博客入口
    path('user/blog/change', blog_manage.user_change_blog)                 # 修改博客操作
]
