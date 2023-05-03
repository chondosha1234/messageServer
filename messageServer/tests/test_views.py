from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from messageServer.models import Message, Group
from messageServer.serializers import MessageSerializer, GroupSerializer

class SendMessageTest(APITestCase):

    def test_send_message(self):
        group = Group.objects.create(name='test group')
        data = {
            'group': group.id,
            'text': 'test message'
        }
        url = reverse('send_message')
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.get().text, 'test message')
        self.assertEqual(Message.objects.get().group, group)


"""
class GetMessagesTests(APITestCase):

    def test_get_messages(self):
        group = Group.objects.create(name='test group')
        message1 = Message.objects.create(group=group, text='test message 1')
        message2 = Message.objects.create(group=group, text='test message 2')
        url = reverse('get_messages', args=[group.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['text'], message1.text)
        self.assertEqual(response.data[1]['text'], message2.text)
"""
