# Generated by Django 5.1.1 on 2024-10-02 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporturi', '0008_transport_nr_masina'),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]