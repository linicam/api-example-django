from datetime import datetime

from drchrono.helpers import helper


def start_clock(gv):
    apps = gv.appointments.filter(status='Arrived')
    for app in apps:
        now = datetime.now()
        duration = (now - app.start_wait_time).seconds
        app.waited_time += duration
        app.save()


def stop_clock(gv):
    apps = gv.appointments.filter(status='Arrived')
    for app in apps:
        app.start_wait_time = datetime.now()
        app.save()


def check_clock(gv):
    apps = gv.appointments.filter(status='Arrived')
    for app in apps:
        now = datetime.now()
        duration = (now - app.start_wait_time).days * 24 * 3600 + (now - app.start_wait_time).seconds
        if duration < 0:
            helper.print_info('clock now', now)
            helper.print_info('clock start wait time', app.start_wait_time)
        app.waited_time += duration
        app.start_wait_time = datetime.now()
        app.save()
