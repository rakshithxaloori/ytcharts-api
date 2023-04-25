from django.contrib import admin

from emails.models import Email, ChartPNG, EmailChartPNG

admin.site.register(Email)
admin.site.register(ChartPNG)
admin.site.register(EmailChartPNG)
