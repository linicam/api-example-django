from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    # url(r'^complete/drchrono/', views.complete, name='complete'),
    url(r'^appointments/$', views.appointment_requests, name='appointments'),
    url(r'^options/$', views.options, name='options'),
    url(r'^alarm/$', views.alarm, name='alarm'),
    url(r'^set_time/$', views.set_alarm_time, name='set_time'),
    url(r'^refresh_token/$', views.refresh_token, name='refresh_token'),
    url(r'^identity/$', views.identify, name='identity'),
    url(r'^checkin/$', views.check_in, name='checkin'),
    url(r'^avatar/$', views.avatar, name='avatar'),
    url(r'^update/$', views.update, name='update'),
    url(r'^feeds/$', views.AppFeed(), name='feeds'),
    url(r'^testapi/$', views.test_api, name='testapi'),
    url(r'^api_tester/$', views.tester, name='tester'),
    # url(r'^update/$', views.update, name='update'),
    url(r'^main/$', views.main, name='main'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^auth/$', views.auth_view, name='auth'),
    url(r'^oauth/$', views.oauth_view, name='oauth'),
    url(r'^register/$', views.register, name='register'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
