from django.contrib import admin
from .models import TrendQuery, TrendResult, User, QuerySubscription, SignUpOTP

# Register your models here.
admin.site.register(TrendQuery)
admin.site.register(TrendResult)
admin.site.register(User)
admin.site.register(SignUpOTP)

@admin.register(QuerySubscription)
class QuerySubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "query", "wants_emails", "is_active", "created_at")
    list_filter = ("wants_emails", "is_active")
    search_fields = ("user__email", "query__industry", "query__region")
