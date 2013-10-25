# encoding: utf-8
import datetime, os, socket, re, datetime, random, hashlib, StringIO
from PIL import Image
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template import Context
from django.db.models import Q, F
from preorder.models import *
from preorder.forms import *
from friends.models import *
from friends.forms import *
from preorder.decorators import preorder_check, payload_check
from settings import *
from c4sh.preorder.models import PreorderTicket
import random

if not settings.EVENT_FRIENDS_ENABLED:
	raise Exception("Friends application is not for this event enabled!")


def friends_review(request, secret):

	application = get_object_or_404(FriendsApplication, token=secret)

	if application.status != "waiting":
		messages.success(request, _('The application has already been processed.'))
		return HttpResponseRedirect(reverse("default"))


	tickets = PreorderTicket.objects.filter(name__istartswith=settings.EVENT_FRIENDS_TICKET_PREFIX)

	if len(tickets) == 0:
		messages.error(request, _('No friends tickets are registered. Please contact the event organisation.'))
		return HttpResponseRedirect(reverse("default"))

	if request.POST:
		if request.POST.get('option') == 'reject':
			# TODO: send email

			application.status = 'rejected'
			application.save()

			messages.success(request, _('The application has been successfully rejected.'))
			return HttpResponseRedirect(reverse("default"))
		elif request.POST.get('option') == 'approve':
			# TODO: set state

			# create preorder with given ticket
			try:
				ticket = PreorderTicket.objects.get(pk=int(request.POST.get('ticket')), name__istartswith=settings.EVENT_FRIENDS_TICKET_PREFIX)
			except PreorderTicket.DoesNotExist:
				messages.error(request, _('Invalid ticket given.'))
				return HttpResponseRedirect(request.META['HTTP_REFERER'])

			# check if user already has a preorder
			preorder_count = CustomPreorder.objects.filter(user_id=application.user.pk)
			if len(preorder_count) != 0:
				messages.error(request, _('The user already has a preorder, therefore the request has been cancelled.'))
				return HttpResponseRedirect(request.META['HTTP_REFERER'])

			# create Preorder
			preorder = CustomPreorder(
				name=application.user.username,
				username=application.user.username,
				user_id=application.user.pk,
				additional_info='Friends application',
				unique_secret=hashlib.sha1(str(random.random())).hexdigest(),
				time=datetime.datetime.now(),
				paid=False,
				cached_sum=0
			)
			preorder.save()

			position = PreorderPosition(preorder=preorder, ticket=ticket)
			from uuid import uuid4
			position.uuid = str(uuid4())
			position.save()

			preorder.cached_sum = simplejson.dumps(preorder.get_sale_amount())
			preorder.save()

			application.status = 'approved'
			application.save()

			# TODO: send email

			messages.success(request, _('The application has been successfully approved.'))
			return HttpResponseRedirect(reverse("default"))


	return render_to_response('friends/review.html', locals(), context_instance=RequestContext(request))

@login_required
@payload_check
def friends_apply(request):
	nav = 'buy'

	# check if user already has a preorder
	preorder_count = CustomPreorder.objects.filter(user_id=request.user.pk)
	if len(preorder_count) != 0:
		messages.error(request, _('You cannot apply for a Friends ticket because you already set up a preorder.'))
		return HttpResponseRedirect(reverse('default'))

	if not request.user.email:
		messages.error(request, _('In order to apply for a Friends ticket, you need to set up an email address so we can contact you in case of further questions and inform you about the status of your application.'))
		return HttpResponseRedirect(reverse("account"))

	try:
		has_application = FriendsApplication.objects.get(user=request.user)
	except FriendsApplication.DoesNotExist:
		has_application = False

	if request.POST.get("application"):
			form = FriendsApplicationForm(request.POST)
			if form.is_valid():
				# do something
				if not has_application:
					application = FriendsApplication(user=request.user, datetime=datetime.datetime.now(), text=form.cleaned_data['application'], token=hashlib.sha1(str(random.random())).hexdigest())
					application.save()
					has_application = True

					messages.success(request, _('We have received your application and will inform you about status changes via email. Thanks.'))

					# TODO: send email to $reviewer

	return render_to_response('friends/apply.html', locals(), context_instance=RequestContext(request))
