from django.db import models
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
