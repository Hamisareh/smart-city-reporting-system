#report_service/reports/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Report(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    description = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')

    user_id = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id}"
        

class ReportImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reports/%Y/%m/%d/')

    def __str__(self):
        return f"Image for Report {self.report.id}"


class StatusHistory(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='history')

    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)

    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.old_status} -> {self.new_status}"       