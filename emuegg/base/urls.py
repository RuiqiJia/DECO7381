from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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

    path('send_request/', views.send_request, name="send_request"),
]