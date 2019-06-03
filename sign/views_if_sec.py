#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
Author:袁麻麻
Data：2019/05/05
Describe: auth安全接口
'''

from django.contrib import auth as django_auth
import base64
from django.http import JsonResponse
from sign.models import Event,Guest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import json
import time,hashlib
from django.views.decorators.csrf import csrf_exempt

# 用户认证
def user_auth(request):
    get_http_auth = request.META.get('HTTP_AUTHORIZATION',b'')
    # request.META是一个python字典，包含了本次http请求的header信息，例如用户认证、ip地址和用户agent，HTTP_AUTHORIZATION用于获取http认证数据。如果为空，将得到一个空的bytes对象
    auth = get_http_auth.split() # 利用split方法拆分成list
    try:
        auth_parts = base64.b64decode(auth[1]).decode('utf-8').partition(';')
        # 通过decode方法以utf-8编码对字符串解码，partition()对字符串分隔

    except IndexError:
        return "null"
    username,password = auth_parts[0],auth_parts[2] # 切片取出最终数据
    user = django_auth.authenticate(username = username,password = password)
    if user is not None:
        django_auth.login(request,user)
        return "success"
    else:
        return "fail"

def get_event_list(request):
    auth_result = user_auth(request) # 调用认证函数
    if auth_result == "null":
        return JsonResponse({'status':10011,'message':'user auth null'})
    if auth_result == "fail":
        return JsonResponse({'status':10012,'message':'user auth fail'})
    eid = request.GET.get("eid","") # 发布会id
    name = request.GET.get("name","") # 发布会名称

    if eid == '' and name == '':
        return JsonResponse({'status':10021,'message':'parameter error'})

    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022, 'message':'query result is empty'})
        else:
            event['eid'] = result.id
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status':200, 'message':'success', 'data':event})

    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['eid'] = r.id
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status':200, 'message':'success', 'data':datas})
        else:
            return JsonResponse({'status':10022, 'message':'query result is empty'})


# 用户签名+时间戳
def user_sign(request):
    if request.method == 'POST':
        client_time = request.POST.get('time','') # 客户端时间戳
        client_sign = request.POST.get('sign','') # 客户端签名
    else:
        return "error"
    if client_time == '' or client_sign == '':
        return "sign null"

    # 服务器时间
    now_time = time.time()
    server_time = str(now_time).split('.')[0] # 将时间戳转换成字符串，并截取小数点前的时间
    #获取时间差
    time_difference = int(server_time)-int(client_time)
    if time_difference >= 60:
        return "timeout"

    # 签名检查
    md5 = hashlib.md5()
    sign_str = client_time + "$Guest-Bugmaster" # 时间戳加秘钥
    sign_bytes_utf8 = sign_str.encode(encoding="utf-8")
    md5.update(sign_bytes_utf8)
    server_sign = md5.hexdigest()
    if server_sign != client_sign:
        return "sign fail"
    else:
        return "sign success"

# 添加发布会接口--增加签名+时间戳
@csrf_exempt
def add_event(request):
    sign_result = user_sign(request)
    if sign_result == 'error':
        return JsonResponse({'status':10011,'message':'request error'})
    elif sign_result == "sign null":
        return JsonResponse({'status':10012,'message':'user sign null'})
    elif sign_result == "timeout":
        return JsonResponse({'status':10013,'message':'user sign timeout'})
    elif sign_result == "sign fail":
        return JsonResponse({'status':10014,'message':'user sign error'})

    eid = request.POST.get('eid', '')  # 发布会id
    name = request.POST.get('name', '')  # 发布会标题
    limit = request.POST.get('limit', '')  # 限制人数
    status = request.POST.get('status', '')  # 状态
    address = request.POST.get('address', '')  # 地址
    start_time = request.POST.get('start_time', '')  # 发布会时间

    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status': 10021, 'message': 'parameter error'})

    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status': 10022, 'message': 'event id already exists'})

    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status': 10023, 'message': 'event name already exists'})

    if status == '':
        status = 1

    try:
        Event.objects.create(id=eid, name=name, limit=limit, address=address, status=int(status), start_time=start_time)
    except ValidationError:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 10024, 'message': error})

    return JsonResponse({'status': 200, 'message': 'add event success'})





