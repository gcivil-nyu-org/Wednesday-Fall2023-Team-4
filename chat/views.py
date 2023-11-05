from django.shortcuts import render

from .models import Message, DirectMessage

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

    return render(request, 'chat/room.html', {'room_name': room_name, 'username': username, 'messages': messages})

def conversation(request, receiverUsername):
    print('Conversation : ', request.user)
    senderUsername = request.user.username
    room_name = '_'.join(sorted([senderUsername, receiverUsername]))
    print(senderUsername, receiverUsername, room_name)
    messages = DirectMessage.objects.filter(room=room_name)[0:25]

    return render(request, 'chat/conversation.html', {'room_name': room_name, 'sender': senderUsername, 'receiver': receiverUsername, 'messages': messages})