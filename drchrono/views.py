from datetime import datetime

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.syndication.views import Feed
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views.decorators.http import require_http_methods, require_GET, require_POST

import drchrono.helpers.drchrono_request
import drchrono.models
from drchrono import settings
from drchrono.helpers import clock, my_forms, helper, drchrono_request
from drchrono.helpers.decorator import association_check, identity_check
from drchrono.helpers.drchrono_request import DrchronoRequest
from drchrono.helpers.global_vars import DailyGlobalVarsSet
from drchrono.helpers.my_forms import CheckInForm, AvatarForm
from drchrono.models import Appointments, Notification, Patient


@require_GET
def home(request):
    if request.user.is_authenticated():
        if association_check(request.user):
            return redirect('/identity')
        return redirect('/oauth')
    c = {}
    c.update(csrf(request))
    return render_to_response('home.html', c, RequestContext(request))


@require_POST
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)
        if association_check(request.user):
            return redirect('/identity')
        return redirect('/oauth')
    else:
        messages.error(request, 'invalid login info')
        return redirect('/')


@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/oauth')
        else:
            messages.error(request, 'already existed or invalid register info')
            return redirect('/register')
    form = UserCreationForm()
    return render_to_response('register.html', {'form': form}, RequestContext(request))


@login_required
@require_GET
def oauth_view(request):
    if association_check(request.user):
        return redirect('/identity')
    return render_to_response('oauth.html', context=RequestContext(request))


@login_required
@require_POST
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
@require_POST
def avatar(request):
    form = AvatarForm(request.POST, request.FILES, instance=request.user.profile)
    if form.is_valid():
        form.save()
        messages.success(request, "Update successfully")
    else:
        messages.error(request, "invalid avatar file")
    # u = User.objects.get(pk=request.user.pk)
    return redirect('/main', RequestContext(request))


@login_required
@user_passes_test(association_check, login_url='oauth')
@require_http_methods(["GET", "POST"])
def identify(request):
    if request.method == 'GET':
        if 'identity' not in request.session:
            form = my_forms.IdentityForm(auto_id=False)
            return render_to_response('identity.html', {
                'form': form,
            }, RequestContext(request))
        elif request.session['identity'] == 'doctor':
            return redirect('/main')
        elif request.session['identity'] == 'patient':
            return redirect('/checkin')
        else:
            return HttpResponseBadRequest('invalid identity')
    elif request.method == 'POST':
        identity = request.POST['identity']
        request.session['identity'] = identity
        if identity == 'doctor':
            return redirect('/main')
        elif identity == 'patient':
            return redirect('/checkin')


@login_required
@user_passes_test(association_check, login_url='/oauth')
@identity_check
@require_GET
def alarm(request):
    apps = drchrono_request.get_future_appointments(request.user,
                                                    settings.SYNC_AT_GV, settings.SYNC_CREATE_NEW)

    form = my_forms.DateTimeForm()
    return render_to_response('alarm.html', {
        'appointments': apps,
        'form': form,
    }, RequestContext(request))


@login_required
@user_passes_test(association_check, login_url='/oauth')
@identity_check
@require_POST
def set_alarm_time(request):
    helper.print_info('set alarm time', request.POST['time'])
    return HttpResponse('Success')


@login_required
@user_passes_test(association_check, login_url='/oauth')
@identity_check
@require_GET
def main(request):
    DailyGlobalVarsSet.get(request.user)
    return render_to_response('main.html', {
        'user': request.user,
        'form': AvatarForm(instance=request.user)
    }, RequestContext(request))


@login_required
@user_passes_test(association_check, login_url='/oauth')
@identity_check
@require_POST
def refresh_token(request):
    # return HttpResponse('being test')
    # print '====refresh token====='
    DrchronoRequest.token_request(request.user)
    # DrchronoRequest.revoke_token_request(request.user)
    return HttpResponse('finished')


