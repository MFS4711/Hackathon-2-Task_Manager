from django.shortcuts import render
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
