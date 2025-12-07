from __future__ import annotations
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from typing import List


class User(AbstractUser):
    ROLE_CHOICES = [
        ('producer', 'Produser'),
        ('actor', 'Aktor'),
        ('editor', 'Editor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='actor')
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class ShootingSchedule(models.Model):
    STATUS_CHOICES = [
        ('available', 'Tersedia'),
        ('closed', 'Ditutup'),
        ('completed', 'Selesai'),
    ]

    producer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produced_schedules')
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    script = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self) -> str:
        return f"{self.title} - {self.date} {self.time}"

    def is_tomorrow(self) -> bool:
        today = timezone.localdate()
        return self.date == today + timezone.timedelta(days=1)

    def get_confirmed_actors(self) -> List[User]:
        return [app.actor for app in self.applications.filter(status='confirmed')]

    def get_actors_list(self) -> str:
        return ", ".join(actor.get_full_name() or actor.username for actor in self.get_confirmed_actors())


class ScheduleApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Konfirmasi'),
        ('confirmed', 'Terkonfirmasi'),
        ('rejected', 'Ditolak'),
    ]
    schedule = models.ForeignKey(ShootingSchedule, on_delete=models.CASCADE, related_name='applications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('schedule', 'actor'),)
        ordering = ['-submitted_at']
    def __str__(self):
        return f"{self.actor} pada {self.schedule} ({self.status})"


class SocialMediaTask(models.Model):
    SOCIAL_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
    ]
    
    schedule = models.ForeignKey(ShootingSchedule, on_delete=models.CASCADE, related_name='social_media_tasks')
    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    social_media = models.CharField(max_length=20, choices=SOCIAL_CHOICES)
    caption = models.TextField()
    film_title = models.CharField(max_length=200)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']
        verbose_name = 'Social Media Task'

    def __str__(self) -> str:
        return f"{self.film_title} - {self.get_social_media_display()}"

    def is_overdue(self) -> bool:
        return not self.is_completed and self.due_date < timezone.now()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    schedule = models.ForeignKey(ShootingSchedule, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.message[:40]}"
