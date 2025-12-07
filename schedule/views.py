from __future__ import annotations
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import RegistrationForm, LoginForm, ShootingScheduleForm
from .models import ShootingSchedule, ScheduleApplication, SocialMediaTask, User, Notification


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registrasi berhasil. Silakan login.')
            return redirect('login')
        else:
            messages.error(request, 'Periksa kembali form Anda.')
    else:
        form = RegistrationForm()
    return render(request, 'schedule/register.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Login berhasil.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah.')
    else:
        form = LoginForm()
    return render(request, 'schedule/login.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, 'Anda telah logout.')
    return redirect('login')


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role == 'producer':
        return redirect('producer_dashboard')
    elif user.role == 'editor':
        return redirect('editor_dashboard')
    return redirect('actor_my_schedules')


@login_required
def producer_dashboard(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'producer':
        return HttpResponseForbidden('Hanya produser yang dapat mengakses halaman ini.')
    schedules = (
        ShootingSchedule.objects
        .filter(producer=user)
        .order_by('date', 'time')
        .prefetch_related('applications__actor')
    )
    tomorrow = timezone.localdate() + timezone.timedelta(days=1)
    # Reminders for confirmed applications only
    reminders = []
    for s in schedules:
        if s.date == tomorrow and any(app.status == 'confirmed' for app in s.applications.all()):
            reminders.append(s)
    return render(request, 'schedule/producer_dashboard.html', {
        'schedules': schedules,
        'reminders': reminders,
    })


@login_required
def actor_dashboard(request: HttpRequest) -> HttpResponse:
    # Backwards compatibility: redirect to "Jadwal Saya"
    return redirect('actor_my_schedules')


@login_required
def actor_my_schedules(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'actor':
        return HttpResponseForbidden('Hanya aktor yang dapat mengakses halaman ini.')
    my_apps = ScheduleApplication.objects.filter(actor=user).select_related("schedule").order_by("-submitted_at")
    tomorrow = timezone.localdate() + timezone.timedelta(days=1)
    reminders = [app.schedule for app in my_apps if app.status == 'confirmed' and app.schedule.date == tomorrow]
    return render(request, 'schedule/actor_my_schedules.html', {
        'my_applications': my_apps,
        'reminders': reminders,
    })


@login_required
def actor_available_schedules(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'actor':
        return HttpResponseForbidden('Hanya aktor yang dapat mengakses halaman ini.')
    # Jadwal available, dan user BELUM punya ScheduleApplication apapun untuk jadwal itu
    all_available = ShootingSchedule.objects.filter(status='available')
    already_applied = ScheduleApplication.objects.filter(actor=user).values_list('schedule_id', flat=True)
    available_schedules = all_available.exclude(id__in=already_applied)
    tomorrow = timezone.localdate() + timezone.timedelta(days=1)
    reminders = []  # reminders hanya di page my schedule
    return render(request, 'schedule/actor_available_schedules.html', {
        'available_schedules': available_schedules,
        'reminders': reminders,
    })


@login_required
def create_schedule(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'producer':
        return HttpResponseForbidden('Hanya produser yang dapat membuat jadwal.')
    if request.method == 'POST':
        form = ShootingScheduleForm(request.POST)
        if form.is_valid():
            schedule: ShootingSchedule = form.save(commit=False)
            schedule.producer = user
            schedule.status = 'available'
            schedule.save()
            messages.success(request, 'Jadwal berhasil dibuat.')
            return redirect('producer_dashboard')
        else:
            messages.error(request, 'Periksa kembali form Anda.')
    else:
        form = ShootingScheduleForm()
    return render(request, 'schedule/create_schedule.html', {'form': form})


@login_required
def edit_schedule(request: HttpRequest, pk: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    schedule = get_object_or_404(ShootingSchedule, pk=pk)
    if user.role != 'producer' or schedule.producer_id != user.id:
        return HttpResponseForbidden('Tidak memiliki izin untuk mengedit jadwal ini.')
    if request.method == 'POST':
        form = ShootingScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jadwal berhasil diperbarui.')
            return redirect('producer_dashboard')
        else:
            messages.error(request, 'Periksa kembali form Anda.')
    else:
        form = ShootingScheduleForm(instance=schedule)
    return render(request, 'schedule/edit_schedule.html', {'form': form, 'schedule': schedule})


@login_required
def delete_schedule(request: HttpRequest, pk: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    schedule = get_object_or_404(ShootingSchedule, pk=pk)
    if user.role != 'producer' or schedule.producer_id != user.id:
        return HttpResponseForbidden('Tidak memiliki izin untuk menghapus jadwal ini.')
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Jadwal berhasil dihapus.')
        return redirect('producer_dashboard')
    return render(request, 'schedule/confirm_delete.html', {'schedule': schedule})


@login_required
def complete_schedule(request: HttpRequest, pk: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    schedule = get_object_or_404(ShootingSchedule, pk=pk)
    if user.role != 'producer' or schedule.producer_id != user.id:
        return HttpResponseForbidden('Tidak memiliki izin untuk menandai selesai.')
    schedule.status = 'completed'
    schedule.save(update_fields=['status'])
    messages.success(request, 'Jadwal ditandai sebagai selesai.')
    return redirect('producer_dashboard')


@login_required
def join_schedule(request: HttpRequest, pk: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'actor':
        return HttpResponseForbidden('Hanya aktor yang dapat mengajukan jadwal.')
    schedule = get_object_or_404(ShootingSchedule, pk=pk)
    # Cek sudah apply
    existing = ScheduleApplication.objects.filter(schedule=schedule, actor=user).first()
    if existing:
        messages.info(request, 'Anda sudah pernah mengajukan ke jadwal ini.')
        return redirect('actor_my_schedules')
    if schedule.status != 'available':
        messages.error(request, 'Pendaftaran jadwal sudah ditutup atau selesai.')
        return redirect('actor_available_schedules')
    ScheduleApplication.objects.create(schedule=schedule, actor=user, status='pending')
    Notification.objects.create(user=schedule.producer, schedule=schedule, message=f'Aktor {user.get_full_name() or user.username} mengajukan untuk bergabung jadwal "{schedule.title}".')
    messages.success(request, 'Pengajuan bergabung dikirim. Mohon tunggu konfirmasi produser.')
    return redirect('actor_my_schedules')


@login_required
def leave_schedule(request: HttpRequest, pk: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    app = get_object_or_404(ScheduleApplication, schedule_id=pk, actor=user)
    if app.status != 'pending':
        messages.error(request, 'Tidak dapat membatalkan jika status sudah dikonfirmasi/ditolak.')
        return redirect('actor_my_schedules')
    app.delete()
    messages.info(request, 'Pengajuan telah dibatalkan.')
    return redirect('actor_my_schedules')


@login_required
def approve_application(request: HttpRequest, app_id: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'producer':
        return HttpResponseForbidden('Hanya produser yang dapat mengelola pengajuan.')
    application = get_object_or_404(ScheduleApplication, id=app_id)
    if application.schedule.producer_id != user.id:
        return HttpResponseForbidden('Tidak memiliki izin untuk pengajuan ini.')
    if request.method != 'POST':
        return redirect('producer_dashboard')
    application.status = 'confirmed'
    application.responded_at = timezone.now()
    application.save(update_fields=['status', 'responded_at'])
    Notification.objects.create(user=application.actor, schedule=application.schedule, message=f'Pengajuan Anda pada "{application.schedule.title}" diterima.')
    messages.success(request, 'Pengajuan diterima.')
    return redirect('producer_dashboard')

@login_required
def reject_application(request: HttpRequest, app_id: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'producer':
        return HttpResponseForbidden('Hanya produser yang dapat mengelola pengajuan.')
    application = get_object_or_404(ScheduleApplication, id=app_id)
    if application.schedule.producer_id != user.id:
        return HttpResponseForbidden('Tidak memiliki izin untuk pengajuan ini.')
    if request.method != 'POST':
        return redirect('producer_dashboard')
    application.status = 'rejected'
    application.responded_at = timezone.now()
    application.save(update_fields=['status', 'responded_at'])
    Notification.objects.create(user=application.actor, schedule=application.schedule, message=f'Pengajuan Anda pada "{application.schedule.title}" ditolak.')
    messages.info(request, 'Pengajuan ditolak.')
    return redirect('producer_dashboard')

@login_required
def close_schedule(request: HttpRequest, pk: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    schedule = get_object_or_404(ShootingSchedule, pk=pk)
    if user.role != 'producer' or schedule.producer_id != user.id:
        return HttpResponseForbidden('Tidak memiliki izin untuk menutup pendaftaran.')
    if request.method != 'POST':
        return redirect('producer_dashboard')
    schedule.status = 'closed'
    schedule.save(update_fields=['status'])
    messages.info(request, 'Pendaftaran jadwal ditutup.')
    return redirect('producer_dashboard')


@login_required
def editor_dashboard(request: HttpRequest) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'editor':
        return HttpResponseForbidden('Hanya editor yang dapat mengakses halaman ini.')
    tasks = SocialMediaTask.objects.filter(editor=user, is_completed=False).order_by('due_date')
    completed_tasks = SocialMediaTask.objects.filter(editor=user, is_completed=True).order_by('-completed_at')
    return render(request, 'schedule/editor_dashboard.html', {
        'tasks': tasks,
        'completed_tasks': completed_tasks,
    })


@login_required
def complete_social_task(request: HttpRequest, task_id: int) -> HttpResponse:
    user: User = request.user  # type: ignore
    if user.role != 'editor':
        return HttpResponseForbidden('Hanya editor yang dapat menyelesaikan task.')
    task = get_object_or_404(SocialMediaTask, id=task_id, editor=user)
    if request.method != 'POST':
        return redirect('editor_dashboard')
    task.is_completed = True
    task.completed_at = timezone.now()
    task.save(update_fields=['is_completed', 'completed_at'])
    messages.success(request, 'Task ditandai sebagai selesai.')
    return redirect('editor_dashboard')
