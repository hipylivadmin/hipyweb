# Generated by Django 3.2.23 on 2024-02-10 15:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('front', '0021_registration_present'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('question_success', models.TextField()),
                ('image', models.FileField(blank=True, null=True, upload_to='questions/')),
                ('function_name', models.CharField(blank=True, max_length=200, null=True)),
                ('reddit', models.URLField(blank=True, null=True)),
                ('resources', models.URLField(blank=True, null=True)),
                ('puzzle_input', models.BooleanField(default=True)),
                ('next', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next_question', to='lifesci.question')),
                ('previous', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lifesci.question')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='lifesci.question')),
            ],
        ),
        migrations.CreateModel(
            name='Human',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('anonymous_user', models.BooleanField(default=False)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='life_sci_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correct', models.BooleanField(default=False)),
                ('time_submitted', models.DateTimeField(auto_now_add=True)),
                ('score', models.IntegerField(default=0)),
                ('submitted', models.BigIntegerField(default=0)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='life_sci_event', to='front.event')),
                ('human', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lifesci.human')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lifesci.question')),
            ],
        ),
    ]
