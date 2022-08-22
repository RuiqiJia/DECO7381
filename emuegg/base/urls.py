from django.urls import path
from . import views
# from django.http import HttpResponse

urlpatterns = [
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.home, name="home"),
    path('profile/<str:id>/', views.profile, name="profile"),
    path('updateProfile/', views.updateProfile, name="updateProfile"),
    path('channel/<str:id>/', views.channel, name="channel"),
    path('map/', views.map, name="map"),
    path('create_channel/', views.createChannel, name="create_channel"),
    path('update_channel/<str:id>/', views.updateChannel, name="update_channel"),
    path('delete_channel/<str:id>/', views.deleteChannel, name="delete_channel"),
    path('delete_message/<str:id>/', views.deleteMessage, name="delete_message"),
]