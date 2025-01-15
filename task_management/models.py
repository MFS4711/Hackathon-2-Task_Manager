from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Task(models.Model):
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
        Override the save method to automatically set the status to 'Overdue' if the
        task is still 'To Do' or 'In Progress' and the due date has passed.
        """
        if self.due_date < timezone.now().date() and self.status in [self.TO_DO, self.IN_PROGRESS]:
            self.status = self.OVERDUE
        super().save(*args, **kwargs)

    def clean(self):
        """
        Custom validation to check:
        1. Due date is not in the past.
        2. Task can only be marked 'Completed' if it was previously 'In Progress'.
        """
        # Ensure due date is not in the past
        if self.due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past.")

        # Only allow status change to 'Completed' if the previous status was 'In Progress'
        if self.status == self.COMPLETED:
            if not self.pk:  # This is a new task
                raise ValidationError(
                    "A new task cannot be marked as 'Completed'.")

            # Check if the current status is 'In Progress' or not
            previous_status = Task.objects.get(
                pk=self.pk).status  # Fetch the previous status
            if previous_status != self.IN_PROGRESS:
                raise ValidationError(
                    "A task can only be marked as 'Completed' after being 'In Progress'.")
            
        # Ensure that a task marked as 'Completed' cannot be changed back to 'In Progress'
        if self.status == self.IN_PROGRESS:
            if self.pk and Task.objects.get(pk=self.pk).status == self.COMPLETED:
                raise ValidationError("A task marked as 'Completed' cannot be changed back to 'In Progress'.")
