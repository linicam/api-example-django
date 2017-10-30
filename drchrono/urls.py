from django.conf.urls import include, url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^complete/drchrono/$', TemplateView.as_view(template_name='complete.html'), name='complete'),

    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
