from django.urls import path
from . import views

urlpatterns = [
    # View to render the task-dashboard page
    path('task-dashboard/', views.task_dashboard, name='task_dashboard'),

]