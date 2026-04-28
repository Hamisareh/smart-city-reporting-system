#/notification_service/notification/models.py
from django.db import models
from datetime import datetime

class Notification(models.Model):
    user_id = models.IntegerField()
    report_id = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=50)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification {self.id} for user {self.user_id}"