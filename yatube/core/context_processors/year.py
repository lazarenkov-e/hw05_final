from datetime import date
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    return {
        'year': date.today().year,
    }
