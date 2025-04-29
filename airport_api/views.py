from rest_framework import viewsets, mixins, status
from django.db.models import Prefetch, Q, F, Count
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from airport_api.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Role,
    CrewMember,
    Flight,
    Order, Ticket,
)
from airport_api.pagination import (
    SmallResultSetPagination,
    BigResultSetPagination,
)
from airport_api.permissions import IsAdminUserOrReadOnly
from airport_api.serializers import (
    CitySerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    RoleSerializer,
    CrewMemberSerializer,
    CrewMemberListSerializer,
    CrewMemberRetrieveSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
    FlightFilterSerializer,
    CrewMemberPhotoSerializer,
)


class CityViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = BigResultSetPagination
    permission_classes = (IsAdminUserOrReadOnly,)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        country = self.request.query_params.get("country")
        if country:
            queryset = queryset.filter(city__country__icontains=country)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("city")

        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteRetrieveSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        source_name = self.request.query_params.get("source_name")
        if source_name:
            queryset = queryset.filter(
                destination__city__name__icontains=source_name
            )

        source_id = self.request.query_params.get("source_id")
        if source_id:
            queryset = queryset.filter(
                destination__city__id=source_id
            )

        destination_name = self.request.query_params.get("destination_name")
        if destination_name:
            queryset = queryset.filter(
                destination__city__name__icontains=destination_name
            )

        destination_id = self.request.query_params.get("destination_id")
        if destination_id:
            queryset = queryset.filter(
                destination__city__id=destination_id
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related(
                "source__city", "destination__city"
            )

        return queryset


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        model_name = self.request.query_params.get("model_name")
        if model_name:
            queryset = queryset.filter(model_name__icontains=model_name)

        airplane_type = self.request.query_params.get("airplane_type")
        if airplane_type:
            queryset = queryset.filter(
                airplane_type__name__icontains=airplane_type
            )

        if self.action in ("list", "retrieve"):
            return queryset.select_related("airplane_type")

        return queryset


class RoleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = BigResultSetPagination
    permission_classes = (IsAdminUserOrReadOnly,)


class CrewMemberViewSet(viewsets.ModelViewSet):
    queryset = CrewMember.objects.select_related("role")
    serializer_class = CrewMemberSerializer
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CrewMemberListSerializer
        if self.action == "retrieve":
            return CrewMemberRetrieveSerializer
        if self.action == "upload_photo":
            return CrewMemberPhotoSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role__name__icontains=role)

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                Q(first_name__icontains=name) | Q(last_name__icontains=name)
            )

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("role")

        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload_photo",
    )
    def upload_photo(self, request, pk=None):
        crew_member = self.get_object()
        serializer = self.get_serializer(crew_member, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    pagination_class = SmallResultSetPagination
    permission_classes = (IsAdminUserOrReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        filter_serializer = FlightFilterSerializer(
            data=self.request.query_params
        )
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        if "departure_time_after" in filters:
            queryset = queryset.filter(
                departure_time__gte=filters["departure_time_after"]
            )
        if "departure_time_before" in filters:
            queryset = queryset.filter(
                departure_time__lte=filters["departure_time_before"]
            )
        if "arrival_time_after" in filters:
            queryset = queryset.filter(
                arrival_time__gte=filters["arrival_time_after"]
            )
        if "arrival_time_before" in filters:
            queryset = queryset.filter(
                arrival_time__lte=filters["arrival_time_before"]
            )

        if "source_city" in filters:
            queryset = queryset.filter(
                route__source__city__name=filters["source_city"]
            )
        if "destination_city" in filters:
            queryset = queryset.filter(
                route__destination__city__name=filters["destination_city"]
            )

        if self.action in ("list", "retrieve"):
            queryset = (queryset
            .select_related(
                "route__destination__city",
                "route__source__city",
                "airplane",
            )
            .prefetch_related("crew__role")
            .annotate(
                available_seats=(
                        F("airplane__seats_in_row") * F("airplane__rows")
                        - Count("tickets")
                )
            ))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightRetrieveSerializer

        return self.serializer_class


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = SmallResultSetPagination
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderRetrieveSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action in ("list", "retrieve"):
            tickets_qs = Ticket.objects.select_related(
                "flight__route__source__city",
                "flight__route__destination__city",
            )

            queryset = queryset.prefetch_related(Prefetch(
                "tickets",
                queryset=tickets_qs,
            ))

        return queryset
