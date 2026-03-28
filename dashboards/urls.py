from django.urls import path
from .import views

urlpatterns = [

    path('', views.dashboard, name='dashboard'),
    path('myproblems/', views.myproblems, name='myproblems'),

    path('myproblems/add/', views.add_problem, name='add_problem'),
    # path('myproblems/edit/<int:problem_id>/', views.edit_problem, name='edit_problem'),
    path('myproblems/delete/<int:problem_id>/', views.delete_problem, name='delete_problem'),
    path('solved_issues/', views.solved_issues, name='solved_issues'),
    path('notifications/mark_read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark_all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/json/', views.notifications_json, name='notifications_json'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
]            