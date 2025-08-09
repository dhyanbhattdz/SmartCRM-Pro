from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crm_app.urls')),          # Your main CRM app URLs
    path('accounts/', include('accounts.urls')), # Login/Register URLs
]

