from django.contrib import admin

from .models import Club, League, PersonalStatistic, Position, Sport, SportStatistic

admin.site.register(Sport)
admin.site.register(Club)
admin.site.register(PersonalStatistic)
admin.site.register(SportStatistic)
admin.site.register(Position)
admin.site.register(League)
