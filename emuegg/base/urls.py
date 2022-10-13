from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.home, name="home"),
    path('profile/<str:id>/', views.profile, name="profile"),
    path('updateProfile/', views.updateProfile, name="updateProfile"),
    path('channel/<str:id>/', views.channel, name="channel"),
    # path('map/', views.map, name="map"),
    path('create_channel/', views.createChannel, name="create_channel"),
    path('update_channel/<str:id>/', views.updateChannel, name="update_channel"),
    path('delete_channel/<str:id>/', views.deleteChannel, name="delete_channel"),
    path('delete_message/<str:id>/', views.deleteMessage, name="delete_message"),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='finish_changing_password.html'), 
        name='finish_changing_password'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='reset_password.html'), 
        name='reset_password'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_finished.html'),
     name='reset_finished'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
     name='password_reset_complete'),

    path('send_request/<str:id>/', views.send_request, name="send_request"),
    path('requests_page/<str:id>/', views.requests_page, name="requests_page"),
    path('accept_request/<requests_id>/', views.accept_request, name="accept_request"),
    path('private_chat/', views.private_chat, name="private_chat"),
    path('start_chat/', views.start_chat, name="start_chat"),


    path('friend_list/<int:user_id>/', views.friend_list, name="friend_list"),    # not use friends_list.html, use friend_list.html instead

    # path('friend/', views.friend, name="friend"),

    path('chat_list/', views.chat_list, name="chat_list"),
    path('chat_box/', views.chat_box, name="chat_box"),
    path('map_test/', views.map_test, name="map_test"),
    # path('feedback/', views.friend_feedback, name="friend_feedback")
]
