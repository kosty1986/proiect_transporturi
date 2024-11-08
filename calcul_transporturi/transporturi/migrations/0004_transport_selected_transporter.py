# Generated by Django 5.1.1 on 2024-09-30 21:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporturi', '0003_remove_transport_price_transportprice'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='selected_transporter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='selected_transports', to=settings.AUTH_USER_MODEL),
        ),
    ]
