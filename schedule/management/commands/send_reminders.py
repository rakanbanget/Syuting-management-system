from __future__ import annotations
from django.core.management.base import BaseCommand
from django.utils import timezone
from schedule.models import ShootingSchedule, ScheduleApplication, Notification


class Command(BaseCommand):
    help = 'Send reminder notifications for tomorrow\'s confirmed applications.'

    def handle(self, *args, **options):
        tomorrow = timezone.localdate() + timezone.timedelta(days=1)
        # Ambil aplikasi yang terkonfirmasi untuk jadwal besok (jadwal belum completed)
        apps = ScheduleApplication.objects.select_related('schedule', 'actor').filter(
            status='confirmed',
            schedule__date=tomorrow,
        )
        count = 0
        for app in apps:
            s = app.schedule
            if s.status == 'completed':
                continue
            msg = f"Reminder: Besok ada syuting '{s.title}' jam {s.time} di {s.location}"
            Notification.objects.create(user=app.actor, schedule=s, message=msg)
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Reminders created: {count}'))
