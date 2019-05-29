from django.db import models

# Create your models here.
# 发布会表
class Event(models.Model):
    name = models.CharField(max_length=20) # 发布会标题
    limit = models.IntegerField() # 参加人数
    status = models.BooleanField() # 状态
    address = models.CharField(max_length=200) # 地址
    start_time = models.DateTimeField('events time') # 发布会时间
    create_time = models.DateTimeField(auto_now=True) # 创建时间（自动获取当前时间）

    def __str__(self):
        return self.name

# 嘉宾表
class Guest(models.Model):
    event = models.ForeignKey(Event) # 关联发布会ID
    realname = models.CharField(max_length=64) # 姓名
    phone = models.CharField(max_length=16) # 手机号
    email = models.EmailField() # 邮箱
    sign = models.BooleanField() # 签到状态
    create_time = models.DateTimeField(auto_now=True) # 创建时间（获取当前时间）

# Meta是Django模型类的内部类，用于定义一些Django模型类的行为特征
class Meta:
    unique_together = ('event','phone') # 设置两个字段为联合主键

# __str__()方法告诉python如何将对象以str的方式显示出来
def __str__(self):
    return self.name