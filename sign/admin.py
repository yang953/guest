from django.contrib import admin
from sign.models import Event,Guest
# Register your models here.
# 映射models中的数据到Django自带的admin后台

# 通知Admin管理工具为这些模块逐一提供界面
# admin.site.register(Event)
# admin.site.register(Guest)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id','name','status','address','start_time']
    search_fields = ['name'] # 搜索栏
    list_filter = ['status'] # 过滤器

class GusetAdmin(admin.ModelAdmin):
    list_display = ['realname','phone','email','sign','create_time','event']
    search_fields = ['realname','phone'] # 搜索栏
    list_filter = ['sign'] # 过滤器

admin.site.register(Event,EventAdmin) # 用EventAdmin选项注册Event模块
admin.site.register(Guest,GusetAdmin)