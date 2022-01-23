from datetime import datetime
from django.http import HttpRequest, HttpResponse


def year(request: HttpRequest) -> HttpResponse:
    """Add info about year."""
    result = datetime.now()
    Y = datetime.strftime(result, '%Y')
    return {
        'year': Y,
    }
