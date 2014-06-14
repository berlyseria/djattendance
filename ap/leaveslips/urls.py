from django.conf.urls import patterns, url

from leaveslips import views

urlpatterns = patterns('',
    url(r'individual/create/$', views.IndividualSlipCreate.as_view(), name='individual-create'),
    url(r'individual/(?P<pk>\d+)$', views.IndividualSlipDetail.as_view(), name='individual-detail'),
    url(r'individual/update/(?P<pk>\d+)$', views.IndividualSlipUpdate.as_view(), name='individual-update'),

    url(r'group/create/$', views.GroupSlipCreate.as_view(), name='group-create'),
    url(r'group/(?P<pk>\d+)$', views.GroupSlipDetail.as_view(), name='group-detail'),

    url(r'^$',views.LeaveSlipList.as_view(), name='leaveslips-list'),

)

#     url(r'schedule/list/$', views.ScheduleList.as_view(), name='schedule-list'),
