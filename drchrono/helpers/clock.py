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
    # apps1 = Appointments.objects.filter(status='Arrived')
    # helper.print_object(apps1, ['waited_time', 'start_wait_time'], 'check clock[db]')
    for app in apps:
        # helper.print_object(apps1, ['waited_time', 'start_wait_time'], 'check clock[gv]')
        now = datetime.now()
        # helper.print_info('clock now', now)
        # helper.print_info('clock start wait time', app.start_wait_time)
        duration = (now - app.start_wait_time).days * 24 * 3600 + (now - app.start_wait_time).seconds
        app.waited_time += duration
        app.start_wait_time = datetime.now()
        app.save()
