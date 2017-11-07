from datetime import datetime

import drchrono.helpers.drchrono_request
from drchrono import settings
from drchrono.models import Appointments


# global vars, check daily to clear the set
# if someone arrived in the last day and still waiting, here has problems
class DailyGlobalVarsSet:
    var = {}
    date = datetime.now().date()

    def __init__(self):
        pass

    def __str__(self):
        return self.var.keys()

    @classmethod
    def get(cls, user, update_local=False):
        if cls.date != datetime.now().date():
            cls.date = datetime.now().date()
            cls.initiate()
        if user.pk in cls.var:
            cls.var[user.pk].update(user, update_local)
            return cls.var[user.pk]
        v = GlobalVars()
        v.update(user, settings.SYNC_AT_GV, settings.SYNC_CREATE_NEW)
        cls.var[user.pk] = v
        return cls.var[user.pk]

    @classmethod
    def initiate(cls):
        cls.var = {}


class GlobalVars:
    def __init__(self):
        self.appointments = None

    def update(self, user, update_local=False, create_new_in_db=False):
        if create_new_in_db:
            drchrono.helpers.drchrono_request.sync_appointments(user, update_local)
        self.appointments = Appointments.objects.filter(doctor=user.profile.doctor.pk,
                                                        scheduled_time__year=DailyGlobalVarsSet.date.year,
                                                        scheduled_time__month=DailyGlobalVarsSet.date.month,
                                                        scheduled_time__day=DailyGlobalVarsSet.date.day).order_by(
            'scheduled_time')
