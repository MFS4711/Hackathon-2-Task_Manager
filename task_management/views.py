from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Task
from django.urls import reverse_lazy, reverse
# Create your views here.


def task_dashboard(request):
    """
    Display the task dashboard.

    **Context:**

    None

    **Template:**

    :template:`task_management/task-dashboard.html`
    """

    return render(request, "task_management/task-dashboard.html")

class AddTaskView(CreateView):
    model = Task
    template_name='add-task.html'
    success_url = reverse_lazy('home')
    
class UpdateTaskView(UpdateView):
    model = Task
    form_class = EditForm
    template_name = 'update-task.html'
    success_url = reverse_lazy('home')

class DeleteTaskView(DeleteView):
    model = Task
    template_name = 'delete-task.html'
    success_url = reverse_lazy('home')


