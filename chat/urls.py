from django.urls import path

from . import views

app_name = "chat"
urlpatterns = [
    path('', views.index, name='index'),
    path(
        'conversationws/<str:receiverUsername>/',
        views.conversation,
        name='conversation'
    ),
    path(
        'conversation/<str:receiverUsername>/',
        views.ConversationView.as_view(),
        name='conversation',
    ),
    path(
        'conversations/', views.ConversationHomeView.as_view(), name='conversation_home'
    ),
]
