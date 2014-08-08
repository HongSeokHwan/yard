from django.conf.urls import patterns, url

from yard.apps.study import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'quotedata', views.quotedata, name='quotedata')
)
