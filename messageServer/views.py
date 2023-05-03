from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Message, Group, Conversation
from .serializers import MessageSerializer, GroupSerializer, ConversationSerializer


@api_view(['POST'])
def send_message(request):
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_messages(request, group_id):
    messages = Message.objects.filter(group=group_id)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request):
    pass
