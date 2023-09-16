from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm
from django import forms

#基于框架form创建自定义表单
class MyUserCreationForm(UserCreationForm):
    birth = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = User  #按User中的属性进行自定义提取 ，也可以加上UserCreationForm自带的属性，比如pwd1，pwd2
        fields = ['name','username','email','password1','password2','birth']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host','participants']  #排除不想要的表格字段

class UserForm(ModelForm):
     class Meta:
         model = User
         fields = ['avatar','name','username','email','bio','birth']  #表单展示多个属性