@login_required
@user_passes_test(association_check, login_url='/oauth')
@identity_check
@require_http_methods(["GET", "POST"])
def appointment_requests(request):
    force_syn = request.method == 'POST'
    gv = DailyGlobalVarsSet.get(request.user, force_syn)

    if not request.user.profile.in_session:
        clock.check_clock(gv)
        gv = DailyGlobalVarsSet.get(request.user)
    appointments = gv.appointments
    if force_syn:
        return HttpResponse('update succeed')
    else:
        waited_patients = Appointments.objects.filter(waited_time__gt=0)
        waited_times = waited_patients.values_list('waited_time', flat=True)
        average_wait_time = sum(waited_times) * 1.0 / len(waited_patients) if len(waited_patients) else 0
        ntfs = Notification.objects.filter(user=request.user, tag=Notification.INFO)
        print len(ntfs)
        Notification.objects.filter(user=request.user, tag=Notification.INFO).delete()
        print ntfs

        return render_to_response('appointments.html', {
            'appointments': appointments,
            'average_wait_time': average_wait_time,
            'in_session': request.user.profile.in_session,
            'notifications': ntfs,
        }, RequestContext(request))


@login_required()
@user_passes_test(association_check, login_url='/oauth')
@identity_check
@require_POST
def options(request):
    user = request.user
    gv = DailyGlobalVarsSet.get(user)
    appointment = request.POST['appointment']
    option = request.POST['option']

    target_app = gv.appointments.filter(appointment=appointment)
    if len(target_app) < 1:
        return Http404('can\'t find appointment')
    target_app = target_app[0]

    if option == 'start':
        if user.profile.in_session:
            return HttpResponseBadRequest('in session')
        user.profile.in_session = appointment
        clock.start_clock(gv)
        status = 'In Room'
        pass
    elif option == 'end':
        if not user.profile.in_session:
            return HttpResponseBadRequest('no session')
        user.profile.in_session = None
        clock.stop_clock(gv)
        status = 'Complete'
    else:
        return HttpResponseBadRequest('wrong option request')
    user.save()
    params = {
        'status': status,
        'appointment': target_app.appointment
    }
    res, content = DrchronoRequest.appointment_request(request.user, params, method='PATCH')
    if res >= 400:
        return HttpResponse(helper.get_error_msg(res, content), status=res)
    target_app.status = status
    target_app.save()
    return HttpResponse(option + 'succeed')


@login_required
@user_passes_test(association_check, login_url='/oauth')
@identity_check
@require_http_methods(["GET", "POST"])
def tester(request):
    if request.method == 'GET':
        return render_to_response('api_tester.html')
    elif request.method == 'POST':
        pass


@login_required
@user_passes_test(association_check, login_url='/oauth')
@require_http_methods(["GET", "POST"])
def check_in(request):
    # helper.print_objects(Patient.objects.all(), title='patients')
    if 'patient' in request.session:
        del request.session['patient']
    if 'appointment' in request.session:
        del request.session['appointment']
    gv = DailyGlobalVarsSet.get(request.user)
    if request.method == 'GET':
        form = CheckInForm(auto_id=False)
        return render_to_response('check_in.html', {
            'form': form,
            'identity': request.session['identity'] == 'doctor'
        }, RequestContext(request))
    elif request.method == 'POST':
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        ssn = request.POST['ssn'].strip()

        args = {
            'time': settings.REDIRECT_TIME,
            'first_name': first_name,
            'last_name': last_name,
        }
        appointments = gv.appointments.filter(
            Q(status__in=['Confirmed', 'Rescheduled', '', 'In Session', 'Arrived', 'In Room']) |
            Q(status__isnull=True)).filter(scheduled_time__gte=datetime.now())
        if len(first_name) > 0 and len(last_name) > 0:
            appointments = appointments.filter(patient__last_name__iexact=last_name,
                                               patient__first_name__iexact=first_name)
        # helper.print_object(appointments, ['status'], 'checkin')
        if ssn is not None and ssn != '':
            appointments = appointments.filter(patient__ssn=ssn)

        l = len(appointments)
        if l < 1:
            messages.error(request, 'No appointment find')
        # elif l > 1:
        #     messages.error(request, 'Can not target patient')
        elif len(appointments.filter(status__in=['Arrived', 'In Room'])) > 0:
            messages.error(request, 'Already checked in')
        else:
            appointment = appointments[0]
            request.session['patient'] = appointment.patient_id
            request.session['appointment'] = appointment.pk

            patient = Patient.objects.get(pk=appointment.patient_id)
            messages.info(request, 'Welcome, {0} {1}!'.format(patient.first_name, patient.last_name))
            return redirect('/update')
        # helper.print_objects(get_messages(request))
        return render_to_response('check_in_result.html', args, RequestContext(request))


