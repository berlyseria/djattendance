from django.db import models
from django.contrib.postgres.fields import HStoreField
from django_hstore import hstore


from django.contrib.auth.models import Group
from accounts.models import Trainee
from services.models import Worker
import services
import json

from aputils.queryfilter import QueryFilterService

from django.db.models import Prefetch

from django.utils.functional import cached_property

'''
WorkerGroup inherits from django Group so service

designated service
 - permission
regular service
general groups
seasonal groups

View functions:
1st term worker group
sisters worker group

group -> run when add a trainee
validator/updater for workergroups

generic worker groups -> auto-generated

Service Worker Group Trainee Filter Picklist

'''


'''
Will either be a filter workergroup or manual workergroup

WorkerGroup can created via:

 - filter
  - http://ap.ftta.lan/api/trainees/term/2/?format=json&terms%5B%5D=2&terms%5B%5D=3&hc=false

 - manual assignment
 - doodle

Assignments may be
 - static
 - rotational
 - weekly manual assignment


Inherits from Group:
 - name          Required. 80 characters or fewer. Any characters are permitted. Example: 'Awesome Users'.
 - permissions   Many-to-many field to Permission:



?? TODO: make workgroup have types, (e.g. designated)

'''
class WorkerGroup(models.Model):

  # Optional query_filter object. Only this filter or workers
  # manual assignments allowed at a time
  name = models.CharField(max_length=255)
  query_filters = models.TextField(blank=True, null=True)

  description = models.TextField(blank=True, null=True)

  active = models.BooleanField(default=True)

  workers = models.ManyToManyField(
    'Worker', related_name="workergroups", blank=True)

  last_modified = models.DateTimeField(auto_now=True)

  @cached_property
  def get_workers(self):
    if not self.active:
      return []
    if not self.query_filters:
      # then it's a manual list of workers
      workers = self.workers
    else:
      workers = Worker.objects
      # Chain all the filters together to get the composite filter
      for name in self.query_filters.split(','):
        workers = workers.filter(QueryFilterService.get_query(name))
      # Return filtered result
      # return workers

    return workers.select_related('trainee')\
        .prefetch_related(Prefetch('assignments', queryset=services.models.Assignment.objects.order_by('week_schedule__start')),
                          'assignments__service', 'assignments__service_slot')

  def get_worker_list(self):
    workers = self.get_workers
    return ', '.join([w.trainee.full_name for w in workers])


  def __unicode__(self):
    return self.name
