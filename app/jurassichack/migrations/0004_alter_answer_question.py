# Generated by Django 3.2.25 on 2025-01-09 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jurassichack', '0003_auto_20250106_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='question', to='jurassichack.question'),
        ),
    ]
