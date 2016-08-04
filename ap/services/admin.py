from django.contrib import admin
from django import forms

from services.models import *

from django_hstore.widgets import BaseAdminHStoreWidget, GrappelliAdminHStoreWidget, SuitAdminHStoreWidget

from django_hstore.forms import DictionaryField

from aputils.admin_utils import FilteredSelectMixin

from aputils.queryfilter import QueryFilterService
from aputils.custom_fields import CSIMultipleChoiceField

class WorkerExceptionInline(admin.TabularInline):
    model = Exception.workers.through
    # fields = ['exception__name']
    readonly_fields = ['name', 'start', 'end', 'active', 'workers']
    extra = 1
    def name(self, instance):
      return instance.exception.name

    def start(self, instance):
      return instance.exception.start

    def end(self, instance):
      return instance.exception.end

    def active(self, instance):
      return instance.exception.active

    def workers(self, instance):
      return instance.exception.get_worker_list()

    extra = 1
    suit_classes = 'suit-tab suit-tab-exception'



class WorkerAdmin(admin.ModelAdmin):
  inlines = [
    WorkerExceptionInline,
  ]
  list_display = ('trainee', 'health', 'services_cap')
  # list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
  ordering = ('trainee__firstname',)
  search_fields = ['trainee__email', 'trainee__firstname', 'trainee__lastname']
  list_filter = ('health', 'services_cap')
  filter_horizontal = ('designated', 'services_eligible', 'qualifications')
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  fieldsets = (
    (None, {
      'classes': ('suit-tab', 'suit-tab-worker',),
      'fields': ('trainee', 'health', 'services_cap', 'qualifications', 'designated', 'services_eligible')
     }),
    )

  suit_form_tabs = (('worker', 'General'),
                    ('exception', 'Exceptions'),
                  )

  class Meta:
    model = Worker
    fields = '__all__'


class SeasonalServiceScheduleForm(forms.ModelForm):
  services = forms.ModelMultipleChoiceField(
    label='Services',
    queryset=Service.objects.all(),
    required=False,
    widget=admin.widgets.FilteredSelectMultiple(
      'services', is_stacked=False))

  class Meta:
    model = SeasonalServiceSchedule
    exclude = []
    widgets = {
    'services': admin.widgets.FilteredSelectMultiple(
      'services', is_stacked=False),
    }

class SeasonalServiceScheduleAdmin(FilteredSelectMixin, admin.ModelAdmin):
  form = SeasonalServiceScheduleForm
  registered_filtered_select = [('services', Service), ]

  list_display = ('name', 'description', 'category', 'active')
  ordering = ('name', 'active')
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  class Meta:
    model = SeasonalServiceSchedule
    fields = '__all__'


class WorkerGroupInline(admin.StackedInline):
    model = Service.worker_groups.through
    fields = ['name', 'workers_required', 'workload', 'role', 'worker_group']
    extra = 1
    def worker_group(self, instance):
        return instance.worker_group.name
    worker_group.short_description = 'worker group'

    suit_classes = 'suit-tab suit-tab-workergroup'


class ServiceSlotAdmin(admin.ModelAdmin):
  list_display = ('service', 'worker_group', 'workers_required', 'role')
  # list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
  ordering = ('service', 'worker_group',)
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  class Meta:
    model = Worker
    fields = '__all__'

class ServiceExceptionInline(admin.TabularInline):
    model = Exception.services.through
    # fields = ['exception__name']
    readonly_fields = ['name', 'start', 'end', 'active', 'workers']
    extra = 1
    def name(self, instance):
      return instance.exception.name

    def start(self, instance):
      return instance.exception.start

    def end(self, instance):
      return instance.exception.end

    def active(self, instance):
      return instance.exception.active

    def workers(self, instance):
      return instance.exception.get_worker_list()

    extra = 1
    suit_classes = 'suit-tab suit-tab-exception'


class ServiceInline(admin.StackedInline):
  model = Service
  fk_name = 'category'
  extra = 1


class CategoryAdmin(admin.ModelAdmin):

  list_display = ('name', 'description')
  ordering = ('name',)
  inlines = [
    ServiceInline,
  ]
  # exclude= ('permissions',)
  # Allows django admin to duplicate record
  # save_as = True

  class Meta:
    model = Category
    fields = '__all__'



