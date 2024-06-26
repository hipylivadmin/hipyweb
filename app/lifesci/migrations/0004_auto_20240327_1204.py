# Generated by Django 3.2.24 on 2024-03-27 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lifesci', '0003_question_example_answer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PeerReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pass_peer', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('feedback', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PreloadedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField()),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='preloaded_user',
        ),
        migrations.RenameField(
            model_name='answer',
            old_name='score',
            new_name='answer_score',
        ),
        migrations.AddField(
            model_name='answer',
            name='figure_pass',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='answer',
            name='figure_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='answer',
            name='peer_feedback',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='peer_reviewed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='human',
            name='student_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='figure_rubric',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='peerreview',
            name='answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewed_answer', to='lifesci.answer'),
        ),
        migrations.AddField(
            model_name='peerreview',
            name='human',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewer', to='lifesci.human'),
        ),
        migrations.AddField(
            model_name='collaboration',
            name='collaborator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='human_collaborator', to='lifesci.human'),
        ),
        migrations.AddField(
            model_name='collaboration',
            name='human',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='human_colab', to='lifesci.human'),
        ),
        migrations.AddField(
            model_name='collaboration',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='collaboration_question', to='lifesci.question'),
        ),
    ]
