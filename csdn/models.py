from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField
import datetime
# Create your models here.


class CsdnUser(models.Model):
    """
    用户
    """
    user = models.OneToOneField(User, models.CASCADE)
    motto = models.CharField(verbose_name="座右铭", max_length=200, null=True, blank=True, default="")
    pic = models.CharField(verbose_name="头像", max_length=50, null=True, blank=True, default="")
    liked_number = models.IntegerField(verbose_name="获赞数", default=0)
    commented_number = models.IntegerField(verbose_name="被评论数", default=0)
    viewed_number = models.IntegerField(verbose_name="被浏览量", default=0)
    followed_number = models.IntegerField(verbose_name="被关注数", default=0)


class BlogSort(models.Model):
    """
    博客分类表
    """
    name = models.CharField(max_length=30, verbose_name="分类名称", null=False, blank=False)
    intro = models.TextField(verbose_name="分类简介", default="")
    csdnUser = models.ForeignKey(CsdnUser, models.CASCADE)
    blogs_number = models.IntegerField(verbose_name="当前分类之下的博客数量", default=0)
    create_time = models.DateTimeField(auto_now_add=True, null=True)


class Blog(models.Model):
    """
    一篇博客
    """
    title = models.CharField(max_length=40, verbose_name="标题")
    content = HTMLField(verbose_name="博客内容")
    liked_number = models.IntegerField(verbose_name="点赞量", default=0)
    unliked_number = models.IntegerField(verbose_name="踩的数量", default=0)
    viewed_number = models.IntegerField(verbose_name="浏览量", default=0)
    commented_number = models.IntegerField(verbose_name="评论数量", default=0)
    csdnUser = models.ForeignKey(CsdnUser, models.CASCADE)
    pub_time = models.DateTimeField(auto_now_add=True)
    blog_sort = models.ForeignKey(BlogSort, on_delete=models.SET_NULL, null=True, blank=True)  # 不级联删除，分类删除了，文章并不删除
    index_sort = models.CharField(max_length=40, verbose_name="首页分类", default="其他")

    class Meta:
        ordering = ["viewed_number"]


class Comment(models.Model):
    """
    评论表
    """
    blog = models.ForeignKey(Blog, models.CASCADE)
    csdnUser = models.ForeignKey(CsdnUser, models.CASCADE)
    content = models.TextField(verbose_name="评论内容")
    comment_time = models.DateTimeField(auto_now_add=True)


class Like_or_unlike(models.Model):
    """
    点赞/反对表,人和文章点赞/反对关系，对多对
    """
    type = models.IntegerField(default=0, verbose_name="点赞还是反对")
    blog = models.ForeignKey(Blog, models.CASCADE)
    csdnUser = models.ForeignKey(CsdnUser, models.CASCADE)
    like_time = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    """
    关注表,csdnUser和csdnUser之间，多对多关系
    """
    csdnUser_follow_id = models.IntegerField(verbose_name="关注者的id")
    csdnUser_followed_id = models.IntegerField()
    follow_time = models.DateTimeField(auto_now_add=True)
