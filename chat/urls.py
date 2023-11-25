from django.urls import path

from . import views

app_name = "chat"
urlpatterns = [
    path('', views.index, name='index'),
    path(
        'conversation/<str:receiverUsername>/',
        views.ConversationWsView.as_view(),
        name='conversation',
    ),
    path(
        'conversation_http/<str:receiverUsername>/',
        views.ConversationHttpView.as_view(),
        name='conversation_http',
    ),
    path(
        'conversations/', views.ConversationHomeView.as_view(), name='conversation_home'
    ),
]
