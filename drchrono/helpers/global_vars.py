from datetime import datetime

import drchrono.helpers.drchrono_request
from drchrono import settings
from drchrono.models import Appointments


# global vars, check daily to clear the set
# if someone arrived in the last day and still waiting, here has problems
class DailyGlobalVarsSet:
    date = datetime.now().date()

    def __init__(self):
        pass

    @classmethod
    def get(cls, user, update_local=False):
        if cls.date != datetime.now().date():
            cls.date = datetime.now().date()
        sync_at_gv = update_local or settings.SYNC_AT_GV
        sync_create_new = update_local or settings.SYNC_CREATE_NEW
        if sync_create_new:
            drchrono.helpers.drchrono_request.sync_appointments(user, sync_at_gv)
        return Appointments.objects.filter(doctor=user.profile.doctor.pk,
                                           scheduled_time__year=DailyGlobalVarsSet.date.year,
                                           scheduled_time__month=DailyGlobalVarsSet.date.month,
                                           scheduled_time__day=DailyGlobalVarsSet.date.day).order_by(
            'scheduled_time')