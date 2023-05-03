from rest_framework import serializers
from .models import Message, Group, Conversation


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'conversation', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    pass
