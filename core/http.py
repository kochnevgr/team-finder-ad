import json

from django.http import JsonResponse


def json_error(message, status):
    return JsonResponse({"status": "error", "message": message}, status=status)


def parse_request_data(request):
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        return data if isinstance(data, dict) else {}
    return request.POST
