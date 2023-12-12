from django.shortcuts import render
from django.db.models import Q
from django.views import generic

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from rrapp.models import Quiz, User
from .models import DirectMessage, DirectMessagePermission, Permission


class ConversationWsView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("rrapp:login"))
        # else process dispatch as it otherwise normally would
        return super(ConversationWsView, self).dispatch(request, *args, **kwargs)

    def canDmReceiver(self, senderUsername, receiverUsername):
        permissions = list(
            DirectMessagePermission.objects.filter(
                (Q(sender__exact=senderUsername) & Q(receiver__exact=receiverUsername))
            )
        )

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
                sender=receiverUser, receiver=request.user
            )
        except DirectMessagePermission.DoesNotExist:
            recipientPermission = None

        return render(
            request,
            'chat/conversation.html',
            {
                'room_name': room_name,
                'sender': senderUsername,
                'receiver': receiverUsernameId,
                'messages': messages,
                'recipient_permission': recipientPermission,
                'target_user': receiverUser,
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

        pending_connections = list(
            DirectMessagePermission.objects.filter(
                Q(receiver__exact=cur_username)
                & Q(permission__exact=Permission.REQUESTED)
            )
        )

        all_pending_connection_usernamesids = []
        for p in pending_connections:
            all_pending_connection_usernamesids.append(
                {
                    'id': p.sender.id,
                    'username': p.sender.username,
                    'matchLevel': self.calculateMatchLevel(
                        cur_username, p.sender.username
                    ),
                }
            )
        all_pending_connection_usernamesids = sorted(
            all_pending_connection_usernamesids,
            key=lambda x: x['matchLevel'],
            reverse=True,
        )

        active_connections = list(
            DirectMessagePermission.objects.filter(
                Q(sender__exact=cur_username) & Q(permission__exact=Permission.ALLOWED)
            )
        )

        all_active_connection_usernamesids = []
        for p in active_connections:
            all_active_connection_usernamesids.append(
                {
                    'id': p.receiver.id,
                    'username': p.receiver.username,
                }
            )

        requested_connections = list(
            DirectMessagePermission.objects.filter(
                Q(sender__exact=cur_username)
                & Q(permission__exact=Permission.REQUESTED)
            )
        )

        all_requested_connection_usernamesids = []
        for p in requested_connections:
            all_requested_connection_usernamesids.append(
                {
                    'id': p.receiver.id,
                    'username': p.receiver.username,
                }
            )

        blocked_connections = list(
            DirectMessagePermission.objects.filter(
                Q(receiver__exact=cur_username)
                & Q(permission__exact=Permission.BLOCKED)
            )
        )

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
            otherUser = User.objects.get(username=request.POST["connection_accept"])
            p = DirectMessagePermission.objects.get(
                sender=otherUser, receiver=request.user
            )
            p.permission = Permission.ALLOWED
            p.save()

            DirectMessagePermission.objects.update_or_create(
                defaults={"permission": Permission.ALLOWED},
                receiver=otherUser,
                sender=request.user,
            )
        elif "connection_reject" in request.POST:
            otherUser = User.objects.get(username=request.POST["connection_reject"])
            p = DirectMessagePermission.objects.get(
                sender=otherUser, receiver=request.user
            )
            p.delete()
        elif "connection_withdraw" in request.POST:
            otherUser = User.objects.get(username=request.POST["connection_withdraw"])
            p = DirectMessagePermission.objects.get(
                receiver=otherUser,
                sender=request.user,
            )
            p.delete()
        elif "connection_unblock" in request.POST:
            otherUser = User.objects.get(username=request.POST["connection_unblock"])
            DirectMessagePermission.objects.filter(
                sender=otherUser,
                receiver=request.user.username,
            ).update(permission=Permission.ALLOWED)
        else:
            pass

        return HttpResponseRedirect(reverse("chat:conversation_home"))

    def calculateMatchLevel(self, cur_username, target_username):
        cur_user = User.objects.get(username=cur_username)
        target_user = User.objects.get(username=target_username)
        cur_quiz, created_cur = Quiz.objects.get_or_create(user=cur_user)
        target_quiz, created_tar = Quiz.objects.get_or_create(user=target_user)

        match_level = 0

        if created_tar:
            return

        for i in range(1, 9):
            cur_field = "question" + str(i)
            if not getattr(target_quiz, cur_field, None):
                print("Rentee quiz have not been filled")
                return
            elif not getattr(cur_quiz, cur_field, None):
                print("Renter quiz have not been filled")
                return -1  # Ask the renter to fill the quiz
            else:
                num_choices = len(cur_quiz._meta.get_field(cur_field).choices)
                value_cur = getattr(cur_quiz, cur_field)
                value_target = getattr(target_quiz, cur_field)
                cur_level = 1 - (abs(value_cur - value_target) / (num_choices - 1))
                match_level += cur_level
        return int(match_level / 8 * 100)


class ConversationHttpView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to
        # access the register page while logged in
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("rrapp:login"))
        # else process dispatch as it otherwise normally would
        return super(ConversationHttpView, self).dispatch(request, *args, **kwargs)

    def canDmReceiver(self, senderUsername, receiverUsername):
        permissions = list(
            DirectMessagePermission.objects.filter(
                (Q(sender__exact=senderUsername) & Q(receiver__exact=receiverUsername))
            )
        )

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
                sender=receiverUser, receiver=request.user
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
