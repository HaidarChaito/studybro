from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Message, Room, Topic, User
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

# Create your views here.


def loginView(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username,
                            password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Wrong username or password')

    return render(request, 'base/auth.html', {'page': 'login'})


def logoutView(request):
    logout(request)
    return redirect('home')


def registerView(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        try:
            user = User.objects.create(
                username=request.POST.get('username').lower(),
                password=request.POST.get('password')
            )
            user.set_password(request.POST.get('password'))
            user.save()
            login(request, user)
            return redirect('home')
        except:
            messages.error(request, 'Error registering the user')
            return redirect('home')
    return render(request, 'base/auth.html')


def home(request):
    q = request.GET.get('q')
    if q != None:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
        room_msgs = Message.objects.filter(Q(room__topic__name__icontains=q))
    else:
        rooms = Room.objects.all()
        room_msgs = Message.objects.all()[0:10]
    rooms_count = rooms.count()

    topics = Topic.objects.all()[0:5]
    topics_count = []
    total_count = 0
    for topic in topics:
        count = Room.objects.filter(topic=topic).count()
        topics_count.append(count)
        total_count += count
    members_count = []
    for room in rooms:
        members_count.append(room.members.count())
    rooms_zip = zip(rooms, members_count)
    topics_zip = zip(topics, topics_count)
    return render(request, 'base/home.html', {'rooms_zip': rooms_zip,
                                              'rooms_count': rooms_count,
                                              'room_msgs': room_msgs, 'topics_zip': topics_zip, 'total_count': total_count, 'page': 'home'})


def room(request, id):
    room = Room.objects.get(id=id)
    roomMessages = room.message_set.all()
    members = room.members.all()

    if request.method == 'POST':
        body: str = request.POST.get('body')
        if body.strip() == '' or body == None:
            messages.error(request, 'Message cannot be empty')
        else:
            message = Message.objects.create(
                user=request.user,
                room=room,
                body=body
            )
            room.members.add(request.user)
        return redirect('room', id=room.id)
    return render(request, 'base/room.html', {'room': room, 'msgs': roomMessages, 'members': members})


def userProfile(request, id):
    user = User.objects.get(id=id)

    q = request.GET.get('q')
    if q != None:
        rooms = user.room_set.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
        room_msgs = user.message_set.filter(Q(room__topic__name__icontains=q))
    else:
        rooms = user.room_set.all()
        room_msgs = user.message_set.all()

    topics = Topic.objects.all()[0:10]
    topics_count = []
    total_count = 0
    for topic in topics:
        count = rooms.filter(topic=topic).count()
        topics_count.append(count)
        total_count += count
    topics_zip = zip(topics, topics_count)
    members_count = []
    for room in rooms:
        members_count.append(room.members.count())
    rooms_zip = zip(rooms, members_count)
    rooms_count = 0
    for room in rooms:
        rooms_count += 1
    return render(request, 'base/profile.html', {'rooms_count': rooms_count, 'user': user, 'rooms_zip': rooms_zip, 'topics_zip': topics_zip, 'total_count': total_count, 'room_msgs': room_msgs, 'page': 'profile'})


def topicView(request):
    q = request.GET.get('q')
    if q != None:
        topics = Topic.objects.filter(name__icontains=q)
    else:
        topics = Topic.objects.all()
    topics_count = []
    total_count = 0
    for topic in topics:
        count = Room.objects.filter(topic=topic).count()
        topics_count.append(count)
        total_count += count
    topics_zip = zip(topics, topics_count)
    return render(request, 'base/topics.html', {'topics_zip': topics_zip})


def activityView(request):
    room_msgs = Message.objects.all()[0:10]
    return render(request, 'base/activity.html', {'room_msgs': room_msgs})


@login_required(login_url='login')
def createRoom(request):
    topics = Topic.objects.all()
    form = RoomForm()
    if request.method == 'POST':
        topic, created = Topic.objects.get_or_create(
            name=request.POST.get('topic'))
        room = Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        room.members.add(request.user)

        return redirect('home')
    return render(request, 'base/room_form.html', {'form': form, 'topics': topics})


@login_required(login_url='login')
def updateRoom(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('Authentication error')
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'base/room_form.html', {'form': form})


@login_required(login_url='login')
def deleteRoom(request, id):
    room = Room.objects.get(id=id)
    if request.user != room.host:
        return HttpResponse('Authentication error')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMsg(request, id):
    msg = Message.objects.get(id=id)
    if request.user != msg.user:
        return HttpResponse('Authentication error')
    if request.method == 'POST':
        msg.delete()
        return redirect('room', id=msg.room.id)
    return render(request, 'base/delete.html', {'obj': msg})


@login_required(login_url='login')
def userSettings(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if form.cleaned_data['username'] is not None:
                user.username = form.cleaned_data['username']
            if form.cleaned_data['about'] is not None:
                user.about = form.cleaned_data['about']
            if form.cleaned_data['avatar'] is not None:
                user.avatar = form.cleaned_data['avatar']
            p1 = form.cleaned_data['password1']
            p2 = form.cleaned_data['password2']
            if p1 is not None and p2 is not None and (p1 == p2) and p1 != "" and (p1.strip() != ""):
                user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect('user-profile', id=user.id)

    return render(request, 'base/settings.html', {'form': form})
