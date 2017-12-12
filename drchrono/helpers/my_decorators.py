from functools import wraps

from django.shortcuts import redirect

from drchrono import settings


def association_check(user):
    return user.profile.doctor is not None


def identity_check(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        passed = 'identity' in request.session and request.session['identity'] == 'doctor'
        if passed:
            return function(request, *args, **kwargs)
        else:
            return redirect(settings.IDENTITY_URL)

    return decorator
