from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import TaskForm
from .models import Task
from django.urls import reverse_lazy, reverse
# Create your views here.


def task_dashboard(request, user_id):
    """
    Display the task dashboard.

    **Context:**

    None

    **Template:**

    :template:`task_management/task-dashboard.html`
    """
    # Fetch the user by user_id
    user = get_object_or_404(User, id=user_id)

    # Add view data

    # Context to pass to the template
    context = {
        "user": user,
    }

    return render(request, "task_management/task-dashboard.html", context)

# --------------------------------------------------------

# class AddTaskView(CreateView):
#     model = Task
#     form_class = TaskForm
#     template_name ='task_management/add_task.html'
#     success_url = reverse_lazy('home')

# class UpdateTaskView(UpdateView):
#     model = Task
#     form_class = EditTaskForm
#     template_name = 'update-task.html'
#     success_url = reverse_lazy('home')

# class DeleteTaskView(DeleteView):
#     model = Task
#     template_name = 'delete-task.html'
#     success_url = reverse_lazy('home')
