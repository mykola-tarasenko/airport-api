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
        "name": "Holovnyi",
        "city": sample_city(),
    }
    defaults.update(params)
    return defaults if as_dict else Airport.objects.create(**defaults)
