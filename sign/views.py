from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from sign.models import Event,Guest
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.shortcuts import render,get_object_or_404
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

@login_required
# 发布会管理
def event_manage(request):
    # 读取浏览器cookie,这里出现一直刷新浏览器获取不到cookies，需要重新登录
    # username = request.COOKIES.get('user')
    # username = request.session.get('user')
    # return render(request,"event_manage.html",{"user":username})
    event_list = Event.objects.all() # 查询所有发布会对象
    username = request.session.get('user','')
    return render(request,"event_manage.html",{"user":username,"events":event_list})

# 发布会名称搜索
@login_required
def search_name(request):
    username = request.session.get('user','')
    search_name = request.GET.get("name","")
    event_list = Event.objects.filter(name__contains=search_name)
    return render(request,"event_manage.html",{"user":username,"events":event_list})

# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user','')
    guest_list = Guest.objects.all()
    paginator = Paginator(guest_list,2) #将数据分2条数据一页
    page = request.GET.get('page') #通过git请求得到当前要显示第几页数据
    try:
        conracts = paginator.page(page) #获取第page数据，如果没有抛出PageNotAnInteger异常，超出范围则抛出EmptyPage异常
    except PageNotAnInteger:
        conracts = paginator.page(1) #如果page不是整数，取第一页数据
    except EmptyPage:
        conracts = paginator.page(paginator.num_pages) #如果page不在范围，取最后一页
    return render(request,"guest_manage.html",{"user":username,"guests":conracts})

# 嘉宾名称搜索
@login_required
def search_realname(request):
    username = request.session.get('user', '')
    search_realname= request.GET.get("realname","")
    guest_list = Guest.objects.filter(realname__contains=search_realname)
    return render(request,"guest_manage.html",{"user":username,
                                               "guests":guest_list})

# 嘉宾手机号搜索
@login_required
def search_phone(request):
    username = request.session.get("user",'')
    search_phone =request.GET.get("phone","")
    search_name_bytes = search_phone.encode(encoding="utf-8")
    guest_list = Guest.objects.filter(phone__contains=search_name_bytes)

    paginator = Paginator(guest_list,10)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    return render(request,"guest_manage.html",{"user":username,
                                               "guests":contacts,
                                               "phone":search_phone})

# 签到页面
@login_required
def sign_index(request,eid):
    event = get_object_or_404(Event,id=eid)
    # get_object_or_404()默认调用Django的table.objects.get()方法，如果查询对象不存在，则抛出一个http404异常
    return render(request,"sign_index.html",{"event":event})

# 签到动作
@login_required
def sign_index_action(requst,eid):
    event = get_object_or_404(Event,id=eid)
    phone = requst.POST.get('phone')
    print(phone)
    result = Guest.objects.filter(phone=phone) # 查询手机号在guest表是否存在
    if not result:
        return render(requst,'sign_index.html',{'event':event,'hint':'phone error'}) # 如果为空则提示用户手机号码错误
    result = Guest.objects.filter(phone=phone,event_id=eid) # 通过手机和发布会id来查询Guest表
    if not result:
        return render(requst,'sign_index.html',{'evevt':event,'hint':'event id or phone error.'}) # 如果为空则提示手机或发布会错误
    result = Guest.objects.get(phone=phone,event_id=eid)
    if result.sign:
        return render(requst,'sign_index.html',{'event':event,'hint':"user has sign in."}) # 如果客户已经签到过则提示已经签到
    else:
        Guest.objects.filter(phone=phone,event_id=eid).update(sign='1')
        return render(requst,'sign_index.html',{'event':event,'hint':'sign in success!','guest':result}) # 客户未签到则更新数据库并提示成功

# 退出登录
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response