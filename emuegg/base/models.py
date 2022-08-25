from email.policy import default
from math import degrees
from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True)
    picture = models.ImageField(null=True, default='')
    country = models.CharField(max_length=50, null=True)
    degree = models.CharField(max_length=50, null=True)
    hobbies = models.CharField(max_length=50, null=True)
    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: list = ['username', 'country']

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
        if friend not in self.friend.all():
            self.friend.add(friend)
    
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
    
    def accept_request(self):
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
