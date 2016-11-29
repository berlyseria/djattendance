from django.db import models
from django.core.urlresolvers import reverse

from accounts.models import Trainee

class Announcement(models.Model):

    class Meta:
        verbose_name = "announcement"

    ANNOUNCE_STATUS = (
        ('A', 'Approved'),
        ('P', 'Pending'),
        ('F', 'Fellowship'),
        ('D', 'Denied'),
    )

    ANNOUNCE_TYPE = (
        ('CLASS', 'In-class'),
        ('SERVE', 'On the server')
    )

    status = models.CharField(max_length=1, choices=ANNOUNCE_STATUS, default='P')
    type = models.CharField(max_length=5, choices=ANNOUNCE_TYPE, default='CLASS')

    date_requested = models.DateField(auto_now_add=True)
    trainee = models.ForeignKey(Trainee, null=True)
    TA_comments = models.TextField(null=True, blank=True)
    trainee_comments = models.TextField(null=True)
    announcement = models.TextField()
    announcement_date = models.DateField()
    announcement_end_date = models.DateField(null=True) # this is required if it's on the server
    # this can be used if it's on the server for those trainees who should see the announcement
    trainees = models.ManyToManyField(Trainee, related_name="announcement_disp", blank=True)

    def __unicode__(self):
        return '<Announcement %s ...> by trainee %s' % (self.announcement[:10], self.trainee)

    @staticmethod
    def get_create_url():
        return reverse('announcements:announcement-request')

    def get_absolute_url(self):
        return reverse('announcements:announcement-detail', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('announcements:announcement-update', kwargs={'pk': self.id})

    def get_ta_comments_url(self):
        return reverse('announcements:ta-comment', kwargs={'pk': self.id})
