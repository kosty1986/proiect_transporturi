# Generated by Django 5.1.1 on 2024-09-30 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporturi', '0004_transport_selected_transporter'),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='is_allocated',
            field=models.BooleanField(default=False),
        ),
    ]