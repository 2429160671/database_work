from django.shortcuts import render
from csdn.models import Blog, User, CsdnUser, Comment, BlogSort, Like_or_unlike
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q


# 用于判断是否参数是否为空的
def verify_is_null(params):
    for param in params:
        if param == "" or param == None:
            return True
    return False


def getCsdnUser(request):
    if request.user.is_authenticated:
        csdnUser = CsdnUser.objects.get(user=request.user)
    else:
        csdnUser = None
    return csdnUser


def index(request):
    """
    主页面，返回博客信息，同时根据搜索信息返回不同的信息
    并返回登录状态，前端根据是否登录显示不同的信息
    :param request:
    :return:
    """
    try:
        records_per_page = 5
        page = request.GET.get("page", "1")
        search = request.GET.get("search", "")
        if search == "":      #根据是否搜索返回不同的信息
            blogs = Blog.objects.all().order_by("-pub_time")
            paginator = Paginator(blogs, records_per_page)
            blogs = paginator.get_page(page)
        else:
            blogs = Blog.objects.filter(Q(title__icontains=search) | Q(content__icontains=search))
            paginator = Paginator(blogs, records_per_page)
            if paginator:
                blogs = paginator.get_page(page)
        result = True
        message = "成功"
    except Exception as err:
        result = False
        message = str(err)
        blogs = paginator = None
    return render(request, "index.html", {
        'blogs': blogs,
        'code': 0,
        "csdnUser": getCsdnUser(request),
        'page_range': paginator.page_range if paginator else 0,
        'page': int(page),
        'message': message,
        'result': result,
        'search': search
    })


def get_user_blogs(request):
    """
    某一个博主的主界面，返回两个用户，一个base.html使用,另一个user_blog_index使用
    :param request:
    :return:
    """
    try:
        page = request.GET.get("page", "1")
        records_per_page = 5
        username = request.GET.get("username")
        csdnUser = getCsdnUser(request)   # 当前登录用户,用户base.html使用

        # 哪一个用户博客主页，根据username进行区分，并获取其相关信息
        blog_csdnUser = CsdnUser.objects.get(user=User.objects.get(username=username))
        blogs = Blog.objects.filter(csdnUser=blog_csdnUser)
        blogs_sorts = BlogSort.objects.filter(csdnUser=blog_csdnUser)
        blogs_viewed_rank = Blog.objects.filter(csdnUser=blog_csdnUser).order_by("-viewed_number")[:5]
        blogs_liked_rank = Blog.objects.filter(csdnUser=blog_csdnUser).order_by("-liked_number")[:5]
        blogs_commented_rank = Blog.objects.filter(csdnUser=blog_csdnUser).order_by("-commented_number")[:5]

        # 分页
        paginator = Paginator(blogs, records_per_page)
        blogs = paginator.get_page(page)

        result = True
        message = "成功啦"
    except Exception as err:
        blog_csdnUser = csdnUser = blogs_commented_rank = blogs_liked_rank = blogs = paginator = blogs_sorts =blogs_viewed_rank= None
        message = str(err)
        result = False
        page = 1

    return render(request, "user_blog_index.html", {
        'result': result,
        'message': message,
        'csdnUser': csdnUser,
        'blogs': blogs,
        'blog_csdnUser': blog_csdnUser,
        'page': int(page),
        'page_range':  paginator.page_range if paginator!=None else 0,
        'blogs_sorts': blogs_sorts,
        'blogs_viewed_rank': blogs_viewed_rank,
        'blogs_liked_rank': blogs_liked_rank,
        'blogs_commented_rank': blogs_commented_rank
    })


@login_required
def write_blog(request):
    """
    写博客入口，判断是否登录了；返回当前用户的分类
    :param request:
    :return:
    """
    try:
        csdnUser = CsdnUser.objects.get(user=request.user)
        blogs_sorts = BlogSort.objects.filter(csdnUser=csdnUser)
        message = "ok"
    except Exception as err:
        message = str(err)
        csdnUser = None
        blogs_sorts = None
    return render(request, "write_blog.html", {
        'csdnUser': csdnUser,
        'blogs_sorts': blogs_sorts,
        'message': message
    })


@login_required
def add_blog(request):
    """
    添加一篇博客
    :param request:
    :return:
    """
    try:
        title = request.POST.get("title")
        content = request.POST.get("content")
        if verify_is_null([title, content]):
            return JsonResponse({'result': False, 'message': "输入不能为空"})
        blogSortName = request.POST.get("blogSort")
        csdnUser = CsdnUser.objects.get(user=request.user)

        blogSort = BlogSort.objects.get(csdnUser=csdnUser, name=blogSortName)
        blog = Blog.objects.create(csdnUser=csdnUser, title=title, content=content, blog_sort=blogSort)

        blogSort.blogs_number += 1    # 该分类下的文章数++
        blogSort.save()

        result = True
        message = "发表成功"
        id = blog.id
    except Exception as err:
        id = None
        result = False
        message = str(err)
    return JsonResponse({'message': message, 'result': result, 'id': id})


