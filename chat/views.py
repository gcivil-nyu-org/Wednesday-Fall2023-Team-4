from django.shortcuts import render
from django.db.models import Q
from django.views import generic

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from rrapp.models import User
from .models import DirectMessage, DirectMessagePermission, Permission


def index(request):
    return render(request, 'chat/index.html')


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
            return HttpResponseRedirect(reverse("rrapp:login"))
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
                    Q(receiver__exact=cur_username)
                    & Q(permission__exact=Permission.REQUESTED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            pending_connections = []
        
        all_pending_connection_usernamesids = []
        for p in pending_connections:
            all_pending_connection_usernamesids.append(
                {
                    'id': User.objects.get(username=p.sender).id,
                    'username': p.sender,
                }
            )

        try:
            active_connections = list(
                DirectMessagePermission.objects.filter(
                    (Q(receiver__exact=cur_username) | Q(sender__exact=cur_username))
                    & Q(permission__exact=Permission.ALLOWED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            active_connections = []

        all_active_connection_usernamesids = []
        for p in active_connections:
            if p.sender == cur_username:
                all_active_connection_usernamesids.append(
                    {
                        'id': User.objects.get(username=p.receiver).id,
                        'username': p.receiver,
                    }
                )
            else:
                all_active_connection_usernamesids.append(
                    {'id': User.objects.get(username=p.sender).id, 'username': p.sender}
                )

        try:
            requested_connections = list(
                DirectMessagePermission.objects.filter(
                    Q(sender__exact=cur_username)
                    & Q(permission__exact=Permission.REQUESTED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            requested_connections = []
        
        all_requested_connection_usernamesids = []
        for p in requested_connections:
            all_requested_connection_usernamesids.append(
                {
                    'id': User.objects.get(username=p.receiver).id,
                    'username': p.receiver,
                }
            )

        return render(
            request,
            'chat/conversation_home.html',
            {
                'cur_username': cur_username,
                'pending_connections': all_pending_connection_usernamesids,
                'active_connections': all_active_connection_usernamesids,
                'requested_connections': all_requested_connection_usernamesids,
            },
        )

    def post(self, request, *args, **kwargs):
        if "connection_accept" in request.POST:
            p = DirectMessagePermission.objects.get(
                sender=request.POST["connection_accept"], receiver=request.user.username
            )
            p.permission = Permission.ALLOWED
            p.save()
        elif "connection_reject" in request.POST:
            print(request.POST)
            p = DirectMessagePermission.objects.get(
                sender=request.POST["connection_reject"], receiver=request.user.username
            )
            p.delete()
        else:
            pass

        return HttpResponseRedirect(reverse("chat:conversation_home"))


class ConversationView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("rrapp:login"))
        # else process dispatch as it otherwise normally would
        return super(ConversationView, self).dispatch(request, *args, **kwargs)
    
    def canDmReceiver(self, senderUsername, receiverUsername):
        try:
            permissions = list(
                DirectMessagePermission.objects.filter(
                    (Q(sender__exact=senderUsername) & Q(receiver__exact=receiverUsername)) | 
                    (Q(sender__exact=receiverUsername) & Q(receiver__exact=senderUsername))
                )
            )
        except DirectMessagePermission.DoesNotExist:
            # permission does not exist
            return False

        if len(permissions) == 0:
            return False
        
        p = permissions[0]
        if p.permission != Permission.ALLOWED:
            return False
        
        return True

    def get(self, request, receiverUsername, *args, **kwargs):
        senderUsername = request.user.username
        room_name = '_'.join(sorted([senderUsername, receiverUsername]))

        if not self.canDmReceiver(senderUsername, receiverUsername):
            print(senderUsername, receiverUsername)
            raise PermissionDenied('The receiver needs to accept your request before your can message them.')
        
        # TODO paginate
        messages = DirectMessage.objects.filter(room=room_name)

        # ALLOWED permission exists in DB
        # render the page and handle messages
        receiverUser = User.objects.get(username=receiverUsername)
        receiverUsernameId = {"username": receiverUsername, "id":receiverUser.id}
        return render(
            request,
            'chat/conversation_http.html',
            {
                'room_name': room_name,
                'sender': senderUsername,
                'receiver': receiverUsernameId,
                'messages': messages,
            },
        )

    def post(self, request, *args, **kwargs):
        senderUsername = request.user.username
        receiverUsername = kwargs["receiverUsername"]

        if not self.canDmReceiver(senderUsername, receiverUsername):
            raise PermissionDenied('The receiver needs to accept your request before your can send messages to them.')
        
        if 'chat-message-input' in request.POST:
            room_name = '_'.join(sorted([senderUsername, receiverUsername]))
            print('saving ', request.POST)
            DirectMessage.objects.create(sender=senderUsername, receiver=receiverUsername, room=room_name, content=request.POST['chat-message-input'])

        return HttpResponseRedirect(reverse("chat:conversation", kwargs={"receiverUsername": receiverUsername}))