@require_GET
def test_api(request):
    patient = request.session['patient']
    appointment = request.session['appointment']
    res = DrchronoRequest.test_request(request.user, {
        'patient': patient,
        'appointment': appointment,
    })
    return redirect('/update')


@login_required()
@user_passes_test(association_check, login_url='/oauth')
@require_http_methods(["GET", "POST"])
def update(request):
    patient = request.session['patient']
    DailyGlobalVarsSet.get(request.user)
    if request.method == 'GET':
        p = Patient.objects.get(pk=patient)
        form = my_forms.UpdateForm(auto_id=False, initial={
            'city': p.city,
            'date_of_birth': p.date_of_birth,
            'address': p.address,
            'cell_phone': p.cell_phone,
        })
        return render_to_response('update.html', {
            'form': form,
        }, RequestContext(request))
    elif request.method == 'POST':
        form = my_forms.UpdateForm(request.POST)
        if form.is_valid() and helper.check_cell_phtone(request.POST['cell_phone']):
            p = Patient.objects.filter(pk=patient)
            p.update(**form.cleaned_data)

            params = form.cleaned_data
            params['patient'] = patient
            res, content = DrchronoRequest.patients_request(request.user, params, method='PATCH')
            if res >= 400:
                messages.error(request, "Server error: {0} {1}".format(res, content))
            else:
                # res, content = DrchronoRequest.patients_request(request.user, {'patient': patient})
                # print res, content
                appointment = request.session['appointment']
                params = {
                    'status': 'Arrived',
                    'appointment': appointment
                }
                res, content = DrchronoRequest.appointment_request(request.user, params, method='PATCH')
                if res >= 400:
                    return HttpResponse(helper.get_error_msg(res, content), status=res)
                app = Appointments.objects.get(pk=appointment)
                app.status = 'Arrived'
                app.start_wait_time = datetime.now()
                app.check_in_time = datetime.now()
                app.save()
                drchrono.models.create_notification(app)

                messages.info(request, "You've successfully checked in for appointment scheduled at {0}".format(
                    app.scheduled_time.strftime(settings.DISPLAY_DATETIME_FORMAT)))
                # messages.success(request, "Successfully updated personal Info")
        else:
            messages.error(request, "Invalid info")
        return render_to_response('update_result.html', {'time': settings.REDIRECT_TIME}, RequestContext(request))


class AppFeed(Feed):
    link = '/feeds/'

    def item_link(self, item):
        return '/feeds/'

    def get_object(self, request, *args, **kwargs):
        return request.user

    def items(self, obj):
        gv = DailyGlobalVarsSet.get(obj)
        return gv.appointments
        # return Appointments.objects.filter(doctor=obj.profile.doctor.pk,
        #                                    scheduled_time__year=DailyGlobalVarsSet.date.year,
        #                                    scheduled_time__month=DailyGlobalVarsSet.date.month,
        #                                    scheduled_time__day=DailyGlobalVarsSet.date.day).order_by('scheduled_time')

    def item_title(self, item):
        return "{0} {1}".format(item.patient.first_name, item.patient.last_name)

    def item_description(self, item):
        return str(item.duration)
        # return {
        #     'scheduled_time': item.scheduled_time,
        #     'waited_time': item.waited_time
        # }
