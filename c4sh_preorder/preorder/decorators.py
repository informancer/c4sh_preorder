from django.http import Http404, HttpResponse, HttpResponseRedirect
from functools import wraps
from django.core.urlresolvers import reverse
from preorder.models import CustomPreorder
from django.conf import settings

def preorder_check(func):
	def _check(request, *args, **kwargs):
		try:
			if request.user.is_authenticated():
				if CustomPreorder.objects.filter(user_id=request.user.pk).count() >= 1:
					#return HttpResponseRedirect(reverse("no-more-preorder"))
					return HttpResponseRedirect(reverse("my-tickets"))
			return func(request, *args, **kwargs)
		except:
			raise
	return wraps(func)(_check)

def payload_check(func):
	def _check(request, *args, **kwargs):
		try:
			if request.user.is_authenticated():
				if CustomPreorder.objects.all().count() >= settings.EVENT_VENUE_PAYLOAD:
					return HttpResponseRedirect(reverse("no-more-preorder"))
			return func(request, *args, **kwargs)
		except:
			raise
	return wraps(func)(_check)