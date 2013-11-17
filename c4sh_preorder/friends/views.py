# encoding: utf-8
import datetime, os, socket, re, datetime, random, hashlib, StringIO
from PIL import Image
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template import Context
from django.db.models import Q, F
from django.core.mail import send_mail
from preorder.models import *
from preorder.forms import *
from friends.models import *
from friends.forms import *
from preorder.decorators import preorder_check, payload_check
from settings import *
from c4sh.preorder.models import PreorderTicket
import random

@login_required
@user_passes_test(lambda u: u.is_staff)
@user_passes_test(lambda u: u.has_perm('friends.review'))
def friends_review(request, secret):
	if not settings.EVENT_FRIENDS_ENABLED:
		raise Exception(_("Friends application is not enabled for this event!"))
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
			application.status = 'rejected'
			application.save()

			send_mail('[%s] Friends application rejected' % settings.EVENT_NAME_SHORT, "Hello %s,\n\nyour friends ticket application has been rejected. Sorry!\n\nThe event orga" % (application.user.username), EVENT_FRIENDS_EMAIL, [application.user.email], fail_silently=False)

			messages.success(request, _('The application has been successfully rejected.'))
			return redirect("default")
		elif request.POST.get('option') == 'approve':
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
				return redirect("default")

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

			from uuid import uuid4
			for i in range(int(request.POST.get('amount', 1))):
				position = PreorderPosition(preorder=preorder, ticket=ticket)
				position.uuid = str(uuid4())
				position.save()

			preorder.cached_sum = simplejson.dumps(preorder.get_sale_amount())
			preorder.save()

			application.status = 'approved'
			application.save()

			send_mail('[%s] Friends application approved' % settings.EVENT_NAME_SHORT, "Hello %s,\n\nyour friends ticket application has been approved.\n\nA preorder with the appropriate ticket has been automatically created for you -- please find it in the preorder system.\n\nThe event orga" % (application.user.username), EVENT_FRIENDS_EMAIL, [application.user.email], fail_silently=False)

			messages.success(request, _('The application has been successfully approved.'))
			return redirect("default")


	return render_to_response('friends/review.html', locals(), context_instance=RequestContext(request))

@login_required
@payload_check
def friends_apply(request):
	if not settings.EVENT_FRIENDS_ENABLED:
		raise Exception(_("Friends application is not enabled for this event!"))
	nav = 'buy'

	# check if user already has a preorder
	preorder_count = CustomPreorder.objects.filter(user_id=request.user.pk)
	if len(preorder_count) != 0:
		messages.error(request, _('You cannot apply for a Friends ticket because you already have a preorder.'))
		return redirect("default")

	if not request.user.email:
		messages.error(request, _('In order to apply for a Friends ticket, you need to set up an email address so we can contact you in case of further questions and inform you about the status of your application.'))
		return redirect("account")

	try:
		has_application = FriendsApplication.objects.get(user=request.user)
	except FriendsApplication.DoesNotExist:
		has_application = False

	if request.POST.get('application'):
			form = FriendsApplicationForm(request.POST)
			if form.is_valid():
				# do something
				if not has_application:
					application = FriendsApplication(user=request.user, datetime=datetime.datetime.now(), text=form.cleaned_data['application'], token=hashlib.sha1(str(random.random())).hexdigest())
					application.save()
					has_application = application

					if request.is_secure():
						protocol = 'https://'
					else:
						protocol = 'http://'

					send_mail('[%s] Friends application received' % settings.EVENT_NAME_SHORT, "Dear friends ticket review team,\na new application has been received.\n\nPlease proceed using the following URL:\n\n%s%s%s" % (protocol, request.get_host(), reverse('friends-review', args=[application.token])), request.user.email, [settings.EVENT_FRIENDS_EMAIL], fail_silently=False)
					# TODO: userinfo

					messages.success(request, _('We have received your application and will inform you about status changes via email. Thanks.'))

	return render_to_response('friends/apply.html', locals(), context_instance=RequestContext(request))
