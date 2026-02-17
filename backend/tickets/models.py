from django.db import models

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('billing', 'Billing'),
        ('technical', 'Technical'),
        ('account', 'Account'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # User selected values
    user_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    user_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    
    # AI suggested values (optional)
    ai_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True)
    ai_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title