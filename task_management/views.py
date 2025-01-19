from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from .forms import TaskForm
from .models import Task


@login_required(login_url='/accounts/login/')
def task_dashboard(request, user_id):
    """
    View for the user's task dashboard.

    **Context:**
    - Displays the user's tasks categorized by their status
    (overdue, upcoming, completed).
    - Allows filtering tasks based on status, priority, category,
    and visibility.

    **Template:**
    :template:`task_management/task-dashboard.html`
    """
    # Ensure the logged-in user matches the user_id in the URL
    if request.user.id != int(user_id):
        messages.error(request, "You are not authorised to access this page.")
        return redirect('/')

    # Fetch the user object from the database
    user = get_object_or_404(User, id=user_id)

    # Get the current date and upcoming date ranges
    today = timezone.now().date()
    next_week = today + timezone.timedelta(days=7)
    next_two_weeks = today + timezone.timedelta(weeks=2)
    next_month = today + timezone.timedelta(weeks=4)

    # Fetch overdue tasks for the user
    overdue_tasks = Task.objects.filter(
        user=user,
        status__in=[Task.TO_DO, Task.IN_PROGRESS],
        due_date__lt=today
    )

    # Extract filters from GET request parameters
    filters = {
        'status': request.GET.get('status', ''),
        'priority': request.GET.get('priority', ''),
        'category': request.GET.get('category', ''),
        'visibility': request.GET.get('visibility', '7_days')
    }

    # Apply visibility filters to determine the upcoming tasks to show
    if filters['visibility'] == '7_days':
        upcoming_tasks = Task.objects.filter(
            user=user, due_date__gte=today, due_date__lte=next_week)
    elif filters['visibility'] == '2_weeks':
        upcoming_tasks = Task.objects.filter(
            user=user, due_date__gte=today, due_date__lte=next_two_weeks)
    elif filters['visibility'] == '1_month':
        upcoming_tasks = Task.objects.filter(
            user=user, due_date__gte=today, due_date__lte=next_month)
    else:
        upcoming_tasks = Task.objects.filter(user=user, due_date__gte=today)

    # Apply additional filters (status, priority, category)
    if filters['status']:
        upcoming_tasks = upcoming_tasks.filter(status=filters['status'])
    if filters['priority']:
        upcoming_tasks = upcoming_tasks.filter(priority=filters['priority'])
    if filters['category']:
        upcoming_tasks = upcoming_tasks.filter(category=filters['category'])

    # Fetch completed tasks
    completed_tasks = Task.objects.filter(user=user, status=Task.COMPLETED)

    # Count tasks in different status (to-do, in-progress, completed, overdue)
    task_counts = {
        'to_do': Task.objects.filter(user=user, status=Task.TO_DO).count(),
        'in_progress': Task.objects.filter(
            user=user,
            status=Task.IN_PROGRESS
        ).count(),
        'completed': Task.objects.filter(
            user=user,
            status=Task.COMPLETED
        ).count(),
        'overdue': overdue_tasks.count(),
    }

    # Prepare context for the template
    context = {
        'user': user,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
        'completed_tasks': completed_tasks,
        'filters': filters,
        'task_counts': task_counts,
    }

    return render(request, "task_management/task-dashboard.html", context)


@login_required(login_url='/accounts/login/')
def task_add(request, user_id):
    """
    View to add a new task.

    **Context:**
    - Displays the task creation form.
    - Ensures that the logged-in user matches the user_id.
    - On successful submission, creates a new task.

    **Template:**
    :template:`task_management/add-task.html`
    """
    # Ensure the logged-in user matches the user_id in the URL
    if request.user.id != int(user_id):
        messages.error(request, "You are not authorised to access this page.")
        return redirect('/')

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        task_form = TaskForm(data=request.POST)
        if task_form.is_valid():
            # Save the task instance with the logged-in user
            task = task_form.save(commit=False)
            task.user = request.user
            task.save()
            messages.add_message(request, messages.SUCCESS,
                                 'You have created a new task.')
            return redirect('task_dashboard', user_id=user.id)

    task_form = TaskForm()

    # Prepare context for the template
    context = {
        "user": user,
        "task_form": task_form,
    }

    return render(request, 'task_management/add-task.html', context)


@login_required(login_url='/accounts/login/')
def task_edit(request, user_id, task_id):
    """
    View to edit an existing task.

    **Context:**
    - Displays the task edit form pre-filled with the current task's details.
    - Ensures that the logged-in user matches the user_id.
    - Updates the task upon valid form submission.

    **Template:**
    :template:`task_management/update-task.html`
    """
    # Ensure the logged-in user matches the user_id in the URL
    if request.user.id != int(user_id):
        messages.error(request, "You are not authorised to access this page.")
        return redirect('/')

    task = get_object_or_404(Task, pk=task_id)

    if request.method == "POST":
        # Initialize the form with the current task data
        task_form = TaskForm(data=request.POST, instance=task)
        if task_form.is_valid():
            # Save the updated task
            task_form.save()
            messages.add_message(request, messages.SUCCESS, "Task updated.")
            return redirect('task_dashboard', user_id=user_id)
        else:
            messages.add_message(
                request, messages.ERROR, 'There was an error updating this \
                task. Please try again.')
    else:
        # For GET request, pre-fill the form with the existing task data
        task_form = TaskForm(instance=task)

    # Prepare context for the template
    context = {
        "user": task.user,
        "task_form": task_form,
        "task": task,  # Optionally pass task for context
    }

    return render(request, 'task_management/update-task.html', context)


@login_required(login_url='/accounts/login/')
def task_delete(request, user_id, task_id):
    """
    View to delete a task.

    **Context:**
    - Ensures that the logged-in user matches the user_id.
    - Deletes task if it belongs to logged-in user and redirects to dashboard.
    - Shows an error message if the task cannot be deleted.

    **Template:**
    - Redirects back to the task dashboard after deletion.
    """
    # Ensure the logged-in user matches the user_id in the URL
    if request.user.id != int(user_id):
        messages.error(request, "You are not authorised to access this page.")
        return redirect('/')

    task = get_object_or_404(Task, pk=task_id)

    if task.user == request.user:
        task.delete()
        messages.add_message(request, messages.SUCCESS, 'Task deleted!')
    else:
        messages.add_message(
            request, messages.ERROR, 'There was an error deleting the task. \
            Please try again.')

    return redirect('task_dashboard', user_id=request.user.id)
