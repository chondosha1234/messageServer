from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from messageServer.models import Message, Group, Conversation
from messageServer.serializers import MessageSerializer, GroupSerializer, UserSerializer

User = get_user_model()


class SendMessageTest(APITestCase):

    def test_send_message(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create(email="chondosha@example.com", name="chondosha")
        self.client.force_authenticate(user=user)

        conversation = Conversation.objects.create(book_title='test conversation', group=group)
        data = {
            'sender': user.id,
            'conversation': conversation.id,
            'text': 'test message'
        }

        url = reverse('send_message')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.get().text, 'test message')
        self.assertEqual(Message.objects.get().conversation, conversation)


class GetMessagesTests(APITestCase):

    def test_get_messages(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create(email="chondosha@example.com", name="chondosha")
        self.client.force_authenticate(user=user)

        conversation = Conversation.objects.create(book_title='test conversation', group=group)
        message1 = Message.objects.create(sender=user, conversation=conversation, text='test message 1')
        message2 = Message.objects.create(sender=user, conversation=conversation, text='test message 2')

        url = reverse('get_messages', args=[conversation.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['text'], message1.text)
        self.assertEqual(response.data[1]['text'], message2.text)


class UserTests(APITestCase):
    pass

class FriendsListTests(APITestCase):

    def test_add_friend(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha", password="chondosha5563")
        friend = User.objects.create(email="friend@example.com", name="friend_guy")
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 0)

        url = reverse('add_friend', args=[friend.id])
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.friends.all().count(), 1)
        self.assertEqual(user.friends.first(), friend)

    def test_remove_friends(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha", password="chondosha5563")
        friend = User.objects.create(email="friend@example.com", name="friend_guy")
        user.friends.add(friend)
        user.save()
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 1)
        self.assertEqual(user.friends.first(), friend)

        url = reverse('remove_friend', args=[friend.id])
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.friends.all().count(), 0)

    def test_get_friends_list(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha", password="chondosha5563")
        friend1 = User.objects.create(email="friend@example.com", name="friend_guy")
        friend2 = User.objects.create(email="friend2@example.com", name="friend2_guy")
        user.friends.add(friend1)
        user.friends.add(friend2)
        user.save()
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 2)

        url = reverse('get_friends_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['email'], friend1.email)
        self.assertEqual(response.data[1]['email'], friend2.email)

    def test_get_friends_list_returns_empty_list(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha", password="chondosha5563")
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 0)

        url = reverse('get_friends_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class GroupTests(APITestCase):

    def test_create_group(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha")
        self.client.force_authenticate(user=user)

        self.assertEqual(Group.objects.count(), 0)

        data = {
            'name': 'test group'
        }
        url = reverse('create_group')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 1)
        self.assertEqual(Group.objects.first().name, 'test group')

    def test_get_group_list(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha")
        self.client.force_authenticate(user=user)
        group1 = Group.objects.create(name='test group1')
        group2 = Group.objects.create(name='test group2')
        user.groups.add(group1)
        user.groups.add(group2)
        user.save()

        url = reverse('get_group_list', args=[user.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], group1.name)
        self.assertEqual(response.data[1]['name'], group2.name)

    def test_get_member_list(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha")
        other_user = User.objects.create(email="other_guy@example.com", name="other_guy")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')
        group.members.add(user)
        group.members.add(other_user)
        group.save()

        url = reverse('get_member_list', args=[group.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], user.name)
        self.assertEqual(response.data[1]['name'], other_user.name)


class ConversationTests(APITestCase):

    def test_create_conversation(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create(email="chondosha@example.com", name="chondosha")
        self.client.force_authenticate(user=user)

        self.assertEqual(Conversation.objects.count(), 0)

        data = {
            'book_title': 'test book',
            'group': group.id
        }
        url = reverse('create_conversation')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Conversation.objects.first().book_title, 'test book')
