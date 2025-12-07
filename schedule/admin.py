from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, ShootingSchedule, Notification, ScheduleApplication, SocialMediaTask


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')


@admin.register(ShootingSchedule)
class ShootingScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'status', 'producer', 'location')
    list_filter = ('status', 'date')
    search_fields = ('title', 'location', 'producer__username', 'producer__first_name', 'producer__last_name')
    autocomplete_fields = ('producer',)


@admin.register(ScheduleApplication)
class ScheduleApplicationAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'actor', 'status', 'submitted_at', 'responded_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('schedule__title', 'actor__username', 'actor__first_name', 'actor__last_name')


@admin.register(SocialMediaTask)
class SocialMediaTaskAdmin(admin.ModelAdmin):
    list_display = ('film_title', 'social_media', 'editor', 'due_date', 'is_completed')
    list_filter = ('social_media', 'is_completed', 'due_date', 'schedule')
    search_fields = ('film_title', 'caption', 'schedule__title', 'editor__username')
    autocomplete_fields = ('schedule', 'editor')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message', 'schedule__title')
