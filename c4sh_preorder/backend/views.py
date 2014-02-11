# -*- coding: utf-8 -*-
import datetime, os, socket, re, datetime, random, hashlib, csv
from decimal import Decimal, getcontext, ROUND_HALF_UP
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth import login, logout
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q, F
from django.utils import simplejson
from django.utils.encoding import smart_str, smart_unicode
from django.utils.translation import ugettext as _
from django.core.mail import send_mail
from preorder.models import *
from preorder.forms import *
from preorder.decorators import preorder_check
from backend import csv_parser
from settings import *

###### API VIEWS #######
@login_required
@user_passes_test(lambda u: u.is_superuser)
def api_get_preorder_view(request):
	preorder_id = int(request.POST.get('id'))

	try:
		preorder = CustomPreorder.objects.get(pk=preorder_id)
		return HttpResponse(simplejson.dumps({'success':True, 'preorder':str(preorder)}))
	except CustomPreorder.DoesNotExist:
		return HttpResponse(simplejson.dumps({'success':False}))

###### VIEWS #######

@login_required
@user_passes_test((lambda user: user.has_perm('preorder.view_stats') \
			   or user.has_perm('preorder.change_paid_status')))
def default_view(request):
	nav = 'admin'
	subnav = 'default'
	return render_to_response('admin/default.html', locals(), context_instance=RequestContext(request))


@login_required
@permission_required('preorder.view_stats')
def statistics_view(request, section):
	nav = 'admin'
	subnav = 'statistics'

	if section == 'charts':
		subnav_statistics = 'charts'

		# stats querysets
		tickets = CustomPreorderTicket.objects.all()

		return render_to_response('admin/statistics_charts.html', locals(), context_instance=RequestContext(request))
	else:
		subnav_statistics = 'overview'


		# stats querysets
		tickets = CustomPreorderTicket.objects.all()

		return render_to_response('admin/statistics.html', locals(), context_instance=RequestContext(request))


@login_required
@permission_required('preorder.change_paid_status')
def import_csv_view(request):
	nav = 'admin'
	subnav = 'import_csv'

	if request.POST:
		if request.POST.get('review'):
			selected = request.POST.getlist('preorder')
			review_preorders = CustomPreorder.objects.filter(Q(pk__in=selected, paid=False))
		elif request.POST.get('mark'):
			mark_as_paid = request.POST.getlist('markAsPaid')
			emails_sent = 0
			preorders = CustomPreorder.objects.filter(Q(pk__in=mark_as_paid, paid=False))

			for preorder in preorders:
				preorder.paid = True
				preorder.paid_time = datetime.datetime.now()
				preorder.paid_via = "Bank"
				preorder.save()

				if preorder.get_user().email:
					# send notification email if email is set
					send_mail("[%s] Update notification" % settings.EVENT_NAME_UNIX, settings.EVENT_PAYMENT_ACK_MAIL_TEXT, "%s <%s>" % (settings.EVENT_NAME_UNIX, settings.EVENT_CONTACT_MAILTO), (preorder.get_user().email,))
					emails_sent = emails_sent+1

			marked_as_paid = len(preorders)
		else:
			form = CSVForm(request.POST, request.FILES)
			if form.is_valid():

				rows = csv_parser.parse(request.FILES['csv_file'], EVENT_CSV_PARSER, EVENT_CSV_DELIMITER)

				matches_success = []
				matches_failure = []

				for row in rows:
					if row[0] == csv_parser.Status.Success:
						# Reference hash detected, let's check it
						preorder = CustomPreorder.objects.filter(Q(unique_secret__icontains=row[4]))
						if len(preorder) == 1:
							value_ok = False
							if preorder[0].paid == True:
								# Preorder has been paid before
								value_ok = True
								status = "already_paid"
								status_message = _("This preorder has already been marked as paid via %(via)s on %(time)s.") % {'via':preorder[0].paid_via, 'time':preorder[0].paid_time}
							else:
								# Preorder wasn't paid before
								status = "ok"
								status_message = ""

								invoice_value = 0
								for iv in simplejson.loads(preorder[0].cached_sum):
									invoice_value+=iv['total']

								getcontext().prec = 20

								if Decimal(invoice_value).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) == row[5]:
									# Check if value is correct
									value_ok = True

							matches_success.append({'value_ok': value_ok, 'status': status, 'status_message': status_message, 'preorder': preorder[0], 'csv_data': row, 'invoice_value': simplejson.loads(preorder[0].cached_sum)})
						else:
							matches_failure.append(row)
					# we found no reference hash, add the current row to the failures for manual matching:
					else:
						matches_failure.append(row)

					alternative_preorders = CustomPreorder.objects.filter(Q(paid=False)).order_by('unique_secret')

				csv_data = True

	return render_to_response('admin/import_csv.html', locals(), context_instance=RequestContext(request))
