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
        conversation = Conversation.objects.create(book_title='test conversation', group=group)
        message1 = Message.objects.create(sender=user, conversation=conversation, text='test message 1')
        message2 = Message.objects.create(sender=user, conversation=conversation, text='test message 2')

        url = reverse('get_messages', args=[conversation.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['text'], message1.text)
        self.assertEqual(response.data[1]['text'], message2.text)


class FriendsListTest(APITestCase):

    def test_add_friend(self):
        user = User.objects.create(email="chondosha@example.com", name="chondosha")
        friend = User.objects.create(email="friend@example.com", name="friend_guy")

        self.assertEqual(user.friends.all().count(), 0)

        url = reverse('add_friend', args=[friend.id])
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.friends.all().count(), 1)
        self.assertEqual(response.data[0], friend)
