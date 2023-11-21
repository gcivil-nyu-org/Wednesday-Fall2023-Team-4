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


def get_pending_connections_count(username):
    try:
        pending_connections_count = DirectMessagePermission.objects.filter(
            Q(receiver__exact=username) & Q(permission__exact=Permission.REQUESTED)
        ).count()
    except DirectMessagePermission.DoesNotExist:
        pending_connections_count = 0

    return pending_connections_count


# def conversation(request, receiverUsername):
#     senderUsername = request.user.username
#     room_name = '_'.join(sorted([senderUsername, receiverUsername]))

#     messages = DirectMessage.objects.filter(room=room_name)[0:25]

#     try:
#         permissions = list(
#             DirectMessagePermission.objects.filter(
#                 Q(sender__exact=senderUsername) | Q(receiver__exact=senderUsername)
#             )
#         )
#     except DirectMessagePermission.DoesNotExist:
#         permissions = [
#             DirectMessagePermission.objects.create(
#                 sender=senderUsername,
#                 receiver=receiverUsername,
#                 permission=Permission.ALLOWED,
#             )
#         ]

#     allowed_usernames = []
#     for p in permissions:
#         if p.sender == senderUsername:
#             allowed_usernames.append(p.receiver)
#         else:
#             allowed_usernames.append(p.sender)

#     return render(
#         request,
#         'chat/conversation.html',
#         {
#             'room_name': room_name,
#             'sender': senderUsername,
#             'receiver': receiverUsername,
#             'messages': messages,
#             'allowed_usernames': allowed_usernames,
#         },
#     )


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
                    'id': p.sender.id,
                    'username': p.sender.username,
                }
            )

        try:
            active_connections = list(
                DirectMessagePermission.objects.filter(
                    Q(sender__exact=cur_username)
                    & Q(permission__exact=Permission.ALLOWED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            active_connections = []

        all_active_connection_usernamesids = []
        for p in active_connections:
            if p.sender.username == cur_username:
                all_active_connection_usernamesids.append(
                    {
                        'id': p.receiver.id,
                        'username': p.receiver.username,
                    }
                )
            else:
                print(p.sender, p.receiver, p.permission, cur_username)
                all_active_connection_usernamesids.append(
                    {'id': p.sender.id, 'username': p.sender.username}
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
                    'id': p.receiver.id,
                    'username': p.receiver.username,
                }
            )

        try:
            blocked_connections = list(
                DirectMessagePermission.objects.filter(
                    Q(receiver__exact=cur_username)
                    & Q(permission__exact=Permission.BLOCKED)
                )
            )
        except DirectMessagePermission.DoesNotExist:
            blocked_connections = []

        all_blocked_connection_usernamesids = []
        for p in blocked_connections:
            all_blocked_connection_usernamesids.append(
                {
                    'id': p.sender.id,
                    'username': p.sender.username,
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
                'blocked_connections': all_blocked_connection_usernamesids,
            },
        )

    def post(self, request, *args, **kwargs):
        if "connection_accept" in request.POST:
            p = DirectMessagePermission.objects.get(
                sender=request.POST["connection_accept"], receiver=request.user.username
            )
            p.permission = Permission.ALLOWED
            p.save()

            DirectMessagePermission.objects.update_or_create(
                defaults={"permission": Permission.ALLOWED},
                receiver=request.POST["connection_accept"],
                sender=request.user.username,
            )
        elif "connection_reject" in request.POST:
            p = DirectMessagePermission.objects.get(
                sender=request.POST["connection_reject"], receiver=request.user.username
            )
            p.delete()
        elif "connection_withdraw" in request.POST:
            p = DirectMessagePermission.objects.get(
                receiver=request.POST["connection_withdraw"],
                sender=request.user.username,
            )
            p.delete()
        elif "connection_unblock" in request.POST:
            DirectMessagePermission.objects.filter(
                sender=request.POST["connection_unblock"],
                receiver=request.user.username,
            ).update(permission=Permission.ALLOWED)
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
                    (
                        Q(sender__exact=senderUsername)
                        & Q(receiver__exact=receiverUsername)
                    )
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
            raise PermissionDenied(
                'The receiver must accept your request before your can message them.'
            )

        # TODO paginate
        messages = DirectMessage.objects.filter(room=room_name)

        # ALLOWED permission exists in DB
        # render the page and handle messages
        receiverUser = User.objects.get(username=receiverUsername)
        receiverUsernameId = {"username": receiverUsername, "id": receiverUser.id}

        try:
            recipientPermission = DirectMessagePermission.objects.get(
                sender=receiverUsername, receiver=senderUsername
            )
        except DirectMessagePermission.DoesNotExist:
            recipientPermission = None

        return render(
            request,
            'chat/conversation_http.html',
            {
                'room_name': room_name,
                'sender': senderUsername,
                'receiver': receiverUsernameId,
                'messages': messages,
                'recipient_permission': recipientPermission,
            },
        )

    def post(self, request, *args, **kwargs):
        senderUsername = request.user.username
        receiverUsername = kwargs["receiverUsername"]
        senderUser = User.objects.get(username=senderUsername)
        receiverUser = User.objects.get(username=receiverUsername)

        if not self.canDmReceiver(senderUsername, receiverUsername):
            raise PermissionDenied(
                'The receiver needs to accept your request before your can send messages to them.'
            )

        if (
            'chat-message-input' in request.POST
            and request.POST['chat-message-input'] != ""
        ):
            room_name = '_'.join(sorted([senderUsername, receiverUsername]))
            print('saving ', request.POST)
            DirectMessage.objects.create(
                sender=senderUser,
                receiver=receiverUser,
                room=room_name,
                content=request.POST['chat-message-input'],
            )

        if 'block-user' in request.POST:
            # receiver should not be able to contact cur_user
            # print('blocking', receiverUsername, '-->', senderUsername)
            DirectMessagePermission.objects.filter(
                sender=receiverUser, receiver=senderUser
            ).update(permission=Permission.BLOCKED)
            return HttpResponseRedirect(reverse("chat:conversation_home"))

        if 'unblock-user' in request.POST:
            # receiver should be able to contact cur_user
            # print('unblocking', receiverUsername, '-->', senderUsername)
            DirectMessagePermission.objects.filter(
                sender=receiverUser, receiver=senderUser
            ).update(permission=Permission.ALLOWED)

        return HttpResponseRedirect(
            reverse("chat:conversation", kwargs={"receiverUsername": receiverUsername})
        )
