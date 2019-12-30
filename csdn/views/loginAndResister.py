from csdn.models import Blog, User, CsdnUser, Comment, BlogSort
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib import auth
from csdn.views.blog import verify_is_null


def login(request):
    """
    登录
    :param request:
    :return:
    """
    try:
        username = request.POST.get('username')
        password = request.POST.get("password")
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            # return render(request, 'index.html')
            message = "登陆成功"
            result = True
        else:
            result = False
            message = "用户名或密码错误"
    except Exception as err:
        message = str(err)
        result = False
    return JsonResponse({'result': result, 'message': message})


def exit(request):
    """
    退出登录
    :param request:
    :return:
    """
    try:
        auth.logout(request)
        return JsonResponse({'message': " 退出成功"})
    except Exception as err:
        return JsonResponse({"message": "退出失败", 'err': str(err)})


def register(request):
    """
    注册用户
    :param request:
    :return:
    """
    try:
        username, password, email = [request.POST.get(key) for key in ("username", "password", "email")]
        if verify_is_null([username, password, email]):
            return JsonResponse({'result': False, 'message': "参数不能为空呦"})
        user = User.objects.filter(username=username)
        if user:  # 已经被注册了
            result = False
            message = "用户名已被注册"
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()

            csdnUser = CsdnUser(user=user)
            csdnUser.save()

            # 初始创建一个未分类的博客分类
            blogSort = BlogSort(csdnUser=csdnUser, name="默认分类")
            blogSort.save()
            message = "注册成功"
            result = True
    except Exception as err:
        result = False
        message = str(err)
    return JsonResponse({'result': result, 'message': message})
