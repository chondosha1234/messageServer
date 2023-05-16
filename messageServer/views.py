from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Message, Group, Conversation
from .serializers import MessageSerializer, GroupSerializer, ConversationSerializer, UserSerializer, LoginSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.core.files.base import ContentFile
from firebase_admin import messaging
import base64

User = get_user_model()


"""
API views related to messages
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    sender_id = request.data.get('sender')
    try:
        sender = User.objects.get(id=sender_id)
    except User.DoesNotExist:
        return Response({'sender': f'User with id {sender_id} does not exist'})

    data = request.data.copy()
    data['sender'] = sender

    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        #Send FCM notifications to all members of group
        conversation_id = request.data.get('conversation')
        conversation = Conversation.objects.get(id=conversation_id)
        members = conversation.group.members.all()
        registration_tokens = [member.fcm_registration_token for member in members]

        title = "New Message(s)"
        body = f"You have new messages!"
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            tokens=registration_tokens
        )
        messaging.send_multicast(message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, conversation_id):
    messages = Message.objects.filter(conversation=conversation_id).order_by('-created_at')
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


"""
API views related to Groups
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    serializer = GroupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except GroupDoesNotExist:
        return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_list(request):
    user = request.user
    groups = user.groups
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_member_list(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesnotExist:
        return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

    members = group.members.all()
    serializer = UserSerializer(members, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_group_picture(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

    base64_image = request.data.get('picture')

    image_data = base64_image.split(';base64,')[-1]
    image_file = ContentFile(base64.b64decode(image_data))
    filename = f"group_{group_id}.jpg"

    group.picture.save(filename, image_file)
    group.save()
    serializer = GroupSerializer(group)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request, group_id, user_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

    try:
        member = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if member not in group.members.all():
        group.members.add(member)
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'User already in group'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_member(request, group_id, user_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

    try:
        member = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if member in group.members.all():
        group.members.remove(member)
        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'User not in group'}, status=status.HTTP_404_NOT_FOUND)


"""
API views related to Conversations
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request, group_id):
    serializer = ConversationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Conversation.DoesNotExist:
        return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_list(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

    conversations = group.conversations.all()
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_conversation_picture(request, conversation_id):
    pass


"""
API views related to Users and friends
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request, user_id):
    try:
        friend = User.objects.get(id=user_id)
        user = request.user
        user.friends.add(friend)
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_friend(request, user_id):
    try:
        friend = User.objects.get(id=user_id)
        user = request.user
        if friend in user.friends.all():
            user.friends.remove(friend)
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': f'{friend.username} is not in friends list'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_friends_list(request):
    user = request.user
    friends = user.friends.all()

    if friends is not None:
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'An error occurred while checking the friends list'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = []


@api_view(['GET'])
def get_user(request, user_id):
    try:
        friend = User.objects.get(id=user_id)
        user = request.user
        user.friends.add(friend)
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    if user:
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_profile_picture(request):
    pass


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_fcm_token(request):
    user = request.user
    token = request.get('fcm_token')
    try:
        user.fcm_registration_token = token
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)



class LoginView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):

    permission_classes = (IsAuthenticated)

    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out successfully'})
