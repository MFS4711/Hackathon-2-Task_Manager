from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import TaskForm
from .models import Task
from django.urls import reverse_lazy, reverse

# Create your views here.

def homepage(request):
    return render(request, "core/index.html")

def task_dashboard(request, user_id):
    
    # Fetch the user by user_id
    user = get_object_or_404(User, id=user_id)

    if user !=request.user:
        raise Http404("You need to log in to view this page")

    tasks = Task.objects.filter(user=user).order_by('-status', '-due_date')
    for task in tasks:
        if task.due_date and task.due_date <= timezone.now() and task.status != 3:  # 3 is "Overdue"
            task.status = 3  # Set status to "Overdue"
            task.save()
    if request.method == "POST":
        task_form = TaskForm(data=request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.author = request.user
            task.save()
            messages.add_message(
                request, messages.SUCCESS,
                'You have created a new task'
            )
            return redirect('dashboard', user_id=user.id)

    task_form = TaskForm()

    context = {
        "user": user,
        "tasks": tasks,
        "task_form": task_form,

    }

    return render(request, "task_management/task-dashboard.html", context)
   
def task_edit(request, user_id, task_id):
    """
    view to edit a task
    """
    if request.method == "POST":
        #get the object you want to eidit
        task= get_object_or404(Task, pk=task_id)
        #initialises form with instance  of task pre-filled
        task_form = TaskForm(data=request.POST, instance=task)
        #check validation and form validation
        if task_form.is_valid():
            #Save the form with updates data
            task_form.save()
            messages.add_message(request, messages.SUCCESS, "Task updated")

        else:
            messages.add_message(
                request, messages.ERROR, 'There was an error updating this task, Please try again.'
            )
        

    return HttpResponseRedirect(reverse('dashboard', args=[task.author.task_id]))

def task_delete(request, user_id, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if task.user == request.user:
        task.delete()
        messages.add_message(request, messages.SUCCESS, 'Task deleted!')
    else:
        messages.add_message(request, messages.ERROR, 'There was an error deleting the task. Please try again')
    return HttpResponseRedirect(reverse('dashboard', args=[task.author.id]))

