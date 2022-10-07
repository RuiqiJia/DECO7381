from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Channel


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['Picture', 'username', 'email', 'Country', 'Major', 'Courses']


class CustomeUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'Country', 'password1', 'password2']

class RoomForm(ModelForm):
    class Meta:
        model = Channel
        fields = '__all__'

        # set initial value for host, participants, update, created
        # initial={'host': '1', 'participants': '1', } # ? how to get current user? current time? 
        # fields = ['name', 'topic', 'description']
        

class CountryForm(ModelForm):
    class Meta:
        model = User
        fields = ['Country']
    