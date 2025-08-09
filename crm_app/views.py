from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Customer, Lead
from .forms import CustomerForm, LeadForm
from datetime import datetime
from .utils.scraper import get_company_info
import csv
import os
import matplotlib
matplotlib.use('Agg')  # For non-GUI matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db.models import Count
import json
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages


# ---------------------------------------------
# 🔹 Home View - Show Dashboard, Customers, Leads, and Predictions
# ---------------------------------------------
from django.core.paginator import Paginator
from django.core.paginator import Paginator

from django.core.paginator import Paginator
from .models import Lead, Customer
from .models import Lead, Customer
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Lead, Customer


@login_required(login_url='login')
def home(request):
    # Get current page numbers from URL parameters
    lead_page = request.GET.get('lead_page', 1)
    customer_page = request.GET.get('customer_page', 1)
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'follow_up_date')
    current_tab = request.GET.get('tab', 'customers')  # Get current tab
    leads = Lead.objects.all()
    customers = Customer.objects.all()

    # Counts
    won_leads_count = leads.filter(status='won').count()
    lost_leads_count = leads.filter(status='lost').count()
    
    # Validate sort_by parameter
    if sort_by not in ['follow_up_date', '-follow_up_date', 'created_at', '-created_at', 'title', '-title']:
        sort_by = 'follow_up_date'

    # Leads with pagination
    lead_queryset = Lead.objects.all().order_by(sort_by)
    lead_paginator = Paginator(lead_queryset, 10)
    try:
        leads = lead_paginator.page(lead_page)
    except (PageNotAnInteger, EmptyPage):
        leads = lead_paginator.page(1)

    # Customers with search and pagination
    customer_queryset = Customer.objects.all()
    if search_query:
        customer_queryset = customer_queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(company__icontains=search_query)
        )
    customer_paginator = Paginator(customer_queryset, 10)
    try:
        customers = customer_paginator.page(customer_page)
    except (PageNotAnInteger, EmptyPage):
        customers = customer_paginator.page(1)

    # Generate charts only if there's data
    pie_chart = None
    bar_chart = None
    status_bar_chart = None
    
    if Lead.objects.exists():
        pie_chart = generate_status_pie_chart()
        bar_chart = generate_monthly_lead_bar_chart()
        status_bar_chart = generate_lead_status_bar_chart()

    # Prepare data for the interactive chart
    status_counts = Lead.objects.values('status').annotate(count=Count('id'))
    chart_data = {
        'labels': [item['status'] for item in status_counts],
        'data': [item['count'] for item in status_counts],
    }



    return render(request, 'crm_app/home.html', {
        'leads': leads,
        'customers': customers,
        'sort_by': sort_by,
        'query': search_query,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
        'status_bar_chart': status_bar_chart,
        'chart_data': json.dumps(chart_data),
        'lead_page': lead_page,
        'customer_page': customer_page,
        'current_tab': current_tab,  # Pass current tab to template
        'won_leads_count': won_leads_count,
        'lost_leads_count': lost_leads_count,
    })

def generate_status_pie_chart():
    """Generate pie chart for lead status distribution"""
    try:
        status_counts = Lead.objects.values('status').annotate(count=Count('id'))
        
        if not status_counts:
            return None
            
        labels = [entry['status'] for entry in status_counts]
        sizes = [entry['count'] for entry in status_counts]
        
        # Use a modern color palette
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        
        plt.figure(figsize=(8, 6), facecolor='#1a1a2e')
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(sizes)], startangle=140,
                textprops={'color': 'white', 'fontsize': 10, 'fontweight': 'bold'})
        plt.title('Lead Status Distribution', fontsize=14, fontweight='bold', pad=20, color='white')
        plt.axis('equal')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='#1a1a2e', edgecolor='none', transparent=False)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating pie chart: {e}")
        return None

def generate_monthly_lead_bar_chart():
    """Generate bar chart for monthly lead trends"""
    try:
        from django.db.models.functions import TruncMonth
        
        data = (
            Lead.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        if not data:
            return None
            
        months = [d['month'].strftime('%b %Y') for d in data]
        counts = [d['count'] for d in data]
        
        plt.figure(figsize=(10, 6), facecolor='#1a1a2e')
        bars = plt.bar(months, counts, color='#667eea', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                     f'{int(height)}', ha='center', va='bottom', fontweight='bold', color='white')
        
        plt.title('Monthly Lead Trend', fontsize=14, fontweight='bold', pad=20, color='white')
        plt.xlabel('Month', fontsize=12, color='white')
        plt.ylabel('Leads Created', fontsize=12, color='white')
        plt.xticks(rotation=45, color='white')
        plt.yticks(color='white')
        plt.grid(axis='y', alpha=0.3, color='white')
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                   facecolor='#1a1a2e', edgecolor='none', transparent=False)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating bar chart: {e}")
        return None

