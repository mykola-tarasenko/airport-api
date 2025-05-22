import re

from django.core.exceptions import ValidationError


def validate_flight_number_format(value):
    if not re.fullmatch(r"[A-Z0-9]{2}\d{1,4}", value):
        raise ValidationError(
            "The flight number must start with 2 uppercase "
            "Latin letters and end with 1 to 4 digits."
        )
