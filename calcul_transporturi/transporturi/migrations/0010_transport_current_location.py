# Generated by Django 5.1.1 on 2024-10-02 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporturi', '0009_transport_is_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='current_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
