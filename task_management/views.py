from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import TaskForm
from .models import Task

def task_dashboard(request, user_id):
    # Fetch the user by user_id
    user = get_object_or_404(User, id=user_id)

    if user != request.user:
        raise Http404("You need to log in to view this page.")

    tasks = Task.objects.filter(user=user).order_by('-status', '-due_date')
    for task in tasks:
        if task.due_date and task.due_date <= timezone.now().date() and task.status != 3:  # 3 is "Overdue"
            task.status = 3  # Set status to "Overdue"
            task.save()

    if request.method == "POST":
        task_form = TaskForm(data=request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.user = request.user
            task.save()
            messages.add_message(
                request, messages.SUCCESS,
                'You have created a new task.'
            )
            return redirect('task_dashboard', user_id=user.id)

    task_form = TaskForm()

    context = {
        "user": user,
        "tasks": tasks,
        "task_form": task_form,
    }

    return render(request, "task_management/task-dashboard.html", context)

def task_edit(request, user_id, task_id):
    """
    View to edit a task
    """
    task = get_object_or_404(Task, pk=task_id)

    if request.method == "POST":
        # Initializes form with the instance of task pre-filled
        task_form = TaskForm(data=request.POST, instance=task)
        if task_form.is_valid():
            # Save the form with updated data
            task_form.save()
            messages.add_message(request, messages.SUCCESS, "Task updated.")
        else:
            messages.add_message(
                request, messages.ERROR,
                'There was an error updating this task. Please try again.'
            )

    return HttpResponseRedirect(reverse('task_dashboard', args=[task.user.id]))

def task_delete(request, user_id, task_id):
    """
    View to delete a task
    """
    task = get_object_or_404(Task, pk=task_id)

    if task.user == request.user:
        task.delete()
        messages.add_message(request, messages.SUCCESS, 'Task deleted!')
    else:
        messages.add_message(request, messages.ERROR, 'There was an error deleting the task. Please try again.')

    return HttpResponseRedirect(reverse('task_dashboard', args=[task.user.id]))
