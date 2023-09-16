from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Topic, Message, User
from .form import RoomForm, UserForm, MyUserCreationForm
# Create your views here.
##注意，view在url.py这个文件中绑定事件和页面的。然后相当于init页面中一个构建生命周期，类似window.onload
# rooms = [
#     {'id':1,'name':'Lets learn python!'},
#     {'id':2,'name':'Design with me!'},
#     {'id':3,'name':'Frontend Developer'},
# ]
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except: 
            messages.error(request,'User does not exist!')

        user = authenticate(request, email=email,password=password)

        if user is not None:
            login(request,user) #自带的login方法
            return redirect('home')
        else:
            messages.error(request,'Email or password does not exist')

    context={'page':page}
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)  #设定表单提取为一个user
        if form.is_valid():
            user = form.save(commit=False)  #提取为user，但暂时不保存到数据库 commit = False
            user.username = user.username.lower()
            user.birth = form.cleaned_data['birth']
            user.save() #保存到数据库
            login(request,user) 
            return redirect('home')
        else:
            messages.error(request,'An error found during registration')

    context={'page':page,'form':form}
    return render(request,'base/login_register.html',context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''  #dj的三元运算（ternary operate）
    #先把所有room条件查询出来。
    rooms = Room.objects.filter(
                                Q(topic__name__icontains=q) | 
                                Q(name__icontains=q) |
                                Q(description__icontains=q))  ##topic__name等都是 框架自带的 __是点的意思，点出属性，icontains 支持模糊查询
                                                              ## 这样写支持多条件搜索,相当于sql查询了

    topics = Topic.objects.all()[0:5] #只要前5个
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) ##按这个msg属于哪个topic进行查询，__是点的意思
                                                                              ##相当于msg随着room类型变化的sql查询 



    context = {'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)  #to which page.

def room(request,pk):
    # #pick up a room by id
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    # context = {'room':room}
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(    ##使用Message model直接创建到数据库，不需要save，其实这里的模型就是service
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    

    context = {'room':room,'room_messages':room_messages,'participants':participants}
    return render(request,'base/room.html',context)  #to which page.

def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() ##找出属于这个user的room
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user':user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

@login_required(login_url='/login') #login need
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':  #Rest
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home')
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False) 
        #     room.host = request.user
        #     room.save()
        #     return redirect('home')
            
    context = {'form':form,'topics':topics}
    return render(request, 'base/room_form.html',context)  #to which page.


@login_required(login_url='/login')
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #prefill room,instance用来传递一个已经存在的对象实例给表单，以便在表单中编辑该对象的属性。通常，这在更新对象数据时非常有用。
    topics = Topic.objects.all()

    if request.user != room.host:   #动作身份认证
        return HttpResponse('You are not allowed here!!!')
    
    if request.method == 'POST':   #Rest
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # form = RoomForm(request.POST,instance=room) #request.post用来更新数据，instance=room用来展现数据，
        #                                             #这两个同时用的效果是将room给更新成post中的数据
        return redirect('home')
    
    context = {'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)  #to which page.

@login_required(login_url='/login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:   #动作身份认证
        return HttpResponse('You are not allowed here!!!')
    
    if request.method == 'POST':  #Rest
        room.delete()
        return redirect('home')
    
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='/login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:   #动作身份认证
        return HttpResponse('You are not allowed here!!!')
    
    if request.method == 'POST':  #Rest
        message.delete()
        return redirect('room',pk=message.room.id)
    
    return render(request,'base/delete.html',{'obj':message})


@login_required(login_url='/login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
        
    return render(request,'base/update-user.html',{'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q')!= None else ''  #dj的三元运算（ternary operate）

    topics = Topic.objects.filter(Q(name__icontains=q))
    return render(request,'base/topics.html',{'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request,'base/activity.html',{'room_messages':room_messages})