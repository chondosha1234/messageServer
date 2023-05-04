from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.view import APIView
from .models import Message, Group, Conversation
from .serializers import MessageSerializer, GroupSerializer, ConversationSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout

User = get_user_model()


"""
API views related to messages
"""

@api_view(['POST'])
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_messages(request, conversation_id):
    messages = Message.objects.filter(conversation=conversation_id)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


"""
API views related to Groups
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    pass


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_list(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status = 404)

    groups = user.groups
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


"""
API views related to Conversations
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    pass


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_list(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return Response({'error': 'Group does not exist'}, status = 404)

    conversations = group.conversations.all()
    serialize = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)


"""
API views related to Users and friends
"""

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request):
    pass


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@api_view(['GET'])
def get_user(request):
    pass


class LoginView(APIView):

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # maybe change from 'detail' to something else like home
            return Response({'detail': 'Logged in successfully'})
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):

    permission_classes = (IsAuthenticated)

    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out successfully'})
