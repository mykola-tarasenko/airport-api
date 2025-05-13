from airport_api.models import (
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Role,
)


def sample_city(as_dict=False, **params):
    defaults = {
        "name": "Odesa",
        "country": "Ukraine"
    }
    defaults.update(params)
    return defaults if as_dict else City.objects.create(**defaults)


def sample_airport(as_dict=False, **params):
    defaults = {
        "name": params.get("name") or "Holovnyi",
        "city": params.get("city") or sample_city(),
    }
    return defaults if as_dict else Airport.objects.create(**defaults)


def sample_route(as_dict=False, **params):
    defaults = {
        "source": params.get("source") or sample_airport(),
        "destination": params.get("destination") or sample_airport(
            city=sample_city(name="Lviv"),
        ),
        "distance": params.get("distance") or 700,
    }
    return defaults if as_dict else Route.objects.create(**defaults)


def sample_airplane_type(as_dict=False, **params):
    defaults = {"name": params.get("name") or "Light"}
    return defaults if as_dict else AirplaneType.objects.create(**defaults)


def sample_airplane(as_dict=False, **params):
    defaults = {
        "model_name": "Test-787",
        "rows": 10,
        "seats_in_row": 10,
        "airplane_type": params.get("airplane_type") or sample_airplane_type(),
    }
    return defaults if as_dict else Airplane.objects.create(**defaults)


def sample_role(as_dict=False, **params):
    defaults = {"name": params.get("name") or "Pilot"}
    return defaults if as_dict else Role.objects.create(**defaults)
