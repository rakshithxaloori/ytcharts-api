from django.contrib import admin

from yt.models import Channel, Video, AccessKeys, DailyViews, DemographicsViews


admin.site.register(Channel)
admin.site.register(Video)
admin.site.register(AccessKeys)
admin.site.register(DailyViews)
admin.site.register(DemographicsViews)
