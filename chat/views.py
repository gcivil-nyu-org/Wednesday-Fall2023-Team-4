from django.shortcuts import render
from django.db.models import Q
from django.views import generic

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic

from .models import Message, DirectMessage, DirectMessagePermission, Permission


def index(request):
    # from redis import Redis

    # redis_host = '127.0.0.1'
    # r = Redis(redis_host, socket_connect_timeout=1) # short timeout for the test

    # r.ping()

    # print('connected to redis "{}"'.format(redis_host))
    return render(request, 'chat/index.html')


def room(request, room_name):
    username = request.GET.get('username', 'Anonymous')
    messages = Message.objects.filter(room=room_name)[0:25]

    return render(
        request,
        'chat/room.html',
        {'room_name': room_name, 'username': username, 'messages': messages},
    )


def conversation(request, receiverUsername):
    senderUsername = request.user.username
    room_name = '_'.join(sorted([senderUsername, receiverUsername]))

    messages = DirectMessage.objects.filter(room=room_name)[0:25]

    try:
        permissions = list(
            DirectMessagePermission.objects.filter(
                Q(sender__exact=senderUsername) | Q(receiver__exact=senderUsername)
            )
        )
    except DirectMessagePermission.DoesNotExist:
        permissions = [
            DirectMessagePermission.objects.create(
                sender=senderUsername,
                receiver=receiverUsername,
                permission=Permission.ALLOWED,
            )
        ]

    allowed_usernames = []
    for p in permissions:
        if p.sender == senderUsername:
            allowed_usernames.append(p.receiver)
        else:
            allowed_usernames.append(p.sender)

    return render(
        request,
        'chat/conversation.html',
        {
            'room_name': room_name,
            'sender': senderUsername,
            'receiver': receiverUsername,
            'messages': messages,
            'allowed_usernames': allowed_usernames,
        },
    )


class ConversationHomeView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if not request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse("rrapp:login")
            )
        # else process dispatch as it otherwise normally would
        return super(ConversationHomeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        cur_username = request.user.username
    
        pending_connections = []
        active_connections = []
        requested_connections = []
        
        try:
            pending_connections = list(
                DirectMessagePermission.objects.filter(
                    Q(receiver__exact=cur_username) & Q(permission__exact=Permission.REQUESTED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            pending_connections = []
        
        try:
            active_connections = list(
                DirectMessagePermission.objects.filter(
                    (Q(receiver__exact=cur_username) | Q(sender__exact=cur_username)) & Q(permission__exact=Permission.ALLOWED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            active_connections = []
        
        all_active_connection_usernames = []
        for p in active_connections:
            if p.sender == cur_username:
                all_active_connection_usernames.append(p.receiver)
            else:
                all_active_connection_usernames.append(p.sender)

        try:
            requested_connections = list(
                DirectMessagePermission.objects.filter(
                    Q(sender__exact=cur_username) & Q(permission__exact=Permission.REQUESTED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            requested_connections = []

        return render(
            request,
            'chat/conversation_home.html',
            {
                'cur_username': cur_username,
                'pending_connections': pending_connections,
                'active_connections': all_active_connection_usernames,
                'requested_connections': requested_connections,
            },
        )

    def post(self, request, *args, **kwargs):
        if "connection_accept" in request.POST:
            p = DirectMessagePermission.objects.get(sender=request.POST["connection_accept"], receiver=request.user.username)
            p.permission = Permission.ALLOWED
            p.save()
        elif "connection_reject" in request.POST:
            p = DirectMessagePermission.objects.get(sender=request.POST["connection_accept"], receiver=request.user.username)
            p.delete()
        else:
            pass

        return HttpResponseRedirect(
            reverse("chat:conversation_home")
        )

# def conversation_home(request):
    # cur_username = request.user.username
    
    # pending_connections = []
    # active_connections = []
    # requested_connections = []
    
    # try:
    #     pending_connections = list(
    #         DirectMessagePermission.objects.filter(
    #             Q(receiver__exact=cur_username) & Q(permission__exact=Permission.REQUESTED)
    #         )
    #     )
    # except DirectMessagePermission.DoesNotExist:
    #     pending_connections = []
    
    # try:
    #     active_connections = list(
    #         DirectMessagePermission.objects.filter(
    #             (Q(receiver__exact=cur_username) | Q(sender__exact=cur_username)) & Q(permission__exact=Permission.ALLOWED)
    #         )
    #     )
    # except DirectMessagePermission.DoesNotExist:
    #     active_connections = []
    
    # all_active_connection_usernames = []
    # for p in active_connections:
    #     if p.sender == cur_username:
    #         all_active_connection_usernames.append(p.receiver)
    #     else:
    #         all_active_connection_usernames.append(p.sender)

    # try:
    #     requested_connections = list(
    #         DirectMessagePermission.objects.filter(
    #             Q(sender__exact=cur_username) & Q(permission__exact=Permission.REQUESTED)
    #         )
    #     )
    # except DirectMessagePermission.DoesNotExist:
    #     requested_connections = []

    # return render(
    #     request,
    #     'chat/conversation_home.html',
    #     {
    #         'cur_username': cur_username,
    #         'pending_connections': pending_connections,
    #         'active_connections': all_active_connection_usernames,
    #         'requested_connections': requested_connections,
    #     },
    # )
