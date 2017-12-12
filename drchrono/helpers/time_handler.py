from datetime import datetime

from drchrono.models import Appointments


def start_clock(app):
    now = datetime.now()
    duration = (now - app.start_wait_time).days * 24 * 3600 + (now - app.start_wait_time).seconds
    # if duration < 0:
    #     helper.print_info('clock now', now)
    #     helper.print_info('clock start wait time', app.start_wait_time)
    app.start_wait_time = datetime.now()
    app.waited_time += duration
    app.save()


def stop_clock(app):
    app.start_wait_time = datetime.now()
    app.save()


def check_clock():
    apps = Appointments.objects.filter(status='Arrived')
    for app in apps:
        start_clock(app)
