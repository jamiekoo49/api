from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from .models import Address, Country, State


class UnidentifiedListFilter(SimpleListFilter):
    title = "unidentified"
    parameter_name = "unidentified"

    def lookups(self, request, model_admin):
        return (("unidentified", "unidentified"),)

    def queryset(self, request, queryset):
        if self.value() == "unidentified":
            return queryset.filter(locality=None)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ("name", "code")


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    search_fields = ("name", "code")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ("address_one", "address_two", "postal_code", "state", "country")
    list_filter = (UnidentifiedListFilter,)