def generate_lead_status_bar_chart():
    """Generate bar chart for lead status overview"""
    try:
        status_counts = Lead.objects.values('status').annotate(count=Count('id'))
        
        if not status_counts:
            return None
            
        # Sort by count descending
        status_counts = sorted(status_counts, key=lambda x: x['count'], reverse=True)
        
        labels = [entry['status'] for entry in status_counts]
        counts = [entry['count'] for entry in status_counts]
        
        # Create a modern color palette
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
        
        plt.figure(figsize=(10, 6), facecolor='#1a1a2e')
        bars = plt.bar(labels, counts, color=colors[:len(labels)], alpha=0.8)
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                     f'{int(height)}', ha='center', va='bottom', fontweight='bold', color='white')
        
        plt.title('Lead Status Overview', fontsize=14, fontweight='bold', pad=20, color='white')
        plt.xlabel('Status', fontsize=12, color='white')
        plt.ylabel('Number of Leads', fontsize=12, color='white')
        plt.xticks(rotation=45, color='white')
        plt.yticks(color='white')
        plt.grid(axis='y', alpha=0.3, color='white')
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight',
                   facecolor='#1a1a2e', edgecolor='none', transparent=False)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode('utf-8')
    except Exception as e:
        print(f"Error generating status bar chart: {e}")
        return None




# ---------------------------------------------
# 🔹 Add Customer View (includes web scraping company info)
# ---------------------------------------------
def add_customer(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        customer = form.save(commit=False)
        if not customer.company:
            customer.company = get_company_info(customer.name)
        customer.save()
        messages.success(request, "Customer added successfully!")
        return redirect('home')
    return render(request, 'crm_app/form.html', {
        'form': form,
        'title': 'Add Customer',
        'year': datetime.now().year
    })


# ---------------------------------------------
# 🔹 Add Lead View
# ---------------------------------------------
def add_lead(request):
    form = LeadForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'crm_app/form.html', {
        'form': form,
        'title': 'Add Lead',
        'year': datetime.now().year
    })


# ---------------------------------------------
# 🔹 Generate Bar Chart with Matplotlib
# ---------------------------------------------
def generate_lead_chart():
    statuses = Lead.objects.values_list('status', flat=True)
    status_list = list(statuses)
    status_count = {status: status_list.count(status) for status in set(status_list)}

    plt.figure(figsize=(6, 4))
    plt.bar(status_count.keys(), status_count.values(), color='teal')
    plt.title("Lead Status Overview")
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')


# ---------------------------------------------
# 🔹 Export Customers as CSV
# ---------------------------------------------
def export_customers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=customers.csv'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Company', 'Created'])

    for c in Customer.objects.all():
        writer.writerow([c.name, c.email, c.phone, c.company, c.created_at])
    return response


from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404

