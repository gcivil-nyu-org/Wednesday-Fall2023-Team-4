from django.urls import path

from . import views

app_name = "chat"
urlpatterns = [
    path('', views.index, name='index'),
    # path('<str:room_name>/', views.room, name='room'),
    path(
        'conversation/<str:receiverUsername>/', views.conversation, name='conversation'
    ),
    # path(
    #     'conversations/', views.conversation_home, name='conversation_home'
    # ),ConversationHomeView
    path(
        'conversations/', views.ConversationHomeView.as_view(), name='conversation_home'
    ),
]
