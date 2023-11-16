from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import DirectMessage, DirectMessagePermission, Permission

User = get_user_model()


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.edu", password="testpassword"
        )

    @classmethod
    def tearDownClass(cls):
        # Clean up any test-specific data
        super().tearDownClass()


class ConversationHomeViewTest(ViewsTestCase):
    def setUp(self):
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.edu", password="testpassword"
        )

    def test_conversation_home_view_unauthenticated_user_GET(self):
        response = self.client.get(
            reverse("chat:conversation_home"),
            {
                "cur_username": self.user.username,
                'pending_connections': [],
                'active_connections': [],
                'requested_connections': [],
                'blocked_connections': [],
            },
            follow=True,
        )
        self.assertRedirects(
            response, expected_url=reverse("rrapp:login"), status_code=302
        )

    def test_conversation_home_view_authenticated_user_GET(self):
        self.client.force_login(self.user)
        user3 = User.objects.create_user(
            username="testuser3", email="test3@example.edu", password="testpassword"
        )
        user4 = User.objects.create_user(
            username="testuser4", email="test4@example.edu", password="testpassword"
        )
        user5 = User.objects.create_user(
            username="testuser5", email="test5@example.edu", password="testpassword"
        )
        DirectMessagePermission.objects.create(
            sender=self.user2.username,
            receiver=self.user.username,
            permission=Permission.REQUESTED,
        )
        all_pending_connection_usernamesids = [
            {
                'id': self.user2.id,
                'username': self.user2.username,
            }
        ]
        DirectMessagePermission.objects.create(
            sender=user3.username,
            receiver=self.user.username,
            permission=Permission.ALLOWED,
        )
        all_active_connection_usernamesids = [
            {
                'id': user3.id,
                'username': user3.username,
            }
        ]
        DirectMessagePermission.objects.create(
            sender=self.user.username,
            receiver=user4.username,
            permission=Permission.REQUESTED,
        )
        all_requested_connection_usernamesids = [
            {
                'id': user4.id,
                'username': user4.username,
            }
        ]
        DirectMessagePermission.objects.create(
            sender=self.user.username,
            receiver=user5.username,
            permission=Permission.BLOCKED,
        )
        all_blocked_connection_usernamesids = [
            {
                'id': user5.id,
                'username': user5.username,
            }
        ]
        response = self.client.get(
            reverse("chat:conversation_home"),
            {
                "cur_username": self.user.username,
                'pending_connections': all_pending_connection_usernamesids,
                'active_connections': all_active_connection_usernamesids,
                'requested_connections': all_requested_connection_usernamesids,
                'blocked_connections': all_blocked_connection_usernamesids,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/conversation_home.html")

    def test_conversation_home_view_authenticated_user_POST_accept(self):
        self.client.force_login(self.user)
        DirectMessagePermission.objects.create(
            sender=self.user2.username,
            receiver=self.user.username,
            permission=Permission.REQUESTED,
        )
        response = self.client.post(
            reverse(
                "chat:conversation_home",
            ),
            {
                "connection_accept": self.user2.username,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DirectMessagePermission.objects.filter(
                sender=self.user2.username,
                receiver=self.user.username,
                permission=Permission.ALLOWED,
            ).exists()
        )

    def test_conversation_home_view_authenticated_user_POST_reject(self):
        self.client.force_login(self.user)
        DirectMessagePermission.objects.create(
            sender=self.user2.username,
            receiver=self.user.username,
            permission=Permission.REQUESTED,
        )
        response = self.client.post(
            reverse(
                "chat:conversation_home",
            ),
            {
                "connection_reject": self.user2.username,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            not DirectMessagePermission.objects.filter(
                sender=self.user2.username,
                receiver=self.user.username,
                permission=Permission.REQUESTED,
            ).exists()
        )

    def test_conversation_home_view_authenticated_user_POST_withdraw(self):
        self.client.force_login(self.user)
        DirectMessagePermission.objects.create(
            sender=self.user.username,
            receiver=self.user2.username,
            permission=Permission.REQUESTED,
        )
        response = self.client.post(
            reverse(
                "chat:conversation_home",
            ),
            {
                "connection_withdraw": self.user2.username,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            not DirectMessagePermission.objects.filter(
                sender=self.user.username,
                receiver=self.user2.username,
                permission=Permission.REQUESTED,
            ).exists()
        )

    def test_conversation_home_view_authenticated_user_POST_unblock(self):
        self.client.force_login(self.user)
        DirectMessagePermission.objects.create(
            sender=self.user2.username,
            receiver=self.user.username,
            permission=Permission.BLOCKED,
        )
        response = self.client.post(
            reverse(
                "chat:conversation_home",
            ),
            {
                "connection_unblock": self.user2.username,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DirectMessagePermission.objects.filter(
                sender=self.user2.username,
                receiver=self.user.username,
                permission=Permission.ALLOWED,
            ).exists()
        )


class ConversationViewTest(ViewsTestCase):
    def setUp(self):
        self.receiverUser = User.objects.create_user(
            username="testuser2", email="test2@example.edu", password="testpassword"
        )
        self.senderUsername = self.user.username
        self.receiverUsername = self.receiverUser.username
        self.permission = DirectMessagePermission.objects.create(
            sender=self.user.username,
            receiver=self.receiverUser.username,
            permission=Permission.ALLOWED,
        )
        self.room_name = '_'.join(sorted([self.senderUsername, self.receiverUsername]))
        self.messages = DirectMessage.objects.create(
            sender=self.senderUsername,
            receiver=self.receiverUsername,
            room=self.room_name,
            content='hello',
        )
        self.receiverUsernameId = {
            "username": self.receiverUsername,
            "id": self.receiverUser.id,
        }

    def test_conversation_view_unauthenticated_user_GET(self):
        recipientPermission = DirectMessagePermission.objects.create(
            sender=self.receiverUsername,
            receiver=self.senderUsername,
            permission=Permission.ALLOWED,
        )
        response = self.client.get(
            reverse("chat:conversation", args=(self.receiverUsername,)),
            {
                'room_name': self.room_name,
                'sender': self.senderUsername,
                'receiver': self.receiverUsernameId,
                'messages': self.messages,
                'recipient_permission': recipientPermission,
            },
        )
        self.assertRedirects(
            response, expected_url=reverse("rrapp:login"), status_code=302
        )

    def test_conversation_view_authenticated_user_GET(self):
        self.client.force_login(self.user)
        recipientPermission = DirectMessagePermission.objects.create(
            sender=self.receiverUsername,
            receiver=self.senderUsername,
            permission=Permission.ALLOWED,
        )
        response = self.client.get(
            reverse("chat:conversation", args=(self.receiverUsername,)),
            {
                'room_name': self.room_name,
                'sender': self.senderUsername,
                'receiver': self.receiverUsernameId,
                'messages': self.messages,
                'recipient_permission': recipientPermission,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/conversation_http.html")

    def test_conversation_view_authenticated_user_POST_chat(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                "chat:conversation",
                args=(self.receiverUsername,),
            ),
            {
                'chat-message-input': 'hello',
                'messages': self.messages,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DirectMessage.objects.filter(
                sender=self.senderUsername,
                receiver=self.receiverUsername,
                room=self.room_name,
                content='hello',
            ).exists()
        )

    def test_conversation_view_authenticated_user_POST_block(self):
        self.client.force_login(self.user)
        recipientPermission = DirectMessagePermission.objects.create(
            sender=self.receiverUsername,
            receiver=self.senderUsername,
            permission=Permission.ALLOWED,
        )
        response = self.client.post(
            reverse(
                "chat:conversation",
                args=(self.receiverUsername,),
            ),
            {
                'room_name': self.room_name,
                'sender': self.senderUsername,
                'receiver': self.receiverUsernameId,
                'messages': self.messages,
                'recipient_permission': recipientPermission,
                'block-user': self.receiverUsername,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DirectMessagePermission.objects.filter(
                sender=self.receiverUsername,
                receiver=self.senderUsername,
                permission=Permission.BLOCKED,
            ).exists()
        )

    def test_conversation_view_authenticated_user_POST_unblock(self):
        self.client.force_login(self.user)
        recipientPermission = DirectMessagePermission.objects.create(
            sender=self.receiverUsername,
            receiver=self.senderUsername,
            permission=Permission.BLOCKED,
        )
        response = self.client.post(
            reverse(
                "chat:conversation",
                args=(self.receiverUsername,),
            ),
            {
                'room_name': self.room_name,
                'sender': self.senderUsername,
                'receiver': self.receiverUsernameId,
                'messages': self.messages,
                'recipient_permission': recipientPermission,
                'unblock-user': self.receiverUsername,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DirectMessagePermission.objects.filter(
                sender=self.receiverUsername,
                receiver=self.senderUsername,
                permission=Permission.ALLOWED,
            ).exists()
        )
