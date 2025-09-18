from django.contrib import admin
from .models import TrendQuery, TrendResult, User, QuerySubscription

# Register your models here.
admin.site.register(TrendQuery)
admin.site.register(TrendResult)
admin.site.register(User)

@admin.register(QuerySubscription)
class QuerySubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "query", "wants_emails", "created_at")
    list_filter = ("wants_emails",)
    search_fields = ("user__email", "query__industry", "query__region")
