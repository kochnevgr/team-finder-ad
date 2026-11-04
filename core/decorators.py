from functools import wraps
from http import HTTPStatus

from core.http import json_error


def login_required_json(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return json_error("Требуется авторизация", HTTPStatus.UNAUTHORIZED)
        return view_func(request, *args, **kwargs)

    return wrapper
