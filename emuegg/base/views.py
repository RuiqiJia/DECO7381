
import branca
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from scipy.fft import idct

from .management.commands.make_recommendation import MakeRecommendation
from .models import User, Channel, Message, Topic, Friends, FriendRequest, PrivateChat, PrivateMessage
from .forms import UserForm, CustomeUserCreationForm, RoomForm, CountryForm 
import folium
import geocoder
import json
from .status import Status
from itertools import chain
# visualize wikipedia contents of corresponding city
# import wikipedia
# import re
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# required library to build message notification
# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from .models import User
# from notifications.signals import notify
from geopy.geocoders import Nominatim

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
    data = {'channels': channels,
            'topics': topics,
            'channel_count': channel_count,
            'channel_messages': channel_messages
      }
    return render(req, 'base/home.html', data)

def profile(req, id):
    # control how much information will be display on profile
    # True: auth_user's profile and friend's profile; False: non-friend's profile
    safe_mode = False

    # get the user with given id
    user = User.objects.get(id=id)
    print("input user", user)  # checking purpose
    # access its related channels and messages
    channels = user.channel_set.all()
    messages = user.message_set.all()
    data = {'user': user, 'channels': channels, 'messages': messages}
    # try to get the entry of given user in friend table, if not exist, create that user instead
    # id: auto-generated id; user_id: corresponding user id (one-to-one)
    try:
        friends = Friends.objects.get(user=user)
        print("get friends: ", friends) # checking purpose
    except Friends.DoesNotExist:
        friends = Friends(user=user)
        friends.save()
    # get the user's friends
    all_friends = friends.friend.all()

    data = {}
    is_self = True
    is_friend = False
    friend_request = Status.NO_REQUEST.value
    friend_requests = None
    # get the user who trigger this HTTP request (user who logged in to the account)
    auth_user = req.user
    # user who logged in request other user's profile
    if auth_user.is_authenticated and auth_user != user:
        is_self = False
        # check whether the login user is a friend of that user
        if all_friends.filter(id=auth_user.id):
            is_friend = True
            safe_mode = True
        else:
            is_friend = False
            safe_mode = False
            #frind request send to auth_user
            if is_friendRequest(sender=user, receiver=auth_user) != False:
                friend_request = Status.REQUEST_SENT.value
                data['pending_request'] = is_friendRequest(sender=user, receiver=auth_user).id
            # friend request sent from auth_user
            elif is_friendRequest(sender=auth_user, receiver=user) != False:
                friend_request = Status.REQUEST_RECEIVED.value
                print(friend_request, "from here")
            else:
                # no request
                friend_request = Status.NO_REQUEST.value
                print("No request found")
    elif not auth_user.is_authenticated:
        is_self = False
    # request the auth_user's own profile
    else:
        friend_requests = FriendRequest.objects.filter(receiver=auth_user, is_accepted=True)
        safe_mode = True

    # check current user
    data['user'] = user
    data['is_self'] = is_self
    data['is_friend'] = is_friend
    # 若访问非当前登陆用户profile，传回对应用户(发出/收到)的friend request信息
    data['friend_request'] = friend_request
    # 若访问当前登陆用户的profile，传回登陆用户自己的friend request信息
    data['friend_requests'] = friend_requests
    # 传回当前访问profile用户的所有好友entries
    data['all_friends'] = all_friends
    # used to check how mush information to disclose
    data['safe_mode'] = safe_mode

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
        # m = folium.Map(location=[-24.7761086, 134.755], zoom_start=4)
        m = folium.Map(location=[-24.7761086, 134.755], zoom_start=4)
        fig = branca.element.Figure(height="100%")
        fig.add_child(m)
        m = m._repr_html_()
        return render(req, 'base/map.html', {'m': m})

    loc = req.POST.get("location")
    loc = str(loc).strip()
    #error handling for china
    # if loc in ("China", "china", "CHINA"):
    #     loc = "中国"
    location = geocoder.osm(loc)
    lat = location.lat
    lng = location.lng

    m = folium.Map(location=[lat, lng], zoom_start=4)

    # added by JWM, display the wikipedia content of the location
    # wiki_loc = wikipedia.page(loc)
    # wiki_content = str(wiki_loc.content)[0:200]
    #
    # open_brankets = ['[', '(', '{']
    # close_brankets = {']': '[', ')': '(', '}': '{'}
    # stack = []
    #
    # start = -100
    # end = -1
    # wiki_content_new = ""
    # wiki_content = re.sub("[\(\[].*?[\)\]]", "", wiki_content)

    # for i in range(len(wiki_content)):
    #     if (wiki_content[i] in open_brankets) or (wiki_content[i] in close_brankets.keys()):
    #         pass
    #     else:
    #         wiki_content_new += wiki_content[i]
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

    # folium.Marker([lat, lng], popup='<strong>' + '<a href="">' + loc + '</a>' + '<br>' + wiki_content_new + '</strong>', tooltip="Click for more information").add_to(m)

    geolocator = Nominatim(user_agent="geoapiExercises")
    country_name = geolocator.reverse(str(lat)+","+str(lng)).raw['address'].get('country', '')
    print(country_name)

    url = "https://en.wikipedia.org/wiki/" + country_name
    iframe = '<iframe frameborder="0" height="250px" src="' + url + '"></iframe><h4><a href="http://127.0.0.1:8000/"> Join Discussion >>> </a></h4>'
    print(iframe)
    folium.Marker([lat, lng], popup=folium.Popup(max_width=300, html=iframe)).add_to(m)

    fig = branca.element.Figure(height="100%")
    fig.add_child(m)
    m = m._repr_html_()
    # loc_name = Channel.objects.get(name=loc)

    return render(req, "base/map.html", {'m': m})

    