def blog_details(request):
    """
    一篇博客的细节页面，此处需要增加访问量；根据此博客信息查询和该博客相似的博客进行推荐；
    并获取访问量前五的文章
    :param request:
    :return:
    """
    try:
        # 博客，评论，直接返回blog，前端直接.出来
        # 两个用户，一个base.html渲染，另一个details页面渲染

        blog_id = request.GET.get("blog_id")
        blog = Blog.objects.get(id=blog_id)
        comments = Comment.objects.filter(blog_id=blog_id)
        blog_csdnUser = blog.csdnUser  # 这个是当前页面的用户
        blogs_sorts = BlogSort.objects.filter(csdnUser=blog.csdnUser)
        blogs_viewed_rank = Blog.objects.filter(csdnUser=blog_csdnUser).order_by("-viewed_number")[:5]
        blogs_liked_rank = Blog.objects.filter(csdnUser=blog_csdnUser).order_by("-liked_number")[:5]
        blogs_commented_rank = Blog.objects.filter(csdnUser=blog_csdnUser).order_by("-commented_number")[:5]

        # 只有别人访问才增加访问量
        if blog_csdnUser != getCsdnUser(request):
            blog_csdnUser.viewed_number += 1    # 对应的博主访问量
            blog_csdnUser.save()

            blog.viewed_number += 1        # 当前博客访问量++
            blog.save()
        result = True
    except Exception as err:
        blog = comments = blogs_liked_rank = blog_csdnUser =  blogs_commented_rank = blogs_sorts = blogs_viewed_rank = None
        result = str(err)
    return render(request, "blog_details.html", {
        'result': result,
        'blog': blog,
        'comments': comments,
        'csdnUser': getCsdnUser(request),
        'blog_csdnUser': blog_csdnUser,
        'blogs_sorts': blogs_sorts,
        'blogs_viewed_rank': blogs_viewed_rank,
        'blogs_liked_rank': blogs_liked_rank,
        'blogs_commented_rank': blogs_commented_rank
    })


def add_comment(request):
    """
    发表评论接口
    ajax请求，所以判断下是否登录了，不然无法正常跳转
    :param request:
    :return:
    """
    try:
        if getCsdnUser(request) == None:
            code = 2
            result = False
            message = "请先登录"
        else:
            content = request.POST.get('content')
            if verify_is_null([content]):
                return JsonResponse({'result': False, 'message': "评论不能为空", 'code': 1})

            blog_id = request.POST.get('blog_id')
            comment = Comment(blog_id=blog_id, content=content,
                              csdnUser=CsdnUser.objects.get(user=request.user))
            comment.save()
            blog = Blog.objects.get(id=blog_id)
            blog.commented_number += 1  # 博客评论数量++
            blog.save()

            csdnUser = blog.csdnUser
            csdnUser.commented_number += 1    # 博客作者评论数量++
            csdnUser.save()
            result = True
            message = "评论成功"
            code = 0
    except Exception as err:
        result = False
        message = "评论失败"+str(err)
        code = 1
    return JsonResponse({'result': result, 'message': message, 'code': code})


def like(request):
    """
    点赞，点赞记录不存在则点赞，存在则取消赞
    :param request:
    :return:
    """
    try:
        if getCsdnUser(request) == None:
            code = 2
            result = False
            message = "请先登录"
        else:
            blog_id = request.GET.get("blog_id")
            csdnUser = getCsdnUser(request)
            blog = Blog.objects.get(id=blog_id)
            like = Like_or_unlike.objects.filter(type=0, blog=blog, csdnUser=csdnUser)
            if like:
                # 取消赞
                like.delete()
                blog.liked_number -= 1  # 当前博客点赞数--
                blog.save()
                csdnUser = blog.csdnUser
                csdnUser.liked_number -= 1   # 文章作者赞数--
                csdnUser.save()
                message = "取消赞成功"
            else:  # 添加点赞记录
                like = Like_or_unlike(type=0, csdnUser=csdnUser, blog=blog)
                like.save()
                blog.liked_number += 1           # 当前博客赞数++
                blog.save()
                csdnUser = blog.csdnUser         # 文章作者赞数++
                csdnUser.liked_number += 1
                csdnUser.save()
                message = "点赞成功"
            result = True
            code = 0
    except Exception as err:
        result = False
        message = "点赞失败"+str(err)
        code = 1
    return JsonResponse({'result': result, 'message': message, 'code': code})


def unlike(request):
    """
    反对，逻辑同点赞
    :param request:
    :return:
    """
    try:
        if getCsdnUser(request) == None:
            code = 2
            result = False
            message = "请先登录"
        else:
            blog_id = request.GET.get("blog_id")
            csdnUser = getCsdnUser(request)
            blog = Blog.objects.get(id=blog_id)
            unlike = Like_or_unlike.objects.filter(type=1, blog=blog, csdnUser=csdnUser)
            if unlike:
                # 取消反对
                unlike.delete()
                blog.unliked_number -= 1  # 当前博客反对数--
                blog.save()
                message = "取消反对成功"
            else:  # 添加反对记录
                unlike = Like_or_unlike(csdnUser=csdnUser, blog=blog, type=1)
                unlike.save()
                blog.unliked_number += 1           # 当前博客反对数++
                blog.save()
                message = "反对成功"
            result = True
            code = 0
    except Exception as err:
        result = False
        message = "反对失败"+str(err)
        code = 1
    return JsonResponse({'result': result, 'message': message, 'code': code})

