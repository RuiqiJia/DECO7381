from calendar import c

import branca
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import User, Channel, Message, Topic, Friends, FriendRequest, PrivateChat, PrivateMessage
from .forms import UserForm, CustomeUserCreationForm, RoomForm, CountryForm 
import folium
import geocoder
import json
from .status import Status
# visualize wikipedia contents of corresponding city
import wikipedia
import re

# required library to build message notification
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
from notifications.signals import notify

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
    # form = CustomeUserCreationForm()
    if req.method == 'POST':
        form = CustomeUserCreationForm(req.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, 'An error occurred. Please try again.')
    # return render(req, 'base/login.html', {'form' : form})
    return render(req, 'base/login.html')

    
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
    try:
        friends = Friends.objects.get(user=user)
    except Friends.DoesNotExist:
        friends = Friends(user=user)
        friends.save()
    all_friends = friends.friend.all()
    data = {}
    is_self = True
    is_friend = False
    friend_request = Status.NO_REQUEST.value
    friend_requests = None

    auth_user =  req.user
    if auth_user.is_authenticated and auth_user != user:
        is_self = False
        if all_friends.filter(id=auth_user.id):
            is_friend = True
        else:
            is_friend = False
            #frind request send to auth_user
            if is_friendRequest(sender=user, receiver=auth_user):
                friend_request = Status.REQUEST_SENT.value
                data['pending_request'] = is_friendRequest(sender=user, receiver=auth_user).id
            # friend request sent from auth_user
            elif is_friendRequest(sender=user, receiver=auth_user) != False:
                friend_request = Status.REQUEST_RECEIVED.value
            else:
                # no request
                friend_request = Status.NO_REQUEST.value
    elif not auth_user.is_authenticated:
        is_self = False
    else:
        
        friend_requests = FriendRequest.objects.filter(receiver=auth_user, is_accepted=True)
    data['user'] = user  
    data['is_self'] = is_self
    data['is_friend'] = is_friend
    data['friend_request'] = friend_request
    data['friend_requests'] = friend_requests
    data[all_friends] = all_friends
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
    # form = CountryForm()
    # users = User.objects.all()
    #
    # location = geocoder.osm('Australia')
    # lat = location.lat
    # lng = location.lng
    # if req.method == 'POST':
    #     form = CountryForm(req.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('map')
    # m = folium.Map(location=[-27.4973, 153.0134], zoom_start=4)
    # folium.Marker([lat, lng], popup='<strong>Brisbane</strong>', tooltip="Click for more information").add_to(m)
    #
    # # 调整地图全屏的关键
    # fig = branca.element.Figure(height="100%")
    # fig.add_child(m)
    #
    # m = m._repr_html_()
    # data = {'m' : m, 'form' : form}
    # return render(req, 'base/map.html', data)

    if req.method == "GET":
        m = folium.Map(location=[-24.7761086, 134.755], zoom_start=4)
        fig = branca.element.Figure(height="100%")
        fig.add_child(m)
        m = m._repr_html_()
        return render(req, 'base/map.html', {'m': m})

    loc = req.POST.get("location")
    print(loc)
    location = geocoder.osm(loc)
    lat = location.lat
    lng = location.lng
    print(lat, lng)

    m = folium.Map(location=[lat, lng], zoom_start=4)

    # added by JWM, display the wikipedia content of the location
    wiki_loc = wikipedia.page(loc)
    wiki_content = str(wiki_loc.content)[0:200]

    open_brankets = ['[', '(', '{']
    close_brankets = {']': '[', ')': '(', '}': '{'}
    stack = []
    #
    # start = -100
    # end = -1
    wiki_content_new = ""
    wiki_content = re.sub("[\(\[].*?[\)\]]", "", wiki_content)

    for i in range(len(wiki_content)):
        if (wiki_content[i] in open_brankets) or (wiki_content[i] in close_brankets.keys()):
            pass
        else:
            wiki_content_new += wiki_content[i]
    # for i in range(len(wiki_content)):
    #
    #     # if wiki_content[i] in open_brankets and start == -1:
    #     #     start = i
    #     #     stack.append(wiki_content[i])
    #     # # elif wiki_content[i] in close_brankets.keys() and len(stack) > 1:
    #     # #     stack.pop()
    #     # elif wiki_content[i] in close_brankets.keys() and end == -1:
    #     #     # stack.pop()
    #     #     end = i
    # wiki_content = wiki_content[0:start] + wiki_content[end+1:]

    folium.Marker([lat, lng], popup='<strong>' + loc + '<br>' + '<br>' + wiki_content_new + '</strong>', tooltip="Click for more information").add_to(m)

    fig = branca.element.Figure(height="100%")
    fig.add_child(m)
    m = m._repr_html_()

    return render(req, "base/map.html", {'m': m})

    

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

