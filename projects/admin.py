from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Project


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


def approve_projects(modeladmin, request, queryset):
    """Action to approve selected projects"""
    updated = queryset.update(status=Project.STATUS_APPROVED)
    modeladmin.message_user(request, f'{updated} project(s) approved successfully! ✅')

approve_projects.short_description = "✅ Approve selected projects"


def reject_projects(modeladmin, request, queryset):
    """Action to reject selected projects"""
    updated = queryset.update(status=Project.STATUS_REJECTED)
    modeladmin.message_user(request, f'{updated} project(s) rejected successfully! ❌')

reject_projects.short_description = "❌ Reject selected projects"


def mark_pending(modeladmin, request, queryset):
    """Action to mark projects as pending"""
    updated = queryset.update(status=Project.STATUS_PENDING)
    modeladmin.message_user(request, f'{updated} project(s) marked as pending! ⏳')

mark_pending.short_description = "⏳ Mark as pending"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student_name', 'category', 'status_badge', 'created_by', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'student_name', 'description')
    readonly_fields = ('created_by', 'created_at', 'display_description', 'display_status')
    raw_id_fields = ('created_by',)
    actions = [approve_projects, reject_projects, mark_pending]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'student_name', 'roll_number', 'category', 'description')
        }),
        ('Project Link', {
            'fields': ('project_link',)
        }),
        ('Status & Meta', {
            'fields': ('status', 'display_status', 'created_by', 'created_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'approved': '#10b981',
            'pending': '#f59e0b',
            'rejected': '#ef4444',
        }
        color = colors.get(obj.status, '#6b7280')
        emoji = {
            'approved': '✅',
            'pending': '⏳',
            'rejected': '❌',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 6px; font-weight: bold;">{} {}</span>',
            color,
            emoji.get(obj.status, '•'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def display_status(self, obj):
        """Display current status in detail view"""
        emoji = {
            'approved': '✅',
            'pending': '⏳',
            'rejected': '❌',
        }
        return f"{emoji.get(obj.status, '•')} {obj.get_status_display()}"
    display_status.short_description = 'Current Status'
    
    def display_description(self, obj):
        """Display description in detail view"""
        return obj.description
    display_description.short_description = 'Project Description'
