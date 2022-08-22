from django.urls import path

from . import views

urlpatterns = [
    # Auth
    path('login/', views.loginView, name='login'),
    path('register/', views.registerView, name='register'),
    path('logout/', views.logoutView, name='logout'),

    path('', views.home, name='home'),
    path('room/<int:id>/', views.room, name='room'),
    path('user-profile/<int:id>/', views.userProfile, name='user-profile'),
    path('user-settings/', views.userSettings, name='user-settings'),
    path('topics/', views.topicView, name='topics'),
    path('activity/', views.activityView, name='activity'),

    #  CRUD
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<int:id>', views.updateRoom, name='update-room'),
    path('delete-room/<int:id>', views.deleteRoom, name='delete-room'),
    path('delete-msg/<int:id>', views.deleteMsg, name='delete-msg'),

]
