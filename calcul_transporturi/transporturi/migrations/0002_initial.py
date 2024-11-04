# Generated by Django 5.1.1 on 2024-09-30 19:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('transporturi', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transport',
            name='transporters',
            field=models.ManyToManyField(limit_choices_to={'user_type': 'Transportator'}, related_name='transport_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]