from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from messageServer.models import Message, Group, Conversation
from messageServer.serializers import MessageSerializer, GroupSerializer, UserSerializer
from django.test import override_settings
import base64
import shutil

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
        self.assertEqual(len(response.data['messages']), 2)
        #because of order_by latest message is first,  also the [0][1] is because messages is list and there is ordered dictionary as only element
        self.assertEqual(response.data['messages'][0]['text'], message2.text)
        self.assertEqual(response.data['messages'][1]['text'], message1.text)


@override_settings(MEDIA_ROOT='media_test')
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
        self.assertEqual(response.data['users'][0]['username'], 'chondosha')
        self.assertEqual(response.data['users'][0]['email'], 'chondosha@example.org')


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
        self.assertTrue('token' in response.data)
        self.assertTrue(isinstance(response.data['token']['key'], str))

        token_key = response.data['token']['key']
        token = Token.objects.get(key=token_key)
        self.assertEqual(token.user, user)

    def test_login_after_user_created_by_view(self):
        data = {
            'email': 'chondosha@example.org',
            'username': 'chondosha',
            'password': 'chondosha5563'
        }
        url = reverse('create_user')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['users'][0]['username'], 'chondosha')
        self.assertEqual(response.data['users'][0]['email'], 'chondosha@example.org')

        data = {
            'username': 'chondosha',
            'password': 'chondosha5563'
        }
        url = reverse('login')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue(isinstance(response.data['token']['key'], str))

        user = User.objects.first()
        token_key = response.data['token']['key']
        token = Token.objects.get(key=token_key)
        self.assertEqual(token.user, user)

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
        self.assertEqual(response.data['users'][0]['username'], 'chondosha')

    def test_search_user_returns_user(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        other = User.objects.create(email="other@example.com", username="other_guy")

        data = {
            'query': 'other_guy'
        }
        url = reverse('search_users')
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['users'][0]['username'], 'other_guy')

    def test_search_does_not_return_current_user(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)

        data = {
            'query': 'chondosha'
        }
        url = reverse('search_users')
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 0)

    def test_partial_search_returns_user(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        other = User.objects.create(email="other@example.com", username="other_guy")

        data = {
            'query': 'other'
        }
        url = reverse('search_users')
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['users'][0]['username'], 'other_guy')

    def test_search_returns_multiple_users(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        other1 = User.objects.create(email="other1@example.com", username="other1_guy")
        other2 = User.objects.create(email="other2@example.com", username="other2_guy")

        data = {
            'query': 'other'
        }
        url = reverse('search_users')
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 2)

    def test_set_profile_picture(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)

        with open('messageServer/tests/images/daffodil.jpg', 'rb') as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data = {
            'picture': base64_image
        }
        url = reverse('set_profile_picture')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['users'][0]['username'], 'chondosha')

        shutil.rmtree('media_test/user_pictures', ignore_errors=True)


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
        response_emails = [friend['email'] for friend in response.data['users']]
        self.assertCountEqual(response_emails, [friend1.email, friend2.email])

    def test_get_friends_list_returns_empty_list(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha", password="chondosha5563")
        self.client.force_authenticate(user=user)

        self.assertEqual(user.friends.all().count(), 0)

        url = reverse('get_friends_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['users'], [])


@override_settings(MEDIA_ROOT='media_test')
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

    def test_create_group_adds_creator_as_member(self):
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
        self.assertEqual(Group.objects.first().members.count(), 1)
        self.assertEqual(Group.objects.first().members.first().username, 'chondosha')

    def test_get_group(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')

        url = reverse('get_group', args=[group.id])
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['groups'][0]['name'], group.name)

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
        self.assertEqual(len(response.data['groups']), 2)
        response_group_names = [group['name'] for group in response.data['groups']]
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
        self.assertEqual(len(response.data['users']), 2)
        response_titles = [user['username'] for user in response.data['users']]
        self.assertCountEqual(response_titles, [user.username, other_user.username])

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

    def test_set_group_picture(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')

        with open('messageServer/tests/images/daffodil.jpg', 'rb') as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data = {
            'picture': base64_image
        }
        url = reverse('set_group_picture', args=[group.id])
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['groups'][0]['name'], 'test group')

        shutil.rmtree('media_test/group_pictures', ignore_errors=True)


@override_settings(MEDIA_ROOT='media_test')
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
        url = reverse('create_conversation')
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
        self.assertEqual(response.data['conversations'][0]['book_title'], conversation.book_title)

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
        self.assertEqual(len(response.data['conversations']), 2)
        response_titles = [conversation['book_title'] for conversation in response.data['conversations']]
        self.assertCountEqual(response_titles, [conversation1.book_title, conversation2.book_title])

    def test_set_conversation_picture(self):
        user = User.objects.create(email="chondosha@example.com", username="chondosha")
        self.client.force_authenticate(user=user)
        group = Group.objects.create(name='test group')
        conversation = Conversation.objects.create(book_title='test conversation', group=group)

        with open('messageServer/tests/images/daffodil.jpg', 'rb') as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data = {
            'picture': base64_image
        }
        url = reverse('set_conversation_picture', args=[conversation.id])
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['conversations'][0]['book_title'], 'test conversation')

        shutil.rmtree('media_test/conversation_pictures', ignore_errors=True)
