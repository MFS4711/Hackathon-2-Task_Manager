from django.urls import path
from .views import task_dashboard, task_edit, task_delete, task_add
from . import views

urlpatterns = [
    path('task-dashboard/<int:user_id>/', task_dashboard, name='task_dashboard'),
    path('task-edit/<int:user_id>/<int:task_id>/', task_edit, name='task_edit'),
    path('task-delete/<int:user_id>/<int:task_id>/', task_delete, name='task_delete'),
    path('task-add/<int:user_id>/', task_add, name='task_add'),
]

