from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^oauth/$', views.oauth, name='oauth'),
    url(r'^identity/$', views.identify, name='identity'),
    url(r'^appointments/$', views.appointment_requests, name='appointments'),
    url(r'^appointments/(?P<app>[0-9]+)/actions/$', views.appointment_actions, name='actions'),
    url(r'^refresh_token/$', views.refresh_token, name='refresh_token'),
    url(r'^checkin/$', views.check_in, name='checkin'),
    url(r'^avatar/$', views.avatar, name='avatar'),
    url(r'^update/$', views.update, name='update'),
    url(r'^main/$', views.main, name='main'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