@login_required(login_url='login')
def createChannel(req):
    if req.method == 'POST':
        form = RoomForm(req.POST)
        if form.is_valid():
            form.save()
            # return HttpResponse('Channel has been created successfully')
            return redirect('home')
    data = {'form' : RoomForm()}
    return render(req, 'base/channel_form.html', data)
    # return render(req, 'base/channel_create.html', data)

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
        return HttpResponse('You are not allowed to delete this channel')
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
        res = "Friend request has been sent successfully"
        # data['res'] = res
        # return JsonResponse(data)
        return render(req, 'base/friend_feedback.html', {'res': res})

    else:
        res = "Friend request has been sent successfully"
        # return HttpResponse('Friend request already sent')
        return render(req, 'base/friend_feedback.html', {'res': res})
    
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

def accept_request(req, *args, **kwargs):

    # friend_request = FriendRequest.objects.get(id=id)
    # if friend_request.receiver == req.user:
    #     #update friend model
    #     # Friends.user = req.user
    #     # Friends.user.save()
    #     # Friends.friend = friend_request.sender
    #     # Friends.friend.save()
    #     # friend_request.receiver.friends.add(friend_request.sender)
    #     # friend_request.sender.friends.add(friend_request.receiver)
    #     friend_request.accept_request()
    #     friend_request.delete()
    #     return HttpResponse('Friend request has been accepted')
    data = {}
    auth_user = req.user
    
    if auth_user.is_authenticated and req.method == 'GET':
        requests_id = kwargs.get('requests_id')
        if requests_id:
            friend_request = FriendRequest.objects.get(id=requests_id)
            if friend_request.receiver == auth_user:
                friend_request.accept_requests()
                friend_request.delete()
                res = "Friend request has been accepted successfully"
    
    # return JsonResponse({'res' : 'Friend request has been accepted successfully'})
    return render(req, 'base/friend_feedback.html', {'res': res})

