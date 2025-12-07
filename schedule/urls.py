from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('producer/', views.producer_dashboard, name='producer_dashboard'),
    path('editor/', views.editor_dashboard, name='editor_dashboard'),

    # Actor pages
    path('actor/', views.actor_dashboard, name='actor_dashboard'),  # redirects to my page
    path('actor/my/', views.actor_my_schedules, name='actor_my_schedules'),
    path('actor/available/', views.actor_available_schedules, name='actor_available_schedules'),

    # Schedule actions
    path('schedule/create/', views.create_schedule, name='create_schedule'),
    path('schedule/<int:pk>/edit/', views.edit_schedule, name='edit_schedule'),
    path('schedule/<int:pk>/delete/', views.delete_schedule, name='delete_schedule'),
    path('schedule/<int:pk>/join/', views.join_schedule, name='join_schedule'),
    path('schedule/<int:pk>/leave/', views.leave_schedule, name='leave_schedule'),
    path('schedule/<int:pk>/complete/', views.complete_schedule, name='complete_schedule'),
    path('schedule/<int:pk>/close/', views.close_schedule, name='close_schedule'),

    # Applications moderation
    path('application/<int:app_id>/approve/', views.approve_application, name='approve_application'),
    path('application/<int:app_id>/reject/', views.reject_application, name='reject_application'),

    # Social Media Tasks
    path('social_task/<int:task_id>/complete/', views.complete_social_task, name='complete_social_task'),
]
