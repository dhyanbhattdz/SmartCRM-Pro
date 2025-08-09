from venv import logger
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def send_lead_status_reminders(self):
        leads = self.lead_set.all()
        if not leads:
            return False
            
        context = {
            'customer': self,
            'leads': leads,
            'date': timezone.now().strftime("%B %d, %Y")
        }
        
        email_subject = f"Your Leads Status Update - {self.company}"
        email_body = render_to_string('emails/lead_status_reminder.txt', context)
        html_body = render_to_string('emails/lead_status_reminder.html', context)
        
        try:
            send_mail(
                email_subject,
                email_body,
                'your@company.com',
                [self.email],
                html_message=html_body,
                fail_silently=False
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send reminder to {self.email}: {str(e)}")
            return False

    def __str__(self):
        return self.name

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('lost', 'Lost'),
        ('won', 'Won'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title
