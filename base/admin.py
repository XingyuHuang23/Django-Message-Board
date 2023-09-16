from django.contrib import admin

# Register your models here.
from .models import Room, Topic, Message, User

#在控制面板上显示model属性
admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)