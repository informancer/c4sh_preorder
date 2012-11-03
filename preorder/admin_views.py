# -*- coding: utf-8 -*-
import datetime, os, socket, re, datetime, random, hashlib
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from preorder.models import *
from settings import * 
from preorder.forms import *
from django.db.models import Q, F
from preorder.decorators import preorder_check
from django.utils import simplejson
import csv
import re
from  django.utils.encoding import smart_str, smart_unicode
from django.utils.translation import ugettext as _
from django.core.mail import send_mail

###### API VIEWS #######

def api_get_preorder_view(request):
	preorder_id = int(request.POST.get('id'))

	try:
		preorder = CustomPreorder.objects.get(pk=preorder_id)
		return HttpResponse(simplejson.dumps({'success':True, 'preorder':str(preorder)}))
	except CustomPreorder.DoesNotExist:
		return HttpResponse(simplejson.dumps({'success':False}))

###### VIEWS #######

@login_required
@user_passes_test(lambda u: u.is_superuser)
def default_view(request):
	nav = 'admin'
	subnav = 'default'
	return render_to_response('admin/default.html', locals(), context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
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
@user_passes_test(lambda u: u.is_superuser)
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
				csv_file = request.FILES['csv_file']
				csv_reader = csv.reader(csv_file, delimiter=str(form.cleaned_data['delimiter']))

				matches_success = []
				matches_failure = []

				for row in csv_reader:
					if len(row) is not 8 or str(row[0]) == str("Buchungstag"):
						continue

					# row[0] is Buchungstag
					# row[1] is Wertstellung
					# row[2] is Umsatzart
					# row[3] is Buchungsdetails (!)
					# row[4] is Auftraggeber
					# row[5] is Empfaenger
					# row[6] is Betrag
					# row[7] is Saldo

					row[6] = re.sub(' \\x80', '', row[6]) # replacing malicious € symbol
					row[6] = re.sub(',', '.', row[6]) # replacing , with . for float formatting
					row[6] = float(row[6])

					reference_hash = re.compile('%s-[a-fA-F0-9]{10}' % settings.EVENT_PAYMENT_PREFIX).findall(row[3])

					# trying to figure out if some brains are unable to use the right reference code
					if not reference_hash:
						reference_hash = re.compile('[a-fA-F0-9]{10}').findall(row[3])

					# okay, giving up
					if not reference_hash:
						reference_hash = []
						reference_hash.append(row[3])
					
					if len(reference_hash) == 1:
						reference_hash_only = re.compile('[a-fA-F0-9]{10}').findall(reference_hash[0])

						if len(reference_hash_only) == 0:
							reference_hash_only.append(reference_hash[0])

						preorder = CustomPreorder.objects.filter(Q(unique_secret__icontains=reference_hash_only[0]))
						if len(preorder) == 1:
							value_ok = False							
							if preorder[0].paid == True:
								value_ok = True
								status = "already_paid"
								status_message = _("This preorder has already been marked as paid via %(via)s on %(time)s.") % {'via':preorder[0].paid_via, 'time':preorder[0].paid_time}
							else:
								status = "ok"
								status_message = ""

								invoice_value = 0
								for iv in simplejson.loads(preorder[0].cached_sum):
									invoice_value+=iv['total']

								if float(invoice_value) == row[6]:
									value_ok = True

							matches_success.append({'value_ok': value_ok, 'status': status, 'status_message': status_message, 'preorder': preorder[0], 'csv_data': row, 'invoice_value': simplejson.loads(preorder[0].cached_sum)})
						else:
							matches_failure.append(row)

					alternative_preorders = CustomPreorder.objects.filter(Q(paid=False)).order_by('unique_secret')

				csv_data = True

	return render_to_response('admin/import_csv.html', locals(), context_instance=RequestContext(request))