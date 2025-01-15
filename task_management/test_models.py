from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Task


class TaskModelTest(TestCase):

    def setUp(self):
        """
        Set up a test instance of Task to be used in the following
        test cases.

        This method creates a `Task` object that will be available for
        all test methods to ensure consistent data across tests.
        """
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.task = Task.objects.create(
            user=self.user,
            title="Test Task",
            description="A task for testing purposes",
            priority=Task.MEDIUM,
            status=Task.TO_DO,
            category=Task.WORK,
            due_date=timezone.now().date() + timedelta(days=5)
        )

    def test_task_creation(self):
        """
        Test that a Task object is correctly created and its fields
        match the given data.

        This test ensures that the attributes like `title`, `description`, 
        `priority`, `status`, `category`, and `due_date` are properly set during
        the object creation.
        """
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "A task for testing purposes")
        self.assertEqual(self.task.priority, Task.MEDIUM)
        self.assertEqual(self.task.status, Task.TO_DO)
        self.assertEqual(self.task.category, Task.WORK)
        self.assertEqual(self.task.due_date,
                         timezone.now().date() + timedelta(days=5))

    def test_default_values(self):
        """
        Test that a new Task instance uses the correct default values
        for fields not explicitly set.

        This test checks the behavior when a `Task` is created without
        specifying certain fields, ensuring that defaults like `priority`, 
        `status`, and `category` are set properly.
        """
        default_task = Task.objects.create(
            user=self.user,
            title="Default Task",
            description="A task with default values",
            due_date=timezone.now().date() + timedelta(days=3)
        )

        self.assertEqual(default_task.priority, Task.MEDIUM)
        self.assertEqual(default_task.status, Task.TO_DO)
        self.assertEqual(default_task.category, Task.WORK)

    def test_str_method(self):
        """
        Test the `__str__` method of the Task model.

        The `__str__` method should return a string representation of the
        Task based on the `title` field. This test ensures that the method
        returns the expected string when called on a Task instance.
        """
        self.assertEqual(str(self.task), "Test Task")

    def test_priority_choices(self):
        """
        Test that the `priority` field of the Task model only allows
        valid choices.

        The `priority` field should be one of the values defined in the
        `PRIORITY_CHOICES`.
        """
        valid_priorities = [choice[0] for choice in Task.PRIORITY_CHOICES]
        self.assertIn(self.task.priority, valid_priorities)

    def test_invalid_priority(self):
        """
        Test that an invalid priority raises a `ValidationError`.

        When an invalid priority (not in the defined `PRIORITY_CHOICES`) is set
        for a `Task`, a `ValidationError` should be raised when the object is validated.
        """
        task = Task(
            user=self.user,
            title="Invalid Priority Task",
            description="A task with an invalid priority",
            priority="Invalid",  # Invalid priority
            status=Task.TO_DO,
            category=Task.WORK,
            due_date=timezone.now().date() + timedelta(days=7)
        )

        # Expect a ValidationError to be raised due to the invalid priority
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_status_choices(self):
        """
        Test that the `status` field of the Task model only allows
        valid choices.

        The `status` field should be one of the values defined in the
        `STATUS_CHOICES`.
        """
        valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
        self.assertIn(self.task.status, valid_statuses)

    def test_category_choices(self):
        """
        Test that the `category` field of the Task model only allows
        valid choices.

        The `category` field should be one of the values defined in the
        `CATEGORY_CHOICES`.
        """
        valid_categories = [choice[0] for choice in Task.CATEGORY_CHOICES]
        self.assertIn(self.task.category, valid_categories)

    def test_task_due_date(self):
        """
        Test that the `due_date` field is set correctly and is a valid date.

        This test checks whether the `due_date` is a valid future date when set,
        and ensures that a task with an invalid date (e.g., a past date) should not be created.
        """
        future_due_date_task = Task.objects.create(
            user=self.user,
            title="Future Due Task",
            description="A task with a future due date",
            priority=Task.HIGH,
            status=Task.TO_DO,
            category=Task.PERSONAL,
            due_date=timezone.now().date() + timedelta(days=10)
        )

        self.assertGreater(future_due_date_task.due_date,
                           timezone.now().date())

    def test_task_overdue_status(self):
        """
        Test that the task status can be correctly updated to 'Overdue' 
        if the task's due date is in the past and the status hasn't been marked as completed.
        """
        overdue_task = Task.objects.create(
            user=self.user,
            title="Overdue Task",
            description="A task that is overdue",
            priority=Task.LOW,
            status=Task.TO_DO,
            category=Task.STUDY,
            due_date=timezone.now().date() - timedelta(days=1)  # Past due date
        )

        # Now save again to trigger the status update
        overdue_task.save()

        # Assert that the status has been automatically updated to 'Overdue'
        self.assertEqual(overdue_task.status, Task.OVERDUE)

    def test_task_category_choices(self):
        """
        Test that the `category` field of the Task model only allows
        valid choices.

        This test validates that the `category` field in the model respects the choices defined.
        """
        valid_categories = [choice[0] for choice in Task.CATEGORY_CHOICES]
        self.assertIn(self.task.category, valid_categories)

    def test_task_user_association(self):
        """
        Test that the `Task` is correctly associated with a `User`.

        This test ensures that the `user` field links the task to the correct `User`.
        """
        self.assertEqual(self.task.user.username, "testuser")

    def test_task_due_date_in_the_past(self):
        """
        Test that a Task cannot be created with a due date in the past.
        """
        task = Task(
            user=self.user,
            title="Past Due Task",
            description="A task with a past due date",
            priority=Task.MEDIUM,
            status=Task.TO_DO,
            category=Task.WORK,
            due_date=timezone.now().date() - timedelta(days=1)  # Past date
        )

        # Expect a ValidationError to be raised due to the invalid due_date
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_status_completed_requires_in_progress(self):
        """
        Test that a Task cannot be marked as 'Completed' if it was not 
        previously marked as 'In Progress'.
        """
        task = Task.objects.create(
            user=self.user,
            title="Task Not In Progress",
            description="A task that's being directly set as 'Completed' without being 'In Progress'",
            priority=Task.MEDIUM,
            status=Task.COMPLETED,  # Directly trying to mark it as completed
            category=Task.WORK,
            due_date=timezone.now().date() + timedelta(days=5)
        )

        # Expect a ValidationError to be raised due to invalid status transition
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_status_not_marked_overdue_if_completed(self):
        """
        Test that a Task marked as 'Completed' is not automatically set to 'Overdue'
        even if the due date is in the past.
        """
        completed_task = Task.objects.create(
            user=self.user,
            title="Completed Task",
            description="A task that's already completed",
            priority=Task.LOW,
            status=Task.COMPLETED,
            category=Task.STUDY,
            due_date=timezone.now().date() - timedelta(days=1)  # Past due date
        )

        # Trigger the save method to check for automatic overdue status
        completed_task.save()

        # Ensure that the task's status remains 'Completed' and is not changed to 'Overdue'
        self.assertEqual(completed_task.status, Task.COMPLETED)

    def test_task_status_auto_overdue_on_past_due_date(self):
        """
        Test that the task status is automatically set to 'Overdue' if 
        the due date has passed and the task is still 'To Do' or 'In Progress'.
        """
        overdue_task = Task.objects.create(
            user=self.user,
            title="Overdue Task",
            description="A task that is overdue",
            priority=Task.LOW,
            status=Task.TO_DO,
            category=Task.STUDY,
            due_date=timezone.now().date() - timedelta(days=1)  # Past due date
        )

        # Trigger the save method to check for automatic overdue status
        overdue_task.save()

        # Assert that the status has been automatically updated to 'Overdue'
        self.assertEqual(overdue_task.status, Task.OVERDUE)

    def test_task_status_in_progress_to_completed(self):
        """
        Test that a task can be marked as 'Completed' only if it was 
        previously 'In Progress'.
        """
        task = Task.objects.create(
            user=self.user,
            title="In Progress Task",
            description="A task that's in progress",
            priority=Task.HIGH,
            status=Task.IN_PROGRESS,
            category=Task.WORK,
            due_date=timezone.now().date() + timedelta(days=5)
        )

        # Transition the task to 'Completed'
        task.status = Task.COMPLETED
        task.save()

        # Ensure the task is now marked as 'Completed'
        self.assertEqual(task.status, Task.COMPLETED)

    def test_task_status_completed_to_in_progress(self):
        """
        Test that a task marked as 'Completed' cannot be changed back to 'In Progress'.
        """
        task = Task.objects.create(
            user=self.user,
            title="Completed Task",
            description="A task that's already completed",
            priority=Task.LOW,
            status=Task.COMPLETED,
            category=Task.STUDY,
            due_date=timezone.now().date() + timedelta(days=5)
        )

        # Try to change it back to 'In Progress'
        task.status = Task.IN_PROGRESS

        # Expect a ValidationError to be raised due to invalid status transition
        with self.assertRaises(ValidationError):
            task.full_clean()

    def test_task_status_cannot_be_set_to_overdue_manually(self):
        """
        Test that a task cannot be manually set to 'Overdue'.
        The 'Overdue' status must be set by the system based on the due date.
        """
        overdue_task = Task.objects.create(
            user=self.user,
            title="Overdue Task",
            description="A task that is overdue",
            priority=Task.LOW,
            status=Task.OVERDUE,  # Manually trying to set it to 'Overdue'
            category=Task.STUDY,
            due_date=timezone.now().date() - timedelta(days=1)  # Past due date
        )

        # Expect a ValidationError because the status should not be manually set to 'Overdue'
        with self.assertRaises(ValidationError):
            overdue_task.full_clean()
