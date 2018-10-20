# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render
from django.views.generic.edit import DeleteView
from django.views.generic import TemplateView
from django.http import HttpResponse

from .models import GospelStat
from terms.models import Term
from accounts.models import Trainee

from datetime import *

from braces.views import GroupRequiredMixin

#ctx[cols] = attributes
attributes = ['Tracts Distributed','Bibles Distributed','Contacted (>30 sec)','Led to Pray','Baptized','2nd Appointment','Regular Appointment','Minutes on the Gospel','Bible Study','Small Groups','District Meeting (New Student)','Conference']
_attributes = ['Tracts_Distributed','Bibles_Distributed','Contacted_(>30_sec)','Led_to_Pray','Baptized','2nd_Appointment','Regular_Appointment','Minutes_on_the_Gospel','Bible_Study','Small_Groups','District_Meeting_(New_Student)','Conference']
ctx = dict()
for i in _attributes:
  ctx[i]=0

def get_week():
  for i in range(0,21):
    if Term.current_term().startdate_of_week(i) <= date.today() and Term.current_term().enddate_of_week(i) >= date.today():
      return i

#In Progress
class GospelStatisticsView(TemplateView):
  template_name = "gospel_statistics/gospel_statistics.html"

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    context = super(GospelStatisticsView, self).get_context_data(**kwargs)
    context['page_title'] = 'Team Statistics'
    context['team'] = current_user.team
    #delete
    context['gospel_pairs'] = current_user.firstname+' '+current_user.lastname
    context['cols'] = attributes
    context['week'] = get_week()
    return context

class NewGospelPairView(TemplateView):
  template_name = "gospel_statistics/new_pair.html"

  def get_context_data(self, **kwargs):
    current_user = self.request.user
    context = super(NewGospelPairView, self).get_context_data(**kwargs)
    context['page_title'] = 'New Gospel Pair'
    context['team'] = current_user.team
    return context

def weekly_statistics(request):
  current_week = get_week()
  current_team = request.user.team
  stats = GospelStat.objects.filter(week=current_week)
  weekly_stats = []
  gps = []
  #Get all existing gospel pairs
  for stat in stats:
    print stat.trainees
  return HttpResponse(json.dumps(weekly_stats))

#In Progress (change to class)
def TAGospelStatisticsView(request):
  context = {
    'page_title': 'TA Gospel Statistics',
  }
  return render(request, 'gospel_statistics/index.html', context=context)