from airport_api.models import (
    City,
    Airport,
    Route,
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