def send_reminder(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    subject = f"⏰ Follow-up Reminder for {customer.name}"
    message = f"Dear {customer.name},\n\nThis is a reminder to follow up on your pending lead.\n\nBest regards,\nCRM Team"
    from_email = 'your_email@gmail.com'  # Replace with your Gmail or SMTP
    recipient_list = [customer.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        messages.success(request, f"Reminder sent to {customer.name}")
    except Exception as e:
        messages.error(request, f"Failed to send email: {e}")

    return redirect('home')

# views.py
from django.contrib import messages

from django.core.cache import cache

def send_lead_reminders(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    leads = customer.lead_set.all()  # Get all leads for this customer
    
    if not leads:
        messages.warning(request, "No leads found for this customer")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    # Prepare email content with just the leads and their statuses
    subject = f"Your Leads Status - {customer.company or customer.name}"
    message_lines = [f"Dear {customer.name},\n\nHere are your current leads and their statuses:\n"]
    
    for lead in leads:
        message_lines.append(f"- {lead.title}: {lead.status}")
    
    message_lines.append("\nBest regards,\nYour CRM Team")
    message = "\n".join(message_lines)
    
    from_email = 'your_email@gmail.com'  # Replace with your actual email
    recipient_list = [customer.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        messages.success(request, f"Lead statuses sent to {customer.email}")
    except Exception as e:
        messages.error(request, f"Failed to send email: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'home'))
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "Customer updated successfully!")  # Add success message
        return redirect('home')
    return render(request, 'crm_app/form.html', {
        'form': form,
        'title': 'Edit Customer',
        'year': datetime.now().year  # Add year for consistency
    })

from django.http import JsonResponse
# views.py
from django.shortcuts import render
from .models import Lead

def calendar_view(request):
    leads = Lead.objects.exclude(follow_up_date__isnull=True)
    events = []
    for lead in leads:
        events.append({
            'title': lead.title + " - " + lead.customer.name,
            'start': lead.follow_up_date.strftime('%Y-%m-%d')
        })
    return render(request, 'crm_app/calendar.html', {'events': events})

def calendar_events(request):
    """Return calendar events as JSON for FullCalendar"""
    try:
        leads = Lead.objects.select_related('customer').filter(follow_up_date__isnull=False)
        events = []
        
        for lead in leads:
            # Create event with more details
            event = {
                "id": lead.id,
                "title": f"{lead.title} - {lead.customer.name}",
                "start": lead.follow_up_date.strftime('%Y-%m-%d'),
                "allDay": True,
                "backgroundColor": "#667eea",
                "borderColor": "#667eea",
                "textColor": "#ffffff",
                "display": "block",
                "extendedProps": {
                    "customer": lead.customer.name,
                    "status": lead.status,
                    "description": f"Lead: {lead.title}\nCustomer: {lead.customer.name}\nStatus: {lead.status}"
                }
            }
            
            # Color code based on status
            if lead.status == 'won':
                event["backgroundColor"] = "#28a745"
                event["borderColor"] = "#28a745"
            elif lead.status == 'lost':
                event["backgroundColor"] = "#dc3545"
                event["borderColor"] = "#dc3545"
            elif lead.status == 'qualified':
                event["backgroundColor"] = "#ffc107"
                event["borderColor"] = "#ffc107"
                event["textColor"] = "#000000"
            elif lead.status == 'contacted':
                event["backgroundColor"] = "#17a2b8"
                event["borderColor"] = "#17a2b8"
            
            events.append(event)
        
        return JsonResponse(events, safe=False)
        
    except Exception as e:
        print(f"Error generating calendar events: {e}")
        return JsonResponse([], safe=False)

import csv
from django.contrib import messages
from .models import Customer, Lead
from .forms import CSVUploadForm


# crm_app/views.py
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    leads = customer.lead_set.all()  # Get all leads for this customer
    
    return render(request, 'crm_app/customer_detail.html', {
        'customer': customer,
        'leads': leads
    })

def upload_customers_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['csv_file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                Customer.objects.get_or_create(
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    company=row['company']
                )
            messages.success(request, "Customers uploaded successfully!")
            return redirect('home')
    else:
        form = CSVUploadForm()
    return render(request, 'crm_app/upload_csv.html', {'form': form, 'title': 'Upload Customers CSV'})

def upload_leads_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['csv_file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                customer, _ = Customer.objects.get_or_create(name=row['customer'])
                Lead.objects.get_or_create(
                    title=row['title'],
                    customer=customer,
                    status=row['status'],
                    follow_up_date=row['follow_up_date']
                )
            messages.success(request, "Leads uploaded successfully!")
            return redirect('home')
    else:
        form = CSVUploadForm()
    return render(request, 'crm_app/upload_csv.html', {'form': form, 'title': 'Upload Leads CSV'})

import pandas as pd
from django.http import HttpResponse

def export_customers_csv(request):
    customers = Customer.objects.all().values()
    df = pd.DataFrame(customers)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=customers.csv'
    df.to_csv(path_or_buf=response, index=False)
    return response
from django.shortcuts import get_object_or_404
from .forms import LeadForm
from .models import Lead

from django.contrib import messages

def edit_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadForm(request.POST or None, instance=lead)
    if form.is_valid():
        form.save()
        messages.success(request, "Lead updated successfully!")
        return redirect('home')
    return render(request, 'crm_app/form.html', {
        'form': form,
        'title': 'Edit Lead',
        'year': datetime.now().year
    })

def delete_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    lead.delete()
    messages.success(request, "Lead deleted successfully.")
    return redirect('home')

import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db.models import Count
from .models import Lead

def generate_status_pie_chart():
    status_counts = Lead.objects.values('status').annotate(count=Count('id'))

    labels = [entry['status'] for entry in status_counts]
    sizes = [entry['count'] for entry in status_counts]

    colors = ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f']

    plt.figure(figsize=(5, 5))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    plt.title('Lead Status Distribution')
    plt.axis('equal')  # Equal aspect ratio ensures pie is circular.

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    return base64.b64encode(image_png).decode('utf-8')

from django.db.models.functions import TruncMonth
from datetime import datetime

def generate_monthly_lead_bar_chart():
    data = (
        Lead.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    months = [d['month'].strftime('%b %Y') for d in data]
    counts = [d['count'] for d in data]

    plt.figure(figsize=(8, 4))
    plt.bar(months, counts, color='teal')
    plt.title('Monthly Lead Trend')
    plt.xlabel('Month')
    plt.ylabel('Leads Created')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    return base64.b64encode(image_png).decode('utf-8')




from django.contrib import messages
from django.db import transaction

@transaction.atomic
def delete_all_customers(request):
    if request.method == 'POST':
        try:
            count = Customer.objects.all().delete()
            messages.success(request, f"Successfully deleted {count[0]} customers")
        except Exception as e:
            messages.error(request, f"Error deleting customers: {str(e)}")
    return redirect('home')

@transaction.atomic
def delete_all_leads(request):
    if request.method == 'POST':
        try:
            count = Lead.objects.all().delete()
            messages.success(request, f"Successfully deleted {count[0]} leads")
        except Exception as e:
            messages.error(request, f"Error deleting leads: {str(e)}")
    return redirect('home')