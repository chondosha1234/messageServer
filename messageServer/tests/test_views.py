from django.url import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Message, Group
from .serializers import MessageSerializer, GroupSerializer

class SendMessageTest(APITestCase):

    def test_send_message(self):
        group = Group.objects.create(name='test group')
        data = {
            'group': group.id,
            'text': 'test message'
        }
        url = reverse('send_message')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.get().text, 'test message')
        self.assertEqual(Message.objects.get().group, group)
