from airport_api.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Role,
    CrewMember,
    Flight,
)


def sample_city(as_dict=False, **params):
    defaults = {
        "name": "Odesa",
        "country": "Ukraine",
    }
    defaults.update(params)
    return defaults if as_dict else City.objects.get_or_create(**defaults)[0]


def sample_airport(as_dict=False, **params):
    defaults = {
        "name": "Holovnyi",
        "city": sample_city(),
    }
    defaults.update(params)
    return defaults if as_dict else Airport.objects.get_or_create(**defaults)[0]


def sample_route(as_dict=False, **params):
    defaults = {
        "source": sample_airport(),
        "destination": sample_airport(city=sample_city(name="Lviv")),
        "distance": 700,
    }
    defaults.update(params)
    return defaults if as_dict else Route.objects.get_or_create(**defaults)[0]


def sample_airplane_type(as_dict=False, **params):
    defaults = {"name": params.get("name") or "Light"}
    return defaults if as_dict else AirplaneType.objects.get_or_create(**defaults)[0]


def sample_airplane(as_dict=False, **params):
    defaults = {
        "model_name": "Test-787",
        "rows": 10,
        "seats_in_row": 10,
        "airplane_type": sample_airplane_type(),
    }
    defaults.update(params)
    return defaults if as_dict else Airplane.objects.get_or_create(**defaults)[0]


def sample_role(as_dict=False, **params):
    defaults = {"name": params.get("name") or "Pilot"}
    return defaults if as_dict else Role.objects.get_or_create(**defaults)[0]


def sample_crew_member(as_dict=False, **params):
    defaults = {
        "first_name": "Anton",
        "last_name": "Antonenko",
        "role": sample_role(),
    }
    defaults.update(params)
    return defaults if as_dict else CrewMember.objects.get_or_create(**defaults)[0]


def sample_flight(as_dict=False, **params):
    defaults = {
        "flight_number": "UA1234",
        "route": sample_route(),
        "airplane": sample_airplane(),
        "departure_time": "2025-5-1 18:00+00:00",
        "arrival_time": "2025-5-1 21:00+00:00",
        "status": 1,
    }
    defaults.update(params)
    return defaults if as_dict else Flight.objects.get_or_create(**defaults)[0]
