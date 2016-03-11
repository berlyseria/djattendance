from django.db import models
from django.contrib.auth.models import Group
<<<<<<< HEAD

<<<<<<< HEAD
""" SERVICES models.py
=======
from ss.models import Qualification
>>>>>>> tweaks to services models
=======
from django.utils import timezone
from .constants import WORKER_ROLE_TYPES, GENDER
from ss.models import WorkerGroup
# from ss.models import Qualification
>>>>>>> Before Ray started working officially on ss 4th term snapshot

The SERVICES model defines services in the training.

Data Models:
    - Category: This is a broad category that contains specific services. For
    example,Cleanup is a category that contains services such as Tuesday
    Breakfast Cleanup or Saturday Lunch Cleanup. Guard contains Guards A, B, C,
    and D.
    - Service: This refers to a specific service that repeats on a weekly basis.
    I.e. Tuesday Breakfast Prep is a service. It repeats every week. A specific
    instance of that service is defined in the service scheduler module as a
    service Instance.
    - Period: This is a period in which services are active and generally
    changes with the schedule of the training. Most of the time, the regular
    FTTA schedule will be in effect, but there are exceptions such as Service
    Week and the semiannual training.

"""


#Define Service Category such as Cleaning, Guard, etc.
class Category(Group):
    """
    Defines a service category such as Clean-up, Guard, Mopping, Chairs, etc.
    """

    def __unicode__(self):
        return self.name


#define Service such as Breakfast Cleaning, Dinner Prep, Guard A, etc
class Service(Group):
    """" FTTA service class to define service such as
    Tues. Breakfast Cleanup, Dinner Prep, Guard A, Wednesday Chairs, etc.
    remove two unecessary methods and minor chagens in comments
    This also includes designated services such as Accounting or Lights.
    """

    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    isActive = models.BooleanField(default=True)

    #Every service has different workload to describe its 
	#service hours and service intensity
    workload = models.IntegerField()
	
	#whether this service needs certain qualified trainees
    needQualification = models.BooleanField(blank=True)

	#Service qualification such as Sack lunch star,Kitchen Star,
	#Shuttle Driver, Piano, Usher, etc
    #Note: This is different from permanent designation. For example, 
	#two brothers are be designated as AV brothers,
    #but others brothers have the qualification to serve AV.
	qualifiedTrainees = models.ManyToManyField('accounts.Trainee')

        #whether this service needs certain qualified trainees
    need_qualification = models.BooleanField(blank=True)

    #Service qualification such as Sack lunch star,Kitchen Star,
    #Shuttle Driver, Piano, Usher, etc
    #Note: This is different from permanent designation. For example,
    #two brothers are be designated as AV brothers,
    #but others brothers have the qualification to serve AV.
    qualifiedTrainees = models.ManyToManyField('accounts.Trainee', blank=True)

    def __unicode__(self):
        return self.name

from random import randint


"""

Worker Specs

 - gender
 - qualifications
 - WORKER_ROLE_TYPES
 - term_types
 - worker_group
 - count
 - workload

worker_group join


class Assignment(models.Model):

    ROLES = WORKER_ROLE_TYPES

    # schedule = models.ForeignKey('Schedule')
    instance = models.ForeignKey(Instance)
    worker = models.ForeignKey(Worker)
    role = models.CharField(max_length=3, choices=ROLES, default='wor')


<<<<<<< HEAD
#Define Service Period such as Pre-Training, FTTA regular week, etc
class Period(models.Model):
    """Define Service Period such as Pre-Training, FTTA regular week, etc"""
=======


"""

# Should be able to define number and type of workers needed. 
# Also allow volunteers, extras to be added
class Service(models.Model):
    """
	Defines a weekly service, whether rotational (e.g. Tuesday Breakfast Clean-up)
    or designated (e.g. Attendance Project, Vehicle Maintenance, or Lights)
    """
>>>>>>> Before Ray started working officially on ss 4th term snapshot

    # according to datetime.date.today()
    WEEKDAYS = (
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    )

    category = models.ForeignKey(Category, related_name="services")
    period = models.ManyToManyField(Period, related_name="services")

    active = models.BooleanField(default=True)
    designated = models.BooleanField(default=False)
    gender = models.CharField(max_length=1, choices=GENDER, default='E')

    # Total number of workers required for this service
    workers_required = models.PositiveSmallIntegerField(default=1)

    '''  
    - Specifies types of worker groups and how many to choose from and 
      what role to give them as well as gender roles
    - Also doubles to hold designated service workers.
    '''
    worker_groups = models.ManyToManyField(WorkerGroup, 
                            through='ServiceWorkerGroup')

    weekday = models.CharField(max_length=1, choices=WEEKDAYS, default=str(randint(0,6)))
    start = models.TimeField(default=timezone.now())
    end = models.TimeField(default=timezone.now())

    def __unicode__(self):
        return self.name

''' 
TODO: Need a powerful editor for service worker groups for service schedulers 
to categorize trainees as workers based on qualifications/criteria
'''
class ServiceWorkerGroup(models.Model):
    service = models.ForeignKey(Service)
    worker_group = models.ForeignKey(WorkerGroup)
    workers_required = models.PositiveSmallIntegerField(default=1)
    # on a scale of 1-12, with 12 being the most intense
    workload = models.PositiveSmallIntegerField(default=3)
    role = models.CharField(max_length=3, choices=WORKER_ROLE_TYPES, default='wor')
    # Optional gender requirement + qualification requirement
    gender = models.CharField(max_length=1, choices=GENDER, default='E')

