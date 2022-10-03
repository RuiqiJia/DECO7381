from email.policy import default
from math import degrees
from django.db import models

from django.contrib.auth.models import AbstractUser
# from .utility import create_chat

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True)
    Picture = models.ImageField(null=True, default='')
    Country = models.CharField(max_length=50, null=True)
    Major = models.CharField(max_length=50, null=True)
    Courses = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=50, unique=False, null=True)
    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: list = ['username', 'Country']

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

class Channel(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    message = models.TextField()
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=50)

class Friends(models.Model):
    # one user can only have one friends list
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friend = models.ManyToManyField(User, blank=True, related_name='friend')
    

    def __str__(self):
        return self.user.username

    def add_friend(self, friend):
        if not friend in self.friend.all():
            self.friend.add(friend)
            self.save()
        # chat = create_chat(self.user, friend)
        # chat.save()

    
    def remove_friend(self, friend):
        if friend in self.friend.all():
            self.friend.remove(friend)
    
    def is_common_friend(self, friend):
        if friend in self.friend.all():
            return True
        return False

class FriendRequest(models.Model):
    # one user can have mutiple friend requests
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    is_accepted = models.BooleanField(default=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username
    
    def accept_requests(self):
        receive_request = Friends.objects.get(user=self.receiver)
        if receive_request:
            receive_request.add_friend(self.sender)
            send_request = Friends.objects.get(user=self.sender)
            if send_request:
                send_request.add_friend(self.receiver)
                self.is_accepted = False

    def reject_request(self):
        self.is_accepted = False
        self.save()

class PrivateChat(models.Model):
    user1= models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2= models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')

class PrivateMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(PrivateChat, on_delete=models.CASCADE)
    message = models.TextField(unique=False, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
