from django.urls import path
from . import views

app_name = 'a_rtchat'

urlpatterns = [
    path('', views.ChatView.as_view(), name="home"),
    path('chat/new_groupchat/', views.CreateGroupChat.as_view(), name="new-groupchat"),
    path('chat/<username>/', views.GetOrCreateChatRoom.as_view(), name="start-chat"),
    path('chat/room/<chatroom_name>/', views.ChatView.as_view(), name="chatroom"),
    path("chat/edit/<chatroom_name>/", views.ChatRoomEditView.as_view(), name="edit-chatroom"),
    path("chat/delete/<chatroom_name>/", views.ChatRoomDeleteView.as_view(), name="chatroom-delete"),
    path("chat/leave/<chatroom_name>/", views.ChatRoomLeaveView.as_view(), name="chatroom-leave")
]
