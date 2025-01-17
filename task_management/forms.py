from django import forms
from .models import Task
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta  # For timedelta to calculate future dates


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority',
                  'status', 'category', 'due_date']
        widgets = {
            'due_date': forms.DateInput(
                format='%Y-%m-%d',  # Date format for HTML5 date input
                attrs={
                    'type': 'date',  # HTML5 date input type
                    'class': 'form-control',  # Optional for styling
                    # Set min to 1 day in the future
                    'min': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
                }
            ),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def clean_due_date(self):
        """
        Custom validation for due_date to ensure it is not in the past.
        """
        due_date = self.cleaned_data.get('due_date')
        if due_date < timezone.now().date():
            raise ValidationError("Due date cannot be in the past.")
        return due_date

    def clean(self):
        """
        Custom validation for status transitions and other conditions.
        """
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        previous_status = None

        if self.instance.pk:
            previous_status = Task.objects.get(pk=self.instance.pk).status

        # Ensure that 'Overdue' is not set manually
        if status == Task.OVERDUE:
            raise ValidationError(
                "The status 'Overdue' is automatically set by the system and cannot be assigned manually.")

        # Only allow status change to 'Completed' if previous status was 'In Progress'
        if status == Task.COMPLETED:
            if not self.instance.pk:  # New task, cannot be 'Completed'
                raise ValidationError(
                    "A new task cannot be marked as 'Completed'.")
            if previous_status != Task.IN_PROGRESS:
                raise ValidationError(
                    "A task can only be marked as 'Completed' after being 'In Progress'.")

        # Ensure a 'Completed' task cannot be changed back to 'In Progress'
        if status == Task.IN_PROGRESS and previous_status == Task.COMPLETED:
            raise ValidationError(
                "A task marked as 'Completed' cannot be changed back to 'In Progress'.")

        # Ensure a 'Completed' task cannot be changed back to 'To Do'
        if status == Task.TO_DO and previous_status == Task.COMPLETED:
            raise ValidationError(
                "A task marked as 'Completed' cannot be changed back to 'To Do'.")

        return cleaned_data


# class TaskForm(forms.ModelForm):
#     class Meta:
#         model = Task
#         fields = [
#             'title',
#             'description',
#             'priority',
#             'status',
#             'category',
#             'due_date',
#         ]
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Title'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Task Description'}),
#             'priority': forms.Select(attrs={'class': 'form-select'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'category': forms.Select(attrs={'class': 'form-select'}),
#             'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#         }


# class EditTaskForm(forms.ModelForm):
#     class Meta:
#         model = Task
#         fields = [
#             'title',
#             'description',
#             'priority',
#             'status',
#             'category',
#             'due_date',
#         ]
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task Title'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Task Description'}),
#             'priority': forms.Select(attrs={'class': 'form-select'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'category': forms.Select(attrs={'class': 'form-select'}),
#             'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#         }
