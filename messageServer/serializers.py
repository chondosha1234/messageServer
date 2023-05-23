from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import Message, Group, Conversation
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

logger = logging.getLogger('django')

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ['key']


class GroupSerializer(serializers.ModelSerializer):
    picture_url = serializers.SerializerMethodField()

    def get_picture_url(self, group):
        if group.picture:
            return settings.SITE_URL + group.picture.url
        return None

    class Meta:
        model = Group
        fields = ['id', 'name', 'picture_url']


class UserSerializer(serializers.ModelSerializer):
    picture_url = serializers.SerializerMethodField()

    def get_picture_url(self, user):
        if user.picture:
            return settings.SITE_URL + user.picture.url
        return None

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'picture_url']


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


class ConversationSerializer(serializers.ModelSerializer):
    picture_url = serializers.SerializerMethodField()

    def get_picture_url(self, conversation):
        if conversation.picture:
            return settings.SITE_URL + conversation.picture.url
        return None

    class Meta:
        model = Conversation
        fields = ['id', 'book_title', 'group', 'picture_url']


    def create(self, validated_data):
        logger.info(f"Inside convo serializer create.  validated data: {validated_data}")
        book_title = validated_data.pop('book_title')
        group = validated_data.pop('group')

        conversation = Conversation.objects.create(
            book_title=book_title,
            group=group
        )

        return conversation
