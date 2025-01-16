from django.urls import path
from . import views

urlpatterns = [
    # View to render the task-dashboard page
    path('task-dashboard/<int:user_id>/', views.task_dashboard, name='task_dashboard'),

]