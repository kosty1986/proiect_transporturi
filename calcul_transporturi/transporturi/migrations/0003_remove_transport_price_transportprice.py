# Generated by Django 5.1.1 on 2024-09-30 20:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporturi', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transport',
            name='price',
        ),
        migrations.CreateModel(
            name='TransportPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='transporturi.transport')),
                ('transporter', models.ForeignKey(limit_choices_to={'user_type': 'Transportator'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
