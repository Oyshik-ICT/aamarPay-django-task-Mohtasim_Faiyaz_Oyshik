from django.contrib import admin
from .models import FileUpload, ActivityLog

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'upload_time', 'status', 'word_count']
    list_filter = ['status', 'upload_time']
    search_fields = ['filename', 'user__username']

    def has_delete_permission(self, request, obj = None):
        return False
    def has_change_permission(self, request, obj = None):
        return False
    
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'metadata', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'action']

    def has_delete_permission(self, request, obj = None):
        return False
    def has_change_permission(self, request, obj = None):
        return False