# friend
def is_friendRequest(sender, receiver):
    """
    Check if two users have friends request or not
    """
    try:
        return FriendRequest.objects.get(sender=sender, receiver=receiver)
    except FriendRequest.DoesNotExist:
        return False

@login_required(login_url='login')
def send_request(req, id):
    """
    Send friend request to another user
    """
    data = {}
    user = req.user
    receiver = User.objects.get(id=id)
    friend_request, created = FriendRequest.objects.get_or_create(sender=user, receiver=receiver)
    if created:
        data['response'] = "Friend request has been sent successfully"
        return JsonResponse(data)

    else:
        return HttpResponse('Friend request already sent')
    # 
    # if req.method == 'POST' and user.is_authenticated:
    #     receiver_id = req.POST.get("receiver_id")
    #     if receiver_id:
    #         receiver = User.objects.get(id=receiver_id)
    #         friend_requests = FriendRequest.objects.filter(sender=user, receiver=receiver)
    #         for request in friend_requests:
    #             if request.is_accepted:
    #                 return HttpResponse('You have sent a friend request to this user')
    #         friend_request = FriendRequest(sender=user, receiver=receiver)
    #         friend_request.save()
    #         data['response'] = "Friend request has been sent successfully"
    #     else:
    #         data['response'] = "Please select a receiver"
    # else:
    #     data['response'] = "You are not authenticated"
    # return JsonResponse(data)

def requests_page(req, id):
    """
    List all friend requests
    """
    data = {}
    auth_user = req.user
    user = User.objects.get(id=id)
    if auth_user.is_authenticated:
        if auth_user == user:
            friend_requests = FriendRequest.objects.filter(receiver=user)
            data['friend_requests'] = friend_requests
    else:
        return redirect('login')
    return render(req, 'base/requests_page.html', data)

def accept_request(req, id):
    friend_request = FriendRequest.objects.get(id=id)
    if friend_request.receiver == req.user:
        #update friend model
        # Friends.user = req.user
        # Friends.user.save()
        # Friends.friend = friend_request.sender
        # Friends.friend.save()
        # friend_request.receiver.friends.add(friend_request.sender)
        # friend_request.sender.friends.add(friend_request.receiver)
        friend_request.delete()
        return HttpResponse('Friend request has been accepted')
    # data = {}
    # auth_user = req.user
    # user = User.objects.get(id=id)
    # if auth_user.is_authenticated:
    #     if auth_user == user and req.method == 'GET':
    #         requests_id = FriendRequest.objects.get(id=id)
    #         if requests_id:
    #             friend_request = FriendRequest.objects.get(id=requests_id)
    #             if friend_request.receiver == auth_user:
    #                 friend_request.accept()
    #                 data['res'] = "Friend request has been accepted successfully"
    
    # return JsonResponse({'res' : 'Friend request has been accepted successfully'})

# Juewen Ma
# visualise the message received from other users(half-way through)
def index(request):
    try:
        users = User.objects.all()
        print(request.user)
        user = User.objects.get(username=request.user)
        return render(request, 'index.html', {'users': users, 'user': user})
    except Exception as e:
        print(e)
        return HttpResponse("Please login from admin site for sending messages.")


def message(request):
    try:
        if request.method == 'POST':
            sender = User.objects.get(username=request.user)
            receiver = User.objects.get(id=request.POST.get('user_id'))
            notify.send(sender, recipient=receiver, verb='Message', description=request.POST.get('message'))
            return redirect('index')
        else:
            return HttpResponse("Invalid request")
    except Exception as e:
        print(e)
        return HttpResponse("Please login from admin site for sending messages")

def private_chat(req):
    room1 = PrivateChat.objects.filter(user1=req.user)
    room2 = PrivateChat.objects.filter(user2=req.user)
    rooms = room1 | room2
    data = {}
    friends_list = []
    for room in rooms:
        if room.user1 == req.user:
            friends_list.append({'message': "", 'user': room.user2})
        else:
            friends_list.append({'message': "", 'user': room.user1})
    data['friends_list'] = friends_list

    return render(req, 'base/private_chat.html')

def create_chat(user1, user2):
	try:
		chat = PrivateChat.objects.get(user1=user1, user2=user2)
	except PrivateChat.DoesNotExist:
		try:
			chat = PrivateChat.objects.get(user1=user2, user2=user1)
		except PrivateChat.DoesNotExist:
			chat = PrivateChat(user1=user1, user2=user2)
			chat.save()
	return chat

def start_chat(req):
    user1 =req.user
    data = {}
    
    user2_id = req.POST.get('user2_id')
    user2 = User.objects.get(id=user2_id)
    chat = create_chat(user1, user2)
    data['response'] = "Chat created successfully"
    data['chat_id'] = chat.id

    return JsonResponse(data)
       
