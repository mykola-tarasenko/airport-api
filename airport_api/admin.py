from django.contrib import admin

from airport_api.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Flight,
    Airplane,
    Role,
    CrewMember,
    Order,
    Ticket,
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country")


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    search_fields = ("name", "city__name")
    list_filter = ("city__country",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__city__name", "destination__city__name")


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("model_name", "type", "capacity")
    search_fields = ("model_name", "type__name")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role")
    search_fields = ("first_name", "last_name")
    list_filter = ("role__name",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("flight_number", "route", "airplane", "status")
    search_fields = ("flight_number",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)
    list_display = ("user", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("passenger_full_name", "flight__route", "flight__flight_number")
    search_fields = ("flight__flight_number",)

    @admin.display(description="passenger_full_name")
    def passenger_full_name(self, obj):
        return f"{obj.passenger_first_name} {obj.passenger_last_name}"
