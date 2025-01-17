from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from .forms import TaskForm
from .models import Task


def task_dashboard(request, user_id):
    # Fetch the user by user_id
    user = get_object_or_404(User, id=user_id)

    if user != request.user:
        raise Http404("You need to log in to view this page.")

    # Get today's date and the date 7 days from today
    today = timezone.now().date()
    next_week = today + timezone.timedelta(days=7)

    # Fetch tasks categorized as overdue
    overdue_tasks = Task.objects.filter(
        user=user, status__in=[Task.TO_DO, Task.IN_PROGRESS], due_date__lt=today)

    # Fetch tasks that are due within the next 7 days
    upcoming_tasks = Task.objects.filter(
        user=user, due_date__gte=today, due_date__lte=next_week).order_by('due_date')

    # Get filters from request
    filters = {
        'status': request.GET.get('status', ''),
        'priority': request.GET.get('priority', ''),
        'category': request.GET.get('category', '')
    }

    # Apply filters to upcoming tasks
    filtered_tasks = upcoming_tasks
    if filters['status']:
        filtered_tasks = filtered_tasks.filter(status=filters['status'])
    if filters['priority']:
        filtered_tasks = filtered_tasks.filter(priority=filters['priority'])
    if filters['category']:
        filtered_tasks = filtered_tasks.filter(category=filters['category'])

    context = {
        'user': user,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': filtered_tasks,
        'filters': filters
    }

    return render(request, "task_management/task-dashboard.html", context)


def task_add(request, user_id):
    """
    View to add a new task
    """
    user = get_object_or_404(User, id=user_id)

    if user != request.user:
        raise Http404("You need to log in to view this page.")

    if request.method == "POST":
        task_form = TaskForm(data=request.POST)
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.user = request.user  # Save task with the logged-in user
            task.save()
            messages.add_message(request, messages.SUCCESS,
                                 'You have created a new task.')
            return redirect('task_dashboard', user_id=user.id)

    task_form = TaskForm()

    context = {
        "user": user,
        "task_form": task_form,
    }

    return render(request, 'task_management/add-task.html', context)


def task_edit(request, user_id, task_id):
    """
    View to edit a task
    """
    task = get_object_or_404(Task, pk=task_id)

    if task.user != request.user:
        raise Http404("You cannot edit this task.")

    if request.method == "POST":
        # Initializes the form with the instance of task pre-filled
        task_form = TaskForm(data=request.POST, instance=task)
        if task_form.is_valid():
            # Save the updated task
            task_form.save()
            messages.add_message(request, messages.SUCCESS, "Task updated.")
            return redirect('task_dashboard', user_id=user_id)
        else:
            messages.add_message(
                request, messages.ERROR,
                'There was an error updating this task. Please try again.'
            )
    else:
        # For GET request, pre-fill the form with the existing task data
        task_form = TaskForm(instance=task)

    context = {
        "user": task.user,
        "task_form": task_form,
        "task": task,  # Optionally pass task for context
    }

    return render(request, 'task_management/update-task.html', context)


def task_delete(request, user_id, task_id):
    """
    View to delete a task
    """
    task = get_object_or_404(Task, pk=task_id)

    if task.user == request.user:
        task.delete()
        messages.add_message(request, messages.SUCCESS, 'Task deleted!')
    else:
        messages.add_message(
            request, messages.ERROR, 'There was an error deleting the task. Please try again.')

    return redirect('task_dashboard', user_id=request.user.id)