class ServiceAdminForm(admin.ModelAdmin):
  inlines = [
    WorkerGroupInline,
    ServiceExceptionInline,
    # ExceptionInline,
  ]

  list_display = ('name', 'code', 'category', 'active', 'weekday', 'start', 'end', 'day')
  ordering = ('name', 'active', 'weekday', 'day')
  exclude= ('exceptions',)
  filter_horizontal = ('schedule',)
  # Allows django admin to duplicate record
  # save_as = True

  fieldsets = (
    (None, {
      'classes': ('suit-tab', 'suit-tab-service',),
      'fields': ('name', 'code', 'category', 'schedule',
                'active', 'designated', 'weekday', 'start',
                'end', 'day')
     }),
    )

  suit_form_tabs = (('service', 'General'),
                    ('workergroup', 'Worker Slots'),
                    ('exception', 'Exceptions'),
                  )


  class Meta:
    model = Service
    fields = '__all__'


class WorkGroupAdminForm(forms.ModelForm):

  query_filters = CSIMultipleChoiceField(choices=QueryFilterService.get_choices(), required=False, label='Filters')

  class Meta:
    model = WorkerGroup
    fields = '__all__'


class WorkerGroupAdmin(admin.ModelAdmin):
  form = WorkGroupAdminForm
  list_display = ('name', 'description', 'active', 'get_worker_list')#, 'query_filters')
  ordering = ('active', 'name')
  exclude= ('permissions',)
  readonly_fields = ['worker_count', 'get_worker_list']
  # Allows django admin to duplicate record
  # save_as = True

  fieldsets = (
    (None, {
      'classes': ('suit-tab', 'suit-tab-general',),
      'fields': ('name', 'description', 'active', 'query_filters', 'workers')
     }),
    ('Preview', {
      'classes': ('suit-tab', 'suit-tab-preview',),
      'fields': ('worker_count', 'get_worker_list',)
      }),
    )

  suit_form_tabs = (('general', 'General'),
                    ('preview', 'Filter Preview'),)

  def worker_count(self, obj):
    return obj.get_workers().count()

  def get_worker_list(self, obj):
    return obj.get_worker_list()
  get_worker_list.short_description = "Trainees after Applying Filter"

  class Meta:
    model = WorkerGroup
    fields = '__all__'


class ExceptionAdmin(admin.ModelAdmin):
  list_display = ('name', 'tag', 'desc', 'start', 'end', 'active')
  ordering = ('active', 'name')

  filter_horizontal = ('workers', 'services')
  search_fields = ('name', 'desc',)
  list_filter = ('active', 'tag', 'start', 'end')
  # inlines = [
  #   ServiceInline,
  # ]

  # exclude = ('services',)

  class Meta:
    model = Exception
    fields = '__all__'


class QualificationForm(forms.ModelForm):
  workers = forms.ModelMultipleChoiceField(
    label='Workers',
    queryset=Worker.objects.all(),
    required=False,
    widget=admin.widgets.FilteredSelectMultiple(
      'workers', is_stacked=False))

  class Meta:
    model = Qualification
    exclude = []
    widgets = {
    'workers': admin.widgets.FilteredSelectMultiple(
      'workers', is_stacked=False),
    }


class QualificationAdmin(FilteredSelectMixin, admin.ModelAdmin):
  form = QualificationForm
  registered_filtered_select = [('workers', Worker), ]
  # inlines = [

  # ]
  list_display = ('name', 'desc')
  ordering = ('name',)


  class Meta:
    model = Qualification
    fields = '__all__'

# from seasonal_service_schedule import *
# from service import *
# from worker import *
# from workergroup import *
# from exception import *
# from assignment import *
# from week_schedule import *

admin.site.register(ScheduleCategory)
admin.site.register(SeasonalServiceSchedule, SeasonalServiceScheduleAdmin)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Service, ServiceAdminForm)
admin.site.register(ServiceSlot, ServiceSlotAdmin)

admin.site.register(Qualification, QualificationAdmin)
admin.site.register(Worker, WorkerAdmin)

admin.site.register(WorkerGroup, WorkerGroupAdmin)

admin.site.register(Exception, ExceptionAdmin)

admin.site.register(Assignment)
admin.site.register(WeekSchedule)