def friend_list(req, *args, **kwargs):
    # Written by Juewen Ma - Oct.7
    data = {}
    auth_user = req.user
    list = []
    recommendation_list = []
    if auth_user.is_authenticated:
        # ***** DO RECOMMENDATION *****
        # get current user object along with its username, Country, Course enrolled, etc
        curr_user = User.objects.get(id=auth_user.id)
        username = curr_user.username
        topics = curr_user.Topics
        major = curr_user.Major
        courses = curr_user.Courses
        country = curr_user.Country

        # collect the recommendation result
        recommend = MakeRecommendation(auth_user.id, username, topics, major, courses, country)
        # Spot 1
        spot1 = recommend.spot1_recommend()
        recommendation_list.append(spot1)
        print(str(spot1) + "is the first recommendation")

        # Spot 2
        spot2 = recommend.spot2_recommend(spot1)
        recommendation_list.append(spot2)
        print(str(spot2) + "is the second recommendation")

        # Spot 3
        spot3 = recommend.spot3_recommend(spot1, spot2)
        recommendation_list.append(spot3)
        print(str(spot3) + "is the third recommendation")

        # Spot 4
        spot4 = recommend.spot4_recommend(spot1, spot2, spot3)
        recommendation_list.append(spot4)
        print(str(spot4) + "is the fouth recommendation")

        print(recommend.split_string(topics))

        # ***** SHOW CURRENT FRIEND LIST *****
        user_id = kwargs.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            print("user_id: ", user_id)
            # error handling if get method cannot retrieve any available user
            try:
                friend_list = Friends.objects.get(user=user.id)
                print("friend_list: ", friend_list.__class__)
                print("friend_list.friend.all(): ", friend_list.friend.all())
                for friend in friend_list.friend.all():
                    list.append(friend)
                    print("friend: ", friend)
            except ObjectDoesNotExist:
                pass

        if auth_user != user:

            return HttpResponse('You are not allowed to view this page')
    data['friends'] = list
    data['recommendation'] = recommendation_list


    return render(req, 'base/friend_list.html', data)


def index(request):
    try:
        users = User.objects.all()
        # print(request.user)
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
DEBUG = False
def private_chat(req):
    friend_lists = Friends.objects.all()
    for f in friend_lists:
        for friend in f.friend.all():
            chat = create_chat(f.user, friend)
            chat.save()
    room1 = PrivateChat.objects.filter(user1=req.user)
    room2 = PrivateChat.objects.filter(user2=req.user)
    rooms = list(chain(room1, room2))
    print(room1)
    data = {}
    friends_list = []
    for room in rooms:
        if room.user1 == req.user:
            friend = room.user2
            print(friend)
            # friends_list.append({'message': "", 'user': room.user2})
        else:
            friend = room.user1
        friends_list.append({'message': "", 'friend': friend})
    data['friends_list'] = friends_list
    data['debug'] = DEBUG
    data['debug_mode'] = settings.DEBUG
    print(data)
    return render(req, 'base/private_chat.html', data)
     
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

def start_chat(req, *args, **kwargs):
    user1 =req.user
    data = {}
    if req.method == 'POST':
        user2_id = req.POST.get('user2_id')
        user2 = User.objects.get(id=user2_id)
        chat = create_chat(user1, user2)
        
        data['response'] = "Chat created successfully"
        data['chat_id'] = chat.id
        print(chat.id)

    return HttpResponse(json.dumps(data), content_type="application/json")

def chat_list(req):
    return render(req, 'base/chat_list.html')

def chat_box(req):
    return render(req, 'base/chat_box.html')
       
def friend(req):
    return render(req, 'base/friend_list.html')

def map_test(req):
    if req.method == "GET":

        capitals = ['Beijing', 'Canberra', 'Tokyo', 'Seoul', 'Manila', 'Hanoi', 'Kuala_Lumpur', 'Jakarta', 'New_Delhi', 'Bangkok']
        cors = []
        for capital in capitals:
            Capitallocation = geocoder.osm(capital)
            capLat = Capitallocation.lat
            capLng = Capitallocation.lng
            country= Capitallocation.country
            url1 = 'https://en.wikipedia.org/wiki/' + capital
            cors.append([capLat, capLng, url1, country])
        return render(req, 'base/map_test.html', {'cors': cors})

    loc = req.POST.get("location")
    loc = str(loc).strip()
    print(loc)
    # print(url)
    location = geocoder.osm(loc)
    country = location.country
    url = "https://en.wikipedia.org/wiki/" + country
    lat = location.lat
    lng = location.lng
    print(lat, lng)

    return render(req, "base/map_test.html", {"lat": lat, "lng": lng, "url": url, 'country': country})

