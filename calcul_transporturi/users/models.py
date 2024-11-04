from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from .constants import TOKEN_LIFETIME

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('Transportator', 'Transportator'),
        ('Client', 'Client'),
        ('Staff', 'Staff'),
    )

    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default='Client')
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    token_used = models.BooleanField(default=False)
    token_created = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)

    def is_token_valid(self):
        return self.token_created >= timezone.now() - TOKEN_LIFETIME


