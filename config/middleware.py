from django.utils.cache import add_never_cache_headers


class NoCacheAuthenticatedMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        # --------------------------------------------------
        # Prevent authenticated pages from being cached
        # --------------------------------------------------

        if request.user.is_authenticated:

            add_never_cache_headers(response)

            response["Cache-Control"] = (
                "no-store, "
                "no-cache, "
                "must-revalidate, "
                "max-age=0, "
                "private"
            )

            response["Pragma"] = "no-cache"

            response["Expires"] = "0"

        return response