from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Task(models.Model):
    """
    Represents a task in a task management system.

    This model stores the details of a task, including its title,
    description, assigned user, priority, status, category, due date,
    and timestamps for creation and updates. The task has various states
    and constraints that ensure data integrity
    (e.g., valid due dates, valid status transitions).

    Attributes:
        user (ForeignKey): The user who is assigned the task.
        title (str): The title or name of the task.
        description (str): A detailed description of the task.
        priority (str): The priority of the task, chosen from predefined
        priority options.
        status (str): The current status of the task, chosen from
        predefined status options.
        category (str): The category of the task, chosen from predefined
        categories (e.g., Work, Personal).
        due_date (DateField): The due date for completing the task.
        created_at (DateTimeField): The timestamp when the task
        was created.
        updated_at (DateTimeField): The timestamp when the task
        was last updated.

    Methods:
        __str__(): Returns the title of the task as its
        string representation.
        save(): Overrides the default save method to automatically set
        the task's status to 'Overdue' if the due date has passed and
        the task is still in a pending state.
        clean(): Custom validation to ensure that due dates are not in
        the past and that status transitions follow business rules
        (e.g., a task can only be marked 'Completed' if it was
        'In Progress').
    """
    # Priority Choices
    HIGH = 'High'
    MEDIUM = 'Medium'
    LOW = 'Low'
    PRIORITY_CHOICES = [
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    ]

    # Status Choices
    TO_DO = 'To Do'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    OVERDUE = 'Overdue'
    STATUS_CHOICES = [
        (TO_DO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (OVERDUE, 'Overdue'),
    ]

    # Category Choices
    WORK = 'Work'
    PERSONAL = 'Personal'
    STUDY = 'Study'
    HEALTH = 'Health'
    OTHER = 'Other'
    CATEGORY_CHOICES = [
        (WORK, 'Work'),
        (PERSONAL, 'Personal'),
        (STUDY, 'Study'),
        (HEALTH, 'Health'),
        (OTHER, 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=MEDIUM
    )
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=TO_DO
    )
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default=WORK
    )
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically set the status to
        'Overdue' if the task is still 'To Do' or 'In Progress' and
        the due date has passed.
        """
        current_date = timezone.now().date()
        is_due = self.due_date < current_date
        is_status_pending = self.status in [self.TO_DO, self.IN_PROGRESS]

        if is_due and is_status_pending:
            self.status = self.OVERDUE

        super().save(*args, **kwargs)

    def clean(self):
        """
        Custom validation to check:
        1. Due date is not in the past.
        2. Task can only be marked 'Completed' if it was previously
        'In Progress'.
        3. Task marked as 'Completed' cannot be reverted back to 'To Do'.
        """
        # Ensure due date is not in the past
        if self.due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past.")

        # Ensure that 'OVERDUE' cannot be assigned manually
        if self.status == self.OVERDUE:
            raise ValidationError(
                "The status 'Overdue' is automatically set by the system and \
                cannot be assigned manually.")

        # Only allow status change to 'Completed' if previous was 'In Progress'
        if self.status == self.COMPLETED:
            if not self.pk:  # This is a new task
                raise ValidationError(
                    "A new task cannot be marked as 'Completed'.")

            # Check if the current status is 'In Progress' or not
            previous_status = Task.objects.get(
                pk=self.pk).status  # Fetch the previous status
            if previous_status != self.IN_PROGRESS:
                raise ValidationError(
                    "A task can only be marked as 'Completed' \
                    after being 'In Progress'.")

        # Ensure a 'Completed' task cannot be changed back to 'In Progress'
        if self.status == self.IN_PROGRESS:
            if self.pk and \
                    Task.objects.get(pk=self.pk).status == self.COMPLETED:
                raise ValidationError(
                    "A task marked as 'Completed' cannot be changed back \
                    to 'In Progress'.")

        # Ensure a 'Completed' task cannot be changed back to 'To Do'
        if self.status == self.TO_DO:
            if self.pk and \
                    Task.objects.get(pk=self.pk).status == self.COMPLETED:
                raise ValidationError(
                    "A task marked as 'Completed' cannot be changed back \
                        to 'To Do'."
                )
