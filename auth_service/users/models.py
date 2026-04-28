#/users/sarah/downloads/smart-city-project/auth_service/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    is_citizen = models.BooleanField(default=True)
    is_official = models.BooleanField(default=False)

    def __str__(self):
        return self.username