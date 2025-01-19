from django.urls import path
from . import views

urlpatterns = [
    path('task-dashboard/<int:user_id>/',
         views.task_dashboard, name='task_dashboard'),
    path('task-edit/<int:user_id>/<int:task_id>/', views.task_edit, name='task_edit'),
    path('task-delete/<int:user_id>/<int:task_id>/',
         views.task_delete, name='task_delete'),
    path('task-add/<int:user_id>/', views.task_add, name='task_add'),
]
