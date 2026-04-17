from django.contrib.auth.models import User
from django.db import models

#model for category
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


#model for project
class Project(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    title = models.CharField(max_length=220, db_index=True)
    student_name = models.CharField(max_length=120, blank=True)
    roll_number = models.CharField(max_length=50, blank=True)
    project_link = models.URLField(blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='projects')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
# ordering projects by latest created date
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
        ]
# returning project title when object is printed
    def __str__(self):
        return self.title
# converting status value to readable label (like Approved, Pending)
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Pending')
