from django.shortcuts import render
from django.db.models import Q

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
        print('here', permissions)
    except DirectMessagePermission.DoesNotExist:
        permissions = [
            DirectMessagePermission.objects.create(
                sender=senderUsername,
                receiver=receiverUsername,
                permission=Permission.ALLOWED,
            )
        ]

    allowed_usernames = ['test']
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
