#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Author:袁麻麻
Data：2019/05/05
Describe: web接口编写
'''
from django.http import JsonResponse
from sign.models import Event,Guest
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.db.utils import IntegrityError
import time
from  django.views.decorators.csrf import csrf_exempt
import ast
# 添加发布会接口
@csrf_exempt
def add_event(request):
    # 通过post请求接收发布会参数eid,name,limit,status,address,start_time
    eid = request.POST.get('eid','')                   # 发布会id
    name = request.POST.get('name','')                 # 发布会标题
    limit = request.POST.get('limit','')               # 限制人数
    status = request.POST.get('status','')             # 状态
    address = request.POST.get('address','')           # 地址
    start_time = request.POST.get('start_time','')     # 发布会时间

    # 判断传递的各值均不能为空，否则返回相应的字段
    if eid == ''or name == ''or limit==''or address==''or start_time=='':
        return JsonResponse({'status':10021,'message':'paramter error'})  # JsonResponse方法将字典转换成字符串返回给客户端

    # 分别判断eid，name是否存在，如果存在说明数据重复，返回对应的状态码和提示信息
    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status':10022,'message':'event id already exists'})

    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status':10023,'message':'event name already exists'})

    # 发布会不是必传字段，判断为空则设置为1，开启状态
    if status == '':
        status=1

    # 尝试将数据插入event表，如果日期格式报错则抛出对应异常信息，否则提示状态码和成功信息
    try:
        Event.objects.create(id=eid,name=name,limit=limit,address=address,status=int(status),start_time=start_time)
    except ValidationError as e:
        error = 'start_time format error.It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status':10024,'message':error})
    return JsonResponse({'status':200,'message':'add event success'})

@csrf_exempt
# 查询发布会接口
def get_event_list(request):
    # 通过get请求接收发布会eid，和名称
    eid = request.GET.get("eid",'') # 发布会ID
    name = request.GET.get("name",'') # 发布会名称
    # eid和name不能都为空，否则返回错误信息
    if eid == ''and name == '':
        return JsonResponse({'status':10021,'message':'parameter error'})
    # 如果eid不为空，则优先以eid查询，如果查询到结果以字典的形式存放到定义的event中，并将event作为接口返回字典中data对应的值
    if eid !='':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022,'message':'query result is empty'})
        else:
            event['eid'] = result.id
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status':200,'message':'success','data':event},safe=False,json_dumps_params={'ensure_ascii':False})
    # 发布会名称为模糊查询，可能存在多条结果，先将每条数据存放到event中，再把每条event字典放到datas数组中，最后将Datas数组作为接口返回字典中data对应值
    if name !='':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status':200,'message':'success','data':datas},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})

@csrf_exempt
# 添加嘉宾接口
def add_guest(request):
    # 通过post请求接收嘉宾参数：eid,realname,phone,email
    eid = request.POST.get('eid','') # 关联发布会id
    realname = request.POST.get('realname','') # 姓名
    phone = request.POST.get('phone','') # 手机号
    email = request.POST.get('email','') # 邮箱

    # 判断eid，realname，phone，等参数均不能为空
    if eid==''or realname==''or phone =='':
        return JsonResponse({'status':10021,'message':'parameter error'})

    # 判断嘉宾关联的发布会ID是否存在，以及发布会状态是否为True。如果不为True，则说明当前为关闭状态，返回相应的状态码和提示信息
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status':10022,'message':'event id null'})
    # 判断状态是否为True
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status':10023,'message':'event status is not available'})
    # 判断发布会已添加的人数是否大于限制人数，如果大于报错
    event_limit = Event.objects.get(id=eid).limit # 发布会限制人数
    guest_limit = Guest.objects.filter(event_id=eid) # 发布会已添加的嘉宾数
    if len(guest_limit)>= event_limit:
        return JsonResponse({'status':10024,'message':'event number is full'})
    # 判断当前时间是否大于发布会时间，如果大于则返回错误信息
    event_time = Event.objects.get(id=eid).start_time # 发布会时间
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime,"%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))

    now_time = str(time.time()) # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)
    if n_time>=e_time:
        return JsonResponse({'status':10025,'message':'event has started'})
    # 插入嘉宾数据，如果手机号已存在，则抛出异常。如果成功则提示成功
    try:
        Guest.objects.create(realname=realname,phone=int(phone),email=email,sign=0,event_id=int(eid))
    except IntegrityError:
        return JsonResponse({'status':10026,'message':'the event guest phone number repeat'})
    return JsonResponse({'status':200,'message':'add guest success'})

@csrf_exempt
# 查询嘉宾接口
def get_guest_list(request):
    # 通过get请求查询发布会id和手机号
    eid = request.GET.get("eid",'') # 关联发布会id
    phone =request.GET.get("phone",'') # 嘉宾手机号
    # 判断关联发布会是否为空
    if eid =='':
        return JsonResponse({'status':10021,'message':'eid cannot be empty'})
    # 判断如果发布会id不为空，手机号为空，将发布会id关联的数据都取出
    if eid !='' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                datas.append(guest)
            return JsonResponse({'status':200,'message':'success','data':datas},safe=False,json_dumps_params={'ensure_ascii':False})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})
    # 如果关联发布会id和手机号都不为空
    if eid !='' and phone !='':
        guest = {}
        try:
            # 匹配对应数据
            result = Guest.objects.get(phone=phone,event_id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022,'message':'query result is empty'})
        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status':200,'message':'success','data':guest},safe=False,json_dumps_params={'ensure_ascii':False})

@csrf_exempt
# 发布会签到接口
def user_sign(request):
    eid = request.POST.get('eid','') # 发布会id
    phone = request.POST.get('phone','') # 嘉宾手机号
    # 判断发布会id和手机号是否为空
    if eid==''or phone == '':
        return JsonResponse({'status':10021,'message':'parameter error'})
    # 判断发布会id是否存在，
    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status':10022,'message':'event id null'})
    # 再判断状态是否是True，不为True则说明发布会未开启
    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status':10023,'message':'event status is not available'})
    event_time = Event.objects.get(id=eid).start_time # 发布会时间
    etime = str(event_time).split(".")[0]
    timeArray = time.strptime(etime,"%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))
    now_time = str(time.time()) # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)
    # 判断当前时间是否大于发布会时间
    if n_time>=e_time:
        return JsonResponse({'status':10024,'message':'event has started'})
    # 判断嘉宾手机号是否存在
    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status':10025,'message':'user phone null'})
    # 判断发布会id和手机号是否是绑定关系
    result = Guest.objects.filter(event_id=eid,phone=phone)
    if not result:
        return JsonResponse({'status':10026,'message':'user did not participate in the conference'})
    # 判断嘉宾是否是签到状态
    result = Guest.objects.get(event_id=eid,phone=phone).sign
    if result:
        return JsonResponse({'status':10027,'message':'user has sign in'})
    else:
        Guest.objects.filter(event_id=eid,phone=phone).update(sign='1')
        return JsonResponse({'status':200,'message':'sign success'})
