import json

from accounts.models import Trainee
from aputils.decorators import group_required
from aputils.eventutils import EventUtils
from aputils.trainee_utils import trainee_from_user
from braces.views import GroupRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.utils import ErrorList
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import generic
from django.views.generic import CreateView, DeleteView, UpdateView, FormView
from rest_framework import filters, viewsets
from terms.models import Term
from attendance.models import Roll

from .forms import EventForm, CreateScheduleForm, UpdateScheduleForm, DeleteScheduleForm, AfternoonClassForm
from .models import Event, Schedule
from .serializers import (EventFilter, EventSerializer,
                          EventWithDateSerializer, ScheduleFilter,
                          ScheduleSerializer)
from .utils import should_split_schedule, split_schedule, afternoon_class_transfer

@group_required(['training_assistant', 'attendance_monitors'])
def assign_trainees_view(request, pk):
  if request.method == 'POST' and request.is_ajax():
    s = get_object_or_404(Schedule, pk=pk)
    s.assign_trainees()
    messages.success(request, 'Assigned trainees to schedule')
  return JsonResponse({'success': "True"})


@group_required(['training_assistant', 'attendance_monitors'])
def assign_team_schedules(request):
  ws = ','.join([str(x) for x in range(1, 19)])
  for s in Schedule.objects.filter(Q(weeks=ws) & ~Q(team_roll=None)):
    s.assign_trainees()
  return HttpResponse("Assigned trainees to team schedules")


@group_required(['training_assistant', 'attendance_monitors'])
def clear_team_schedules(request):
  ws = ','.join([str(x) for x in range(1, 19)])
  for s in Schedule.objects.filter(Q(weeks=ws) & ~Q(team_roll=None)):
    s.trainees.clear()
  return HttpResponse("Clear trainees from team schedules")


@group_required(['training_assistant', 'attendance_monitors'])
def clear_all_schedules(request):
  for s in Schedule.objects.all():
    s.trainees.clear()
  return HttpResponse("Cleared trainees from all schedules")


class EventDetail(generic.DetailView):
  model = Event
  context_object_name = "event"


class EventDelete(generic.DeleteView):
  model = Event
  success_url = reverse_lazy('schedules:event-create')


class TermEvents(generic.ListView):
  model = Event
  template_name = 'schedules/term_events.html'
  context_object_name = 'events'

  def get_queryset(self, **kwargs):
    return Event.objects.filter(term=Term.decode(self.kwargs['term']))

  def get_context_data(self, **kwargs):
    context = super(TermEvents, self).get_context_data(**kwargs)
    context['term'] = Term.decode(self.kwargs['term'])
    return context


class AllSchedulesView(generic.ListView):
  model = Schedule
  template_name = 'schedules/schedules_list.html'


#  API-ONLY VIEWS  #
class EventViewSet(viewsets.ModelViewSet):
  queryset = Event.objects.all()
  serializer_class = EventWithDateSerializer

  def get_queryset(self):
    if 'trainee' in self.request.GET:
      trainee = Trainee.objects.get(pk=self.request.GET.get('trainee'))
    else:
      user = self.request.user
      trainee = trainee_from_user(user)
    events = trainee.events
    return events

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class ScheduleViewSet(viewsets.ModelViewSet):
  queryset = Schedule.objects.all()
  serializer_class = ScheduleSerializer
  filter_backends = (filters.DjangoFilterBackend,)
  filter_class = ScheduleFilter

  def get_queryset(self):
    trainee = trainee_from_user(self.request.user)
    schedule = Schedule.objects.filter(trainees=trainee)
    return schedule

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllEventViewSet(viewsets.ModelViewSet):
  queryset = Event.objects.all()
  serializer_class = EventSerializer
  filter_backends = (filters.DjangoFilterBackend,)
  filter_class = EventFilter

  def get_queryset(self):
    try:
      week = int(self.request.GET.get('week', ''))
      day = int(self.request.GET.get('weekday', ''))
      date = Term.current_term().get_date(week, day)
      return Event.objects.filter(chart__isnull=False).filter(Q(weekday=day, day__isnull=True) | Q(day=date))
    except ValueError as e:
      print '%s (%s)' % (e.message, type(e))
      return Event.objects.all()

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class AllScheduleViewSet(viewsets.ModelViewSet):
  queryset = Schedule.objects.all()
  serializer_class = ScheduleSerializer
  filter_backends = (filters.DjangoFilterBackend,)
  filter_class = ScheduleFilter

  def allow_bulk_destroy(self, qs, filtered):
    return not all(x in filtered for x in qs)


