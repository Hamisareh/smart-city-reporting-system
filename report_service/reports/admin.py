#report_service/report/admin.py

from django.contrib import admin
from .models import Category, Report, ReportImage, StatusHistory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'description', 'status', 'priority', 'user_id', 'category', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['description']
    readonly_fields = ['created_at']

@admin.register(ReportImage)
class ReportImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'image']

@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'old_status', 'new_status', 'changed_at']
    readonly_fields = ['changed_at']
