from django.shortcuts import redirect

class BlockOwnerAdminMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            if hasattr(request.user, "ownerprofile"):
                if request.path.startswith("/admin"):
                    return redirect("/dashboard/")

        return self.get_response(request)