class EventCRUDMixin(GroupRequiredMixin):
  model = Event
  template_name = 'schedules/admin_form.html'
  form_class = EventForm
  group_required = [u'attendance_monitors', u'training_assistant']


class EventAdminCreate(EventCRUDMixin, CreateView):
  def get_context_data(self, **kwargs):
    ctx = super(EventAdminCreate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Create Event'
    ctx['button_label'] = 'Create'
    return ctx


class EventAdminUpdate(EventCRUDMixin, UpdateView):
  def get_context_data(self, **kwargs):
    ctx = super(EventAdminUpdate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Update Event'
    ctx['button_label'] = 'Update'
    ctx['delete_button'] = True
    return ctx


class EventAdminDelete(EventCRUDMixin, DeleteView):
  success_url = reverse_lazy('schedules:admin-event-create')


class ScheduleCRUDMixin(GroupRequiredMixin):
  model = Schedule
  template_name = 'schedules/admin_form.html'
  # form_class =  BaseScheduleForm
  group_required = [u'attendance_monitors', u'training_assistant']

  # # function that pulls all rolls given the schedule, trainees, and weeks
  # # pull events from schedules, trainees of interest and the weeks range
  # # schedule is a single schedule object
  # # trainees is a queryset of trainees
  # # startWeek and endWeek is a single integer
  # def scheduleRolls(schedule, trainees, startWeek, endWeek):
  #   events_id = schedule.events.values_list('id', flat=True)
  #   trainee_ids = trainees.values_list('id', flat=True)
  #   rolls = Roll.objects.filter(trainee__id__in=trainee_ids, event__id__in=events_id)

  #   current_term = Term.objects.get(current=True)
  #   start_date = current_term.startdate_of_week(startWeek)
  #   end_date = current_term.enddate_of_week(endWeek)
  #   rolls = rolls.filter(date__range=(start_date, end_date)).order_by('trainee', 'date')
  #   return rolls


class ScheduleAdminCreate(ScheduleCRUDMixin, CreateView):
  form_class = CreateScheduleForm

  def get_context_data(self, **kwargs):
    ctx = super(ScheduleAdminCreate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Create Schedule'
    ctx['button_label'] = 'Create'
    return ctx

  def form_invalid(self, form, **kwargs):
    error_data = json.loads(form.errors.as_json())
    errors_list = error_data['__all__']
    rolls_ids = []
    for error in errors_list:
      if error['code'] == 'invalidRolls':
        rolls_to_delete = error['message']
        roll_ids = [int(s) for s in rolls_to_delete[1:-1].split(',')]
        break

    context = self.get_context_data(form=form)
    context['delete_rolls'] = Roll.objects.filter(id__in=roll_ids).order_by('trainee', 'date')
    return self.render_to_response(context)

class ScheduleAdminUpdate(ScheduleCRUDMixin, UpdateView):
  form_class = UpdateScheduleForm

  def get_context_data(self, **kwargs):
    ctx = super(ScheduleAdminUpdate, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Update Schedule'
    ctx['button_label'] = 'Update'
    ctx['delete_button'] = True
    ctx['split_button'] = True
    ctx['assign_trainees_button'] = True
    return ctx

  # def form_valid(self, form):

  #   new_schedule = form.instance
  #   cur_schedule = Schedule.objects.get(id=new_schedule.id)

  #   new_set = new_schedule.trainees.all()
  #   current_set = cur_schedule.trainees.all()

  #   # If the trainee sets are identical, minor schedule update
  #   to_add = new_set.exclude(pk__in=current_set)
  #   to_delete = current_set.exclude(pk__in=new_set)

  #   if not to_add and not to_delete:
  #     return super(ScheduleAdminUpdate, self).form_valid(form)

  #   for t in to_delete:
  #     # trainee cannot be moved off of a schedule if there are rolls for events on that schedule
  #     t_events = t.rolls.order_by('event').distinct('event').values_list('event__id', flat=True)
  #     if cur_schedule.events.filter(id__in=t_events).exists():
  #       form._errors[NON_FIELD_ERRORS] = ErrorList([u'Trainee(s) cannot be removed from schedule. Split the schedule.'])
  #       return super(ScheduleAdminUpdate, self).form_invalid(form)

  #   for t in to_add:
  #     # trainee cannot be moved onto a schedule if there are rolls for events on a schedule that it will overlap
  #     sch_event_set = cur_schedule.events.values('event__id', 'event__start', 'event__end')
  #     tr_event_set = t.rolls.order_by('event').distinct('event').values('event__id', 'event__start', 'event__end')
  #     for i in tr_event_set:
  #       for j in sch_event_set:
  #         if EventUtils.time_overlap(i['event__start'], i['event__end'], j['event__start'], j['event__end']):
  #           form._errors[NON_FIELD_ERRORS] = ErrorList([u'Trainee(s) cannot be added to schedule. Split the schedule.'])
  #           return super(ScheduleAdminUpdate, self).form_invalid(form)

  #   return super(ScheduleAdminUpdate, self).form_valid(form)


class ScheduleAdminDelete(ScheduleCRUDMixin, DeleteView):
  form_class = DeleteScheduleForm
  success_url = reverse_lazy('attendance:schedules-viewer')


@group_required(['training_assistant', 'attendance_monitors'])
def split_schedules_view(request, pk, week):
  if request.method == 'POST' and request.is_ajax():
    schedule = Schedule.objects.get(id=pk)
    if should_split_schedule(schedule, int(week)):
      curr, first_half, second_half = split_schedule(schedule, int(week))
      if second_half is not None:
        return JsonResponse({'success': second_half.get_absolute_url()})
      else:
        return JsonResponse({'failed': 'failed'})
  return HttpResponse(status=204)


# this class uses AfternoonClassForm with three inputs, trainees_id, event, and week
# uses function in utils called afternoon_class_transfer that moves traines onto the chosen schedule for the event
# returns string to indicate whether the transfer was successful or not
# there may be loopholes not found in certain circumnstancs --- Benji
class AfternoonClassChange(FormView):
  template_name = 'schedules/afternoon_class.html'
  form_class = AfternoonClassForm
  success_url = reverse_lazy('schedules:afternoon-class-change')

  def get_context_data(self, **kwargs):

    ctx = super(AfternoonClassChange, self).get_context_data(**kwargs)
    ctx['page_title'] = 'Afternoon Classes Changes'

    aftn_evs_code = Event.objects.filter(class_type='AFTN', weekday=3, monitor='AM').values('name', 'code')
    ctx['class_options'] = aftn_evs_code
    return ctx

  def get_form_kwargs(self):

    afternoon_classes = list(Event.objects.filter(class_type='AFTN', weekday=3, monitor='AM').values_list('code', 'name').order_by('name'))
    afternoon_classes.insert(0, ('', '---'))

    kwargs = super(AfternoonClassChange, self).get_form_kwargs()
    kwargs['event_choices'] = afternoon_classes

    return kwargs

  def form_valid(self, form):
    data = dict(form.data.iterlists())
    start_week = int(data['week'][0])
    trainees_ids = data['trainees']
    e_code = str(data['event'][0])
    for t_id in trainees_ids:
      t = Trainee.objects.get(pk=t_id)
      mess = afternoon_class_transfer(t, e_code, int(start_week))
      messages.success(self.request, mess)

    return super(AfternoonClassChange, self).form_valid(form)

