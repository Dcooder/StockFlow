"""Keep browser navigation in the HTML app while retaining JSON APIs for clients."""
from django.shortcuts import redirect


class ApiBrowserRedirectMiddleware:
    """Redirect human browser GETs from API collections to their UI pages.

    API tools normally send ``Accept: application/json`` and therefore keep the
    JSON response. Browsers request HTML and are sent to the equivalent page.
    """
    page_map = {
        "/api/products/": "/products/",
        "/api/categories/": "/categories/",
        "/api/suppliers/": "/suppliers/",
        "/api/stock-movements/": "/stock-movements/",
        "/api/transactions/": "/stock-movements/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        accepts_html = "text/html" in request.headers.get("Accept", "")
        if request.method == "GET" and accepts_html and request.path in self.page_map:
            return redirect(self.page_map[request.path])
        return self.get_response(request)
