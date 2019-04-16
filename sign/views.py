from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
# Create your views here.

def index(request):
    return render(request,"index.html")

# 登录动作
def login_action(request):
    # 获取客户端的请求方式并判断
    if request.method == 'POST':
        # 获取账户名和密码
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username,password=password)
        if user is not None:
        #if username=='admin' and password=='admin123':
            # 验证成功显示结果成功
            # return HttpResponse('login success!')
            auth.login(request,user)
            # HttpResponseRedirect类可以重新对路径定向，将请求成功后转向指向/event_manage/目录
            response = HttpResponseRedirect('/event_manage/')
            # 添加浏览器cookie
            # response.set_cookie('user',username,3600)
            request.session['user']=username # 将session信息记录到浏览器
            return response
        else:
            # 验证失败通过render返回index.html页面
            return render(request,'index.html',{'error':'username or password error!'})

@login_required()
# 发布会管理
def event_manage(request):
    # 读取浏览器cookie,这里出现一直刷新浏览器获取不到cookies，需要重新登录
    # username = request.COOKIES.get('user')
    username = request.session.get('user')
    return render(request,"event_manage.html",{"user":username})