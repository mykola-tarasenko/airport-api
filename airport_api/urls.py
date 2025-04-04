from django.urls import path, include
from rest_framework import routers

from airport_api.views import (
    CityViewSet,
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    RoleViewSet,
    CrewMemberViewSet,
)

router = routers.DefaultRouter()
router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("roles", RoleViewSet)
router.register("crew_members", CrewMemberViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
