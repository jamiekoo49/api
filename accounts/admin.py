from django.contrib import admin

from .models import Account, Athlete, Coach, NotificationToken, Payment

admin.site.register(Account)
admin.site.register(Payment)


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ("user", "uuid")
    readonly_fields = ("uuid",)


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("user", "university", "uuid")
    readonly_fields = ("uuid",)


@admin.register(NotificationToken)
class NotificationTokenAdmin(admin.ModelAdmin):
    list_display = ("account", "token", "created_at")
    readonly_fields = ("created_at",)
