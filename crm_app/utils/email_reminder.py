from django.core.mail import send_mail
from datetime import date
from crm_app.models import Lead

def send_followup_reminders():
    today = date.today()
    leads = Lead.objects.filter(follow_up_date__lte=today)

    for lead in leads:
        subject = f"🔔 Follow-up Reminder: {lead.title}"
        message = f"""Dear CRM User,

You have a lead titled '{lead.title}' for customer '{lead.customer.name}' 
that is scheduled for follow-up on {lead.follow_up_date}.

Please follow up as soon as possible.

Thanks,
SmartCRM-AI Bot"""
        recipient_list = ['your_email@gmail.com']  # 🔁 You can make this dynamic
        send_mail(subject, message, 'your_email@gmail.com', recipient_list)
