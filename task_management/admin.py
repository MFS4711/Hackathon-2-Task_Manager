from django.contrib import admin
from .models import Task

# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'title',
        'user',
        'priority',
        'status',
        'category',
        'due_date',
        'created_at',
        'updated_at'
    )

    # Fields to filter by in the sidebar
    list_filter = (
        'priority',
        'status',
        'category',
        'due_date',
        'user'
    )

    # Fields to search for
    search_fields = ('title', 'description', 'user__username')

    # Default ordering
    ordering = ('-created_at', 'due_date')
