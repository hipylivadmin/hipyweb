# Generated by Django 3.2.25 on 2025-01-10 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jurassichack', '0005_alter_answer_next_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='function_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
    ]