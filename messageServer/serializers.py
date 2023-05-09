from rest_framework import serializers
from .models import Message, Group, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'sender', 'conversation', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        sender = validated_data.pop('sender')
        conversation = validated_data.pop('conversation')
        text = validated_data.pop('text')

        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            text=text
        )

        return message


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conversation
        fields = '__all__'

    def create(self, validated_data):
        book_title = validated_data.pop('book_title')
        group = validated_data.pop('group')

        conversation = Conversation.objects.create(
            book_title=book_title,
            group=group
        )

        return conversation
