import datetime
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings
from model_utils.fields import StatusField
from model_utils import Choices
from c4sh.preorder.models import PreorderTicket, PreorderPosition, Preorder

class FriendsApplication(models.Model):
	STATUS = Choices('waiting', 'approved', 'rejected')

	user = models.ForeignKey(User, verbose_name="Applicant")
	datetime = models.DateTimeField()
	text = models.TextField()
	token = models.CharField(max_length=50, null=False, blank=False, verbose_name="Secret token of this application", unique=True)
	status = StatusField()

	def __unicode__(self):
		return "Applicant: %s (%s), Status: %s" % (self.user, self.datetime, self.status)

	class Meta:
		permissions = (
			('review', 'Can review Friends Applications'),
		)
