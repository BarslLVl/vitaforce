from django.shortcuts import redirect

class BannedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.groups.filter(name='Banned').exists():
            return redirect('banned_page')
        return self.get_response(request)
