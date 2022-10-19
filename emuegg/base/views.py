import branca
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .management.commands.make_recommendation import MakeRecommendation
from .models import User, Channel, Message, Topic, Friends, FriendRequest, PrivateChat, PrivateMessage
from .forms import UserForm, CustomeUserCreationForm, RoomForm, CountryForm 
import folium
import geocoder
import json
from .status import Status
from itertools import chain
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from geopy.geocoders import Nominatim

def loginView(req):
    """
        login view
    """
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
    """
        sign up view
    """
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
    """
        
    """

    # query channels using name topic and description
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
    # check whether username has not been change, if it is, update it with its email address
    if user.username == '' or user.username is None:
        user.username = user.email
        user.save()
    # access its related channels and messages
    channels = user.channel_set.all()
    messages = user.message_set.all()
    data = {'user': user, 'channels': channels, 'messages': messages}
    # try to get the entry of given user in friend table, if not exist, create that user instead
    # id: auto-generated id; user_id: corresponding user id (one-to-one)
    try:
        friends = Friends.objects.get(user=user)

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
        print("It is entering")
        # check whether the login user is a friend of that user
        if all_friends.filter(id=auth_user.id):
            is_friend = True
            safe_mode = True
            print("1")
        else:
            is_friend = False
            safe_mode = False
            print("2")
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
    print("current profile is your friend:", is_friend)
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
    return render(req, "base/map.html", {'m': m})

@login_required(login_url='login')
def createChannel(req):
    if req.method == 'POST':
        form = RoomForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
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

        return render(req, 'base/friend_feedback.html', {'res': res})
    else:
        res = "Friend request has been sent successfully"
        return render(req, 'base/friend_feedback.html', {'res': res})
    
 
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
    list = []
    data = {}
    friends = None
    if req.method == "GET":
        user = req.user
        try:
            friend_list = Friends.objects.get(user=user)
            counter = 0
            for each_friend in friend_list.friend.all():
                list.append(each_friend)
                print("friend: ", each_friend)
                counter += 1

            if counter == 0:
                friends = None
            else:
                friends = list[0]
        except ObjectDoesNotExist:

            pass

    data['friend'] = friends
    return render(req, 'base/chat_list.html', data)


def chat_box(req):
    list = []
    data = {}
    friends = None
    user = req.user

    # initialize the required field
    common_topic = []
    common_courses = []
    common_major = []
    has_c_major = False
    has_c_topics = False
    has_c_courses = False

    # generate req user's own topic, courses, major set
    user_topic = {x for x in split_string(req.user.Topics)}
    user_courses = {x for x in split_string(req.user.Courses)}
    user_major = {req.user.Major}
    print(user, user_major, user_courses, user_topic)

    friend_topic = None
    friend_courses = None
    friend_major = None
    friend_ename = None


    has_friends = False

    # 判断请求种类，若为get请求，传回相关参数
    if req.method == "GET":
        user = req.user

        try:
            friend_list = Friends.objects.get(user=user)
            counter = 0
            for each_friend in friend_list.friend.all():
                list.append(each_friend)
                print("friend: ", each_friend)
                counter += 1
            # if no friend found
            if counter == 0:
                friends = None
                has_friends = False
            # if some friend exists, display the first friend found
            else:
                friends = list[0]
                has_friends = True
        except ObjectDoesNotExist:
            print("Object does not exist")
            pass

    # 如果好友是None，默认传Jack Li 的写死界面
    if friends is None:
        pass
    else:
        # 如果有friend，传回friend相关参数
        # generate this friend's topic, courses, major set
        friend_topic = {x for x in split_string(friends.Topics)}
        friend_courses = {x for x in split_string(friends.Courses)}
        friend_major = {friends.Major}

        # 当好友username问none，取好友的email@之前的字符串
        friend_ename = friends.email.split("@")[0]
        print(friend_ename)

        # common_topic related variable
        common_topic = user_topic.intersection(friend_topic)
        has_c_topics = True if len(common_topic) > 0 else False

        # common_major related variable
        common_major = user_major.intersection(friend_major)
        has_c_major = True if len(common_major) > 0 else False

        # common_courses related variable
        common_courses = user_courses.intersection(friend_courses)
        has_c_courses = True if len(common_courses) > 0 else False

    # 判断是用写死的Jack Li界面，还是当前基于此好友的动态界面
    data['has_friends'] = has_friends
    data['friend'] = friends

    # common major list  && whether has common major
    data['common_major'] = ','.join(common_major)
    data['has_c_major'] = has_c_major

    # common topic list && whether has common topics
    data['common_topic'] = ','.join(common_topic)
    data['has_c_topics'] = has_c_topics
    # common courses list && whether has common courses
    data['common_courses'] = ','.join(common_courses)
    data['has_c_courses'] = has_c_courses

    # current user
    data['user'] = user
    data['friend_ename'] = friend_ename

    return render(req, 'base/chat_box.html', data)


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
    location = geocoder.osm(loc)
    country = location.country
    url = "https://en.wikipedia.org/wiki/" + country
    lat = location.lat
    lng = location.lng
    print(lat, lng)

    return render(req, "base/map_test.html", {"lat": lat, "lng": lng, "url": url, 'country': country})


def split_string(string_sequence: str) -> list:
        """
        Helper method to split topic/course
        topics: input topic string
        Return:
            list contains all topic
        """

        string_list = []
        # return empty list if it is empty
        if string_sequence is None:
            return string_list
        # split the string and strip the whitespace
        else:
            string_list = string_sequence.split(",")

            for i in range(len(string_list)):
                string_list[i] = string_list[i].strip()
        return string_list
