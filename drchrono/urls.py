from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    # url(r'^complete/drchrono/', views.complete, name='complete'),
    url(r'^appointments/$', views.appointment_requests, name ='appointments'),
    url(r'^options/$', views.options, name='options'),
    url(r'^checkin/$', views.check_in, name ='checkin'),
    url(r'^update/$', views.update, name = 'update'),
    url(r'^done/$', views.logged_in, name='done'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
