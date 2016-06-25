from django.conf.urls import patterns, url

from bible_tracker import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^changeWeek/$', views.changeWeek, name='changeWeek'),
    url(r'^updateStatus/$', views.updateStatus, name='updateStatus'),
    url(r'^reports/$', views.report, name='report'),
    url(r'^generateReport/$', views.generateReport, name='generateReport'),
)
