from airport_api.models import City


def sample_city(as_dict=False, **params):
    defaults = {
        "name": "Odesa",
        "country": "Ukraine"
    }
    defaults.update(params)
    return defaults if as_dict else City.objects.create(**defaults)
