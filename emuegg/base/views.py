from calendar import c
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import User, Channel, Message, Topic
from .forms import UserForm, CustomeUserCreationForm, RoomForm, CountryForm 
import folium
import geocoder

def loginView(req):
    page = 'login'
    if req.user.is_authenticated:
        return redirect('home')
    if req.method == 'POST':
        email = req.POST.get('email')
        password = req.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(req, 'Invalid email address')
        user = authenticate(req, email=email, password=password)
        if user is not None:
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, 'Invalid email address or password')

    data = {'page' : page}
    return render(req, 'base/login.html', data)

def logoutView(req):
    logout(req)
    return redirect('home')

def signup(req): 
    form = CustomeUserCreationForm()
    if req.method == 'POST':
        form = CustomeUserCreationForm(req.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, 'An error occurred. Please try again.')
    return render(req, 'base/login.html', {'form' : form})
    
def home(req):
    query = req.GET.get('query') if req.GET.get('query') else ''
    channels = Channel.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
        )
    channel_count = channels.count()
    topics = Topic.objects.all()
    channel_messages = Message.objects.all().order_by('-created')
    data = {'channels' : channels,
     'topics' : topics,
      'channel_count' : channel_count,
        'channel_messages' : channel_messages
      }
    return render(req, 'base/home.html', data)

def profile(req, id):
    user = User.objects.get(id=id)
    channels = user.channel_set.all()
    messages = user.message_set.all()
    data = {'user' : user, 'channels' : channels, 'messages' : messages}
    return render(req, 'base/profile.html', data)

@login_required(login_url='login')
def updateProfile(req):
    user = req.user
    form = UserForm(instance=user)
    if req.method == 'POST':
        form = UserForm(req.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', id=user.id)
    
    return render(req, 'base/updateProfile.html', {'form' : form})

def channel(req, id):
    channel = Channel.objects.get(id=id)
    posts = channel.message_set.all().order_by('-created')
    participants = channel.participants.all()
    if req.method == 'POST':
        posts = Message.objects.create(
            user=req.user,
            channel=channel,
            message=req.POST.get('message')
            )
        channel.participants.add(req.user)
        return redirect('channel', id=channel.id)
        
    data = {'channel' : channel, 'posts' : posts, 'participants' : participants}
    return render(req, 'base/channel.html', data)

def map(req):
    form = CountryForm()
    users = User.objects.all()
    
    location = geocoder.osm(users.country_set.all())
    lat = location.latlng[0]
    lng = location.latlng[1]
    if req.method == 'POST':
        form = CountryForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('map')
    m = folium.Map(location=[-27.4973, 153.0134], zoom_start=4)
    folium.Marker([lat, lng], popup='<strong>Brisbane</strong>', tooltip="Click for more information").add_to(m)
    m = m._repr_html_()
    data = {'m' : m, 'form' : form}
    return render(req, 'base/map.html', data)
    

@login_required(login_url='login')
def createChannel(req):
    if req.method == 'POST':
        form = RoomForm(req.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Channel has been created successfully')
    data = {'form' : RoomForm()}
    return render(req, 'base/channel_form.html', data)

@login_required(login_url='login')
def updateChannel(req, id):
    channel = Channel.objects.get(id=id)
    if req.user != channel.host:
        return HttpResponse('You are not allowed to update this channel')
    if req.method == 'POST':
        form = RoomForm(req.POST, instance=channel)
        if form.is_valid():
            form.save()
            return redirect('home')
    channel = Channel.objects.get(id=id)
    return render(req, 'base/channel_form.html', {'form' : RoomForm(instance=channel)})

@login_required(login_url='login')
def deleteChannel(req, id):
    channel = Channel.objects.get(id=id)
    if req.user != channel.host:
        return HttpResponse('You are not allowed to update this channel')
    if req.method == 'POST':
        channel.delete()
        return redirect('home')
    return render(req, 'base/delete.html', {'obj':channel})

@login_required(login_url='login')
def deleteMessage(req, id):
    message = Message.objects.get(id=id)
    if req.user != message.user:
        return HttpResponse('You are not allowed to update this message')
    if req.method == 'POST':
        message.delete()
        return redirect('home')
    return render(req, 'base/delete.html', {'obj':message})

