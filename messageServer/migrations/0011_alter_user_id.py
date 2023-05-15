# Generated by Django 4.2 on 2023-05-12 22:01

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('messageServer', '0010_conversation_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]