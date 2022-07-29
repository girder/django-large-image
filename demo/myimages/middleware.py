from django.contrib.auth.models import User


class AuthenticationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.user = User.objects.filter()[0]
        except IndexError:
            # HACK: No users in DB yet, make one
            user = User.objects.create_superuser(
                username='admin',
                email='admin@kitware.com',
                password='password',
                is_superuser=True,
            )
            request.user = user
        return self.get_response(request)
