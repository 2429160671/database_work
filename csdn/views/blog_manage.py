from django.shortcuts import render
from csdn.models import Blog, User, CsdnUser, Comment, BlogSort, Like_or_unlike
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from csdn.views.blog import getCsdnUser, verify_is_null


def get_user_info(request):
    """
    获取用户总的访问量，点赞量等信息的接口，
    根据用户名获取，唯一的,base_details处使用，改变left之中的信息
    :param request:
    :return:
    """
    try:
        username = request.GET.get("username")
        csdnUser = CsdnUser.objects.get(user=User.objects.get(username=username))
        result = True
        message = "1"
    except Exception as err:
        result = False
        message = str(err)
        csdnUser = None
    return JsonResponse({
        'result': result,
        'message': message,
        'liked_number': csdnUser.liked_number,
        'viewed_number': csdnUser.viewed_number,
        'followed_number': csdnUser.followed_number,
        'commented_number': csdnUser.commented_number
    })


@login_required
def user_blog_manage(request):
    """
    当前用户的博客管理，默认是进入文章管理
    :param request:
    :return:
    """
    try:
        csdnUser = CsdnUser.objects.get(user=request.user)
        page = request.GET.get("page", "1")
        records_per_page = 5
        blogs = Blog.objects.filter(csdnUser=csdnUser)
        paginator = Paginator(blogs, records_per_page)
        blogs = paginator.get_page(page)
        result = True
        message = "获取文章成功啦"
    except Exception as err:
        blogs = csdnUser = page = paginator = None
        result = False
        message = str(err)

    return render(request, "blog_manage.html", {
        'result': result,
        'message': message,
        'blogs': blogs,
        'csdnUser': csdnUser,
        'page_range': paginator.page_range,
        'page': int(page)
    })


def user_blog_sort_manage(request):
    """
    用户的博客分类管理， 不分页，全部返回直接
    :param request:
    :return:
    """
    try:
        csdnUser = getCsdnUser(request)
        blog_sorts = BlogSort.objects.filter(csdnUser=csdnUser)
        result = True
        message = '成功'
    except Exception as err:
        result = False
        message = str(err)
        csdnUser = blog_sorts = None
    return render(request, "blog_manage_sort.html", {
        'result': result,
        'message': message,
        'blog_sorts': blog_sorts,
        'csdnUser': csdnUser
    })


@login_required
def user_blog_delete(request):
    """
    删除博客
    :param request:
    :return:
    """
    try:
        blog_id = request.POST.get("blog_id")
        Blog.objects.get(id=blog_id).delete()
        result = True
        message = "删除成功"
    except Exception as err:
        result = False
        message = "删除失败"+str(err)
    return JsonResponse({
        'result': result,
        'message': message,
    })


@login_required
def user_change_blog_index(request):
    """
    修改博客信息入口，获取已有博客信息，前端进行渲染
    :param request:
    :return:
    """
    try:
        blog_id = request.GET.get("blog_id")
        csdnUser = getCsdnUser(request)
        blog = Blog.objects.get(id=blog_id)
        message = "成功"
        result = True
    except Exception as err:
        message = str(err)
        blog = csdnUser = None
        result = False
    return render(request, "blog_manage_change.html", {
        'message': message,
        'csdnUser': csdnUser,
        'blog': blog,
        'result': result
    })


def user_change_blog(request):
    """
    修改博客信息，
    :param reqeust:
    :return:
    """
    try:
        blog_id = request.POST.get("blog_id")
        blog = Blog.objects.get(id=blog_id)
        blog.title = request.POST.get("title")
        blog.content = request.POST.get("content")
        csdnUser = getCsdnUser(request)
        blog_sort_now = BlogSort.objects.get(csdnUser=csdnUser, name=request.POST.get("blog_sort"))
        blog_sort_ever = blog.blog_sort
        # 判断分类是否改变了，改变了需要更改相应分类下文章的数目
        if blog_sort_now != blog_sort_ever:
            blog_sort_now.blogs_number += 1
            blog_sort_ever.blogs_number -= 1
            blog.blog_sort = blog_sort_now
            blog_sort_now.save()
            blog_sort_ever.save()
        blog.save()
        message = "修改成功"
        result = True
    except Exception as err:
        result = False
        message = "修改失败" + str(err)

    return JsonResponse({
        'message': message,
        'result': result
    })


@login_required
def user_blog_sort_add(request):
    """
    添加一个分类的接口
    :param request:
    :return:
    """
    try:
        sort_name = request.POST.get("sort_name")
        sort_intro = request.POST.get("sort_intro")
        if verify_is_null([sort_name,sort_intro]):
            return JsonResponse({'result': False, 'message': "参数不能为空"})
        csdnUser = CsdnUser.objects.get(id=request.POST.get("csdnUser_id"))
        if BlogSort.objects.filter(csdnUser=csdnUser, name=sort_name):
            return JsonResponse({'result': False, 'message': "不可创建同名分类"})
        else:
            BlogSort.objects.create(csdnUser=csdnUser, name=sort_name, intro=sort_intro)
            message = "添加成功"
        result = True
    except Exception as err:
        result = False
        message = "添加失败"+str(err)
    return JsonResponse({
        'result': result,
        'message': message,
    })


def user_blog_sort_delete(request):
    """
    删除分类
    :param request:
    :return:
    """
    try:
        sort_id = request.POST.get("sort_id")
        BlogSort.objects.get(id=sort_id, csdnUser=getCsdnUser(request)).delete()
        message = "删除成功"
        result = True
    except Exception as err:
        result = False
        message = "添加失败"+str(err)
    return JsonResponse({
        'result': result,
        'message': message
    })
