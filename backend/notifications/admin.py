from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'notification_type', 'is_sent', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_sent', 'is_read')
    search_fields = ('student__user__email', 'job__title')
