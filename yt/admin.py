from django.contrib import admin

from yt.models import (
    FetchStatus,
    Channel,
    Video,
    AccessKeys,
    TopCountry,
    DailyViews,
    Demographics,
)


admin.site.register(FetchStatus)
admin.site.register(Channel)
admin.site.register(Video)
admin.site.register(AccessKeys)
admin.site.register(TopCountry)
admin.site.register(DailyViews)
admin.site.register(Demographics)
