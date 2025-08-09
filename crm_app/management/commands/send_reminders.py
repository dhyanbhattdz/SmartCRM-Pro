from django.core.management.base import BaseCommand
from crm_app.utils.email_reminder import send_followup_reminders

class Command(BaseCommand):
    help = 'Send email reminders for follow-ups'

    def handle(self, *args, **kwargs):
        send_followup_reminders()
        self.stdout.write(self.style.SUCCESS('✅ Follow-up reminders sent!'))
