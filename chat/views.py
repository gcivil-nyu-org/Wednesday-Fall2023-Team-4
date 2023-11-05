from django.shortcuts import render

from .models import Message

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