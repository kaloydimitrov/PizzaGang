from django.http import HttpResponseNotFound
from django.template.loader import get_template


class ExceptionHandler:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            template = get_template('404.html')
            response = HttpResponseNotFound(template.render())
        elif response.status_code >= 500:
            template = get_template('500_server_errors.html')
            response = HttpResponseNotFound(template.render())
        return response
