from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Channel


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['picture', 'username', 'email', 'country', 'degree', 'hobbies']


class CustomeUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'country', 'password1', 'password2']

class RoomForm(ModelForm):
    class Meta:
        model = Channel
        fields = '__all__'
        exclude = ['host', 'paticipants']
