from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from messageServer.models import Message, Group, Conversation
from messageServer.serializers import MessageSerializer, GroupSerializer, UserSerializer

User = get_user_model()


class MessageTests(APITestCase):

    def test_send_message(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
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

    def test_get_messages(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)

        conversation = Conversation.objects.create(book_title='test conversation', group=group)
        message1 = Message.objects.create(sender=user, conversation=conversation, text='test message 1')
        message2 = Message.objects.create(sender=user, conversation=conversation, text='test message 2')

        url = reverse('get_messages', args=[conversation.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        #because of order_by latest message is first
        self.assertEqual(response.data[0]['text'], message2.text)
        self.assertEqual(response.data[1]['text'], message1.text)


class UserTests(APITestCase):

    def test_create_user(self):
        self.assertEqual(User.objects.count(), 0)

        data = {
            'email': 'chondosha@example.org',
            'username': 'chondosha',
            'password': 'chondosha5563'
        }
        url = reverse('create_user')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['username'], 'chondosha')
        self.assertEqual(response.data['email'], 'chondosha@example.org')


    def test_login_successful(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        user.set_password('chondosha5563')
        user.save()

        data = {
            'username': 'chondosha',
            'password': 'chondosha5563'
        }
        url = reverse('login')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'chondosha')

    def test_login_invalid_credentials(self):
        data = {
            'username': 'invalid_user',
            'password': 'invalid_password'
        }
        url = reverse('login')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')

    def test_get_current_user(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')
        group.members.add(user)
        group.save()

        url = reverse('get_current_user')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'chondosha')


class FriendsListTests(APITestCase):

    def test_add_friend(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha", password="chondosha5563")
        friend = User.objects.create(email="friend@example.com", username="friend_guy")
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 0)

        url = reverse('add_friend', args=[friend.id])
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.friends.all().count(), 1)
        self.assertEqual(user.friends.first(), friend)

    def test_remove_friends(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha", password="chondosha5563")
        friend = User.objects.create(email="friend@example.com", username="friend_guy")
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
        user = User.objects.create(email="chondosha@example.com", username="chondosha", password="chondosha5563")
        friend1 = User.objects.create(email="friend@example.com", username="friend_guy")
        friend2 = User.objects.create(email="friend2@example.com", username="friend2_guy")
        user.friends.add(friend1)
        user.friends.add(friend2)
        user.save()
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 2)

        url = reverse('get_friends_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_emails = [friend['email'] for friend in response.data]
        self.assertCountEqual(response_emails, [friend1.email, friend2.email])

    def test_get_friends_list_returns_empty_list(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha", password="chondosha5563")
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 0)

        url = reverse('get_friends_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class GroupTests(APITestCase):

    def test_create_group(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
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

    def test_get_group(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')

        url = reverse('get_group', args=[group.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], group.name)

    def test_get_group_list(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        group1 = Group.objects.create(name='test group1')
        group2 = Group.objects.create(name='test group2')
        user.groups.add(group1)
        user.groups.add(group2)
        user.save()

        url = reverse('get_group_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        response_group_names = [group['name'] for group in response.data]
        self.assertCountEqual(response_group_names, [group1.name, group2.name])

    def test_get_member_list(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        other_user = User.objects.create(email="other_guy@example.com", username="other_guy")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')
        group.members.add(user)
        group.members.add(other_user)
        group.save()

        url = reverse('get_member_list', args=[group.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['username'], user.username)
        self.assertEqual(response.data[1]['username'], other_user.username)

    def test_add_member(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha", password="chondosha5563")
        friend = User.objects.create(email="friend@example.com", username="friend_guy")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')
        group.members.add(user)
        group.save()

        self.assertEqual(group.members.all().count(), 1)

        url = reverse('add_member', args=[group.id, friend.id])
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(group.members.all().count(), 2)
        self.assertIn(user, group.members.all())
        self.assertIn(friend, group.members.all())

    def test_remove_member(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha", password="chondosha5563")
        friend = User.objects.create(email="friend@example.com", username="friend_guy")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')
        group.members.add(user)
        group.members.add(friend)
        group.save()

        self.assertEqual(group.members.all().count(), 2)

        url = reverse('remove_member', args=[group.id, friend.id])
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(group.members.all().count(), 1)
        self.assertEqual(group.members.first().username, user.username)
        self.assertEqual(group.members.last().username, user.username)


class ConversationTests(APITestCase):

    def test_create_conversation(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)

        self.assertEqual(Conversation.objects.count(), 0)

        data = {
            'book_title': 'test book',
            'group': group.id
        }
        url = reverse('create_conversation', args=[group.id])
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Conversation.objects.first().book_title, 'test book')

    def test_get_conversation(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')
        conversation = Conversation.objects.create(book_title='test conversation1', group=group)

        url = reverse('get_conversation', args=[conversation.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book_title'], conversation.book_title)

    def test_get_conversation_list(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)

        conversation1 = Conversation.objects.create(book_title='test conversation1', group=group)
        conversation2 = Conversation.objects.create(book_title='test conversation2', group=group)

        self.assertEqual(group.conversations.all().count(), 2)

        url = reverse('get_conversation_list', args=[group.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['book_title'], conversation1.book_title)
        self.assertEqual(response.data[1]['book_title'], conversation2.book_title)
