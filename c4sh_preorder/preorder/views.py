# encoding: utf-8
import datetime, os, socket, re, datetime, random, hashlib, StringIO
from PIL import Image
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
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
from preorder.decorators import preorder_check, payload_check
from preorder.bezahlcode_helper import make_bezahlcode_uri
from settings import *
###### TOOLS #######

def get_cart(session_cart):
	if session_cart:
		cart = []
		for q in session_cart:
			try:
				if int(session_cart[q]['amount']) == 0:
					continue
				cart_quota = PreorderQuota.objects.get(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False), Q(pk=q))
				cart.append({'quota': cart_quota, 'amount': int(session_cart[q]['amount'])})
			except:
				continue
	else:
		return False
	return cart

###### VIEWS #######

@preorder_check
@payload_check
def default_view(request):
	if request.user.is_authenticated():
		nav = 'buy'
		quota_raw = PreorderQuota.objects.filter(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False),
			# check if we only sell this ticket in a certain time span
			(
				# nope, just sell it
				Q(ticket__limit_timespan=False)
				| # or..
				(
					Q(ticket__valid_from__lte=datetime.datetime.now(),
					ticket__valid_until__gte=datetime.datetime.now())
				)
			)).order_by('ticket__sortorder')
		quota = []
		tshirt_quota = []

		for q in quota_raw:
			if len([item for item in quota if item['ticket'] == q.ticket]) == 0:

				try:
					tshirt = Tshirt.objects.get(pk=q.ticket.pk)
					tshirt_quota.append({'quota': q, 'tshirt': tshirt})
					continue
				except Tshirt.DoesNotExist:
					ticket = q.ticket

				quota.append({'quota': q, 'ticket': ticket})

		cart = get_cart(request.session.get('cart', False))
		return render_to_response('buy.html', locals(), context_instance=RequestContext(request))

	signupform = SignupForm()
	return render_to_response('default.html', locals(), context_instance=RequestContext(request))

@login_required
@preorder_check
@payload_check
def order_view(request):
	if not request.POST:
		raise Http404
	else:
		cart = get_cart(request.session.get('cart', False))

		if not cart:
			messages.error(request, _('Cart is empty. Maybe someone was faster with his preorder and now the quota which your ticket belonged to is exceeded. Please try again.'))
			return HttpResponseRedirect(reverse("default"))

		# create Preorder
		preorder = CustomPreorder(
			name=request.user.username,
			username=request.user.username,
			user_id=request.user.pk,
			additional_info='',
			unique_secret=hashlib.sha1(str(random.random())).hexdigest(),
			time=datetime.datetime.now(),
			paid=False,
			cached_sum=0
		)
		preorder.save()

		form = BillingAddressForm(request.POST)

		if not request.POST.get('without_billingaddress') == 'yes':
			if form.is_valid():
				billing_address = PreorderBillingAddress()
				billing_address.company = form.cleaned_data['company']
				billing_address.firstname = form.cleaned_data['firstname']
				billing_address.lastname = form.cleaned_data['lastname']
				billing_address.address1 = form.cleaned_data['address1']
				billing_address.address2 = form.cleaned_data['address2']
				billing_address.city = form.cleaned_data['city']
				billing_address.zip = form.cleaned_data['zip']
				billing_address.country = form.cleaned_data['country']
				billing_address.preorder = preorder
				billing_address.save()

		for c in cart:
			amount = c['amount']
			quota = c['quota']

			try:
				quota_ = PreorderQuota.objects.get(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False), Q(pk=quota.pk))
				del quota_
			except PreorderQuota.DoesNotExist:
				messages.error(request, _("Quota for ticket %s not found or exceeded.")%quota.ticket)
				preorder.delete()
				return HttpResponseRedirect(reverse("default"))
			except:
				raise

			user_limit_exceeded = False
			if quota.ticket.limit_amount_user > 0 and int(amount) > quota.ticket.limit_amount_user:
				user_limit_exceeded = True
			if int(amount) > int(quota.get_available()) or user_limit_exceeded:
				messages.error(request, _("Your selected amount %(amount)d of %(ticket)s is no longer available.") % {'amount':int(amount), 'ticket':str(quota.ticket)})
				preorder.delete()
				return HttpResponseRedirect(reverse("default"))

			for i in range(1, amount+1):
				position = PreorderPosition(preorder=preorder, ticket=quota.ticket)

				from uuid import uuid4
				position.uuid = str(uuid4())

				position.save()

				quota.sold+=1
				quota.positions.add(position)

			quota.save()


		preorder.cached_sum = simplejson.dumps(preorder.get_sale_amount())
		preorder.save()

		request.session['cart'] = {}
		del request.session['billing_address']

		# sending out success notification via email -- if email is set
		if request.user.email:
			from c4shmail import c4shmail
			payment_until = datetime.datetime.now() + datetime.timedelta(days=int(settings.EVENT_PAYMENT_REQUIRED_TIME))
			c4shmail(request.user.email, _("Checkout successfully completed"), "checkout_success", Context({ 'user': request.user, 'preorder': preorder , 'payment_until': payment_until, 'payment_details': settings.EVENT_PAYMENT_DETAILS, 'payment_prefix': settings.EVENT_PAYMENT_PREFIX}));

		messages.success(request, _("Thanks for your preorder!"))
		return HttpResponseRedirect(reverse("my-tickets"))

@login_required
@preorder_check
@payload_check
def checkout_view(request):
	cart = get_cart(request.session.get('cart', False))
	if cart:
		totals_raw = {}
		single_ticket_over_limit = False

		for q in cart:
			amount = float(q['quota'].ticket.price)*int(q['amount'])
			taxes = float(amount) - (float(amount) / (float(q['quota'].ticket.tax_rate)/float(100)+float(1)))

			if amount >= EVENT_BILLING_ADDRESS_LIMIT:
				single_ticket_over_limit = True

			try:
				totals_raw[q['quota'].ticket.currency]['amount']+=amount
			except KeyError:
				totals_raw[q['quota'].ticket.currency] = {}
				totals_raw[q['quota'].ticket.currency]['amount']=amount

			try:
				[item for item in totals_raw[q['quota'].ticket.currency]['taxes'] if item['rate'] == q['quota'].ticket.tax_rate][0]['amount']+=taxes
			except KeyError:
				totals_raw[q['quota'].ticket.currency]['taxes'] = []
				totals_raw[q['quota'].ticket.currency]['taxes'].append({'rate':q['quota'].ticket.tax_rate, 'amount': taxes})
			except IndexError:
				totals_raw[q['quota'].ticket.currency]['taxes'].append({'rate':q['quota'].ticket.tax_rate, 'amount': taxes})

		totals = []
		for t in totals_raw:
			totals.append({'currency': t, 'total': totals_raw[t]['amount'], 'taxes': totals_raw[t]['taxes']})

		if single_ticket_over_limit:
			if request.POST:
				p = request.POST
			else:
				p = None
			form = BillingAddressForm(p)
			limit = "%.2f" % EVENT_BILLING_ADDRESS_LIMIT
			request.session['billing_address'] = True
		else:
			request.session['billing_address'] = False

	nav = 'buy'
	return render_to_response('checkout.html', locals(), context_instance=RequestContext(request))

@login_required
@preorder_check
def cart_view(request, action):
	quota_id = request.POST.get('quota')
	amount = request.POST.get('amount')

	if action == "add":
		try:
			if not quota_id or not amount or int(amount) < 0:
				messages.error(request, _("Got unexpected post data - please try again."))
				return HttpResponseRedirect(reverse("default"))
		except ValueError:
			messages.error(request, _("You are expected to enter digits.. Nothing else."))
			return HttpResponseRedirect(reverse("default"))

		try:
			quota = PreorderQuota.objects.get(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False), Q(pk=quota_id),
				# check if we only sell this ticket in a certain time span
				(
					# nope, just sell it
					Q(ticket__limit_timespan=False)
					| # or..
					(
						Q(ticket__valid_from__lte=datetime.datetime.now(),
						ticket__valid_until__gte=datetime.datetime.now())
					)
				))
		except PreorderQuota.DoesNotExist:
			messages.error(request, _("Quota not found or exceeded."))
			return HttpResponseRedirect(reverse("default"))
		except:
			raise

		session_cart = request.session.get('cart', {})
		try:
			old_amount = int(session_cart[quota.pk]['amount'])
			new_amount = old_amount + int(amount)
		except KeyError:
			new_amount = amount

		user_limit_exceeded = False
		if quota.ticket.limit_amount_user > 0 and int(new_amount) > quota.ticket.limit_amount_user:
			user_limit_exceeded = True
		if int(new_amount) > int(quota.get_available()) or user_limit_exceeded:
			messages.error(request, _("Your selected amount %(amount)d of %(ticket)s is not available.") % {'amount':int(new_amount), 'ticket':quota.ticket})
			return HttpResponseRedirect(reverse("default"))
		else:
			session_cart[int(quota.pk)] = {'amount': new_amount}
			request.session['cart'] = session_cart

		return HttpResponseRedirect(reverse("default"))

	elif action == "amend":
		try:
			if not quota_id or not amount or int(amount) < 0:
				messages.error(request, _("Got unexpected post data - please try again."))
				return HttpResponseRedirect(reverse("default"))
		except ValueError:
			messages.error(request, _("You are expected to enter digits.. Nothing else."))
			return HttpResponseRedirect(reverse("default"))

		try:
			quota = PreorderQuota.objects.get(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False), Q(pk=quota_id),
			# check if we only sell this ticket in a certain time span
			(
				# nope, just sell it
				Q(ticket__limit_timespan=False)
				| # or..
				(
					Q(ticket__valid_from__lte=datetime.datetime.now(),
					ticket__valid_until__gte=datetime.datetime.now())
				)
			))
		except PreorderQuota.DoesNotExist:
			messages.error(request, _("Quota not found or exceeded."))
			return HttpResponseRedirect(reverse("default"))
		except:
			raise

		session_cart = request.session.get('cart', False)
		if not session_cart:
			return HttpResponseRedirect(reverse("default"))

		user_limit_exceeded = False
		if quota.ticket.limit_amount_user > 0 and int(amount) > quota.ticket.limit_amount_user:
			user_limit_exceeded = True
		if int(amount) > int(quota.get_available()) or user_limit_exceeded:
			messages.error(request, _("Your selected amount %(amount)d of %(ticket)s is not available." % {'amount':int(amount), 'ticket':quota.ticket}))
			return HttpResponseRedirect(reverse("default"))
		else:
			session_cart[int(quota_id)] = {'amount': amount}
			request.session['cart'] = session_cart

		return HttpResponseRedirect(reverse("default"))

	elif action == "delete":
		session_cart = request.session.get('cart', False)
		if not session_cart:
			return HttpResponseRedirect(reverse("default"))

		session_cart[int(quota_id)] = {'amount': 0}
		request.session['cart'] = session_cart

		return HttpResponseRedirect(reverse("default"))

	raise Http404

@login_required
@payload_check
def redeem_token_view(request):
	if request.method == 'POST':
		if request.POST.get("token"):
			form = GoldenTokenForm(request.POST)
			if form.is_valid():
				token = GoldenToken.objects.get(token=form.cleaned_data['token'])
				token.redeemed = True
				token.redeem_timestamp = datetime.datetime.now()
				token.redeemer = request.user
				ticket = token.ticket

				if ticket.deleted == True:
					messages.error(request, _('The ticket %s does no longer exist. Your token has not been redeemed. Please contact support.' % ticket))

				# create Preorder
				preorder = CustomPreorder(
					name=request.user.username,
					username=request.user.username,
					user_id=request.user.pk,
					additional_info='Redeemed token: %s' % token,
					unique_secret=hashlib.sha1(str(random.random())).hexdigest(),
					time=datetime.datetime.now(),
					cached_sum=0
				)

				if ticket.price == 0:
					# This is a free ticket, mark this as paid.
					preorder.paid = True
					preorder.paid_time = datetime.datetime.now()
					preorder.paid_via = "goldentoken" # do not change this!
				else:
					preorder.paid = False

				preorder.save()
				PreorderPosition(preorder=preorder, ticket=ticket).save()

				preorder.cached_sum = simplejson.dumps(preorder.get_sale_amount())
				preorder.save()

				token.save()

				messages.success(request, _("Your token has been successfully redeemed."))

			for e in form['token'].errors:
				messages.error(request, e)

	return HttpResponseRedirect(reverse("default"))

@login_required
def tickets_view(request):
	nav = 'my'

	try:
		preorders = CustomPreorder.objects.filter(user_id=request.user.pk)
	except CustomPreorder.DoesNotExist:
		preorders = []

	if settings.EVENT_BEZAHLCODE_ENABLE and len(preorders) > 0:
		bezahlcode = make_bezahlcode_uri(preorders[0].get_reference_hash(), \
			preorders[0].get_sale_amount()[0]['total'])

	return render_to_response('tickets.html', locals(), context_instance=RequestContext(request))

@login_required
def bezahlcode_view(request):
	if not settings.EVENT_BEZAHLCODE_ENABLE:
		return HttpResponseNotFound()

	preorders = CustomPreorder.objects.filter(user_id=request.user.pk)
	if len(preorders) < 1:
		return HttpResponseServerError()

	import pyqrcode
	uri = make_bezahlcode_uri(preorders[0].get_reference_hash(), \
			preorders[0].get_sale_amount()[0]['total'])
	buf = StringIO.StringIO()
	qr = pyqrcode.MakeQRImage(uri)
	img = qr.resize((200,200), Image.ANTIALIAS)
	img.save(buf, "PNG")
	return HttpResponse(buf.getvalue(), mimetype="image/png")

@login_required
def no_view(request):
	return render_to_response('no.html', locals(), context_instance=RequestContext(request))

def signup_view(request):
	signup_page = True
	if request.method == 'POST':
		signupform = SignupForm(request.POST)
		if signupform.is_valid():
			signup_success = True
			user = User(username=signupform.cleaned_data['username'])
			if (request.POST.get('email')):
				user.email = signupform.cleaned_data['email']

			user.set_password(signupform.cleaned_data['password'])
			try:
				user.save()
			except:
				signup_success = False
				messages.error(request, _("Something went wrong, please try again."))
				return render_to_response('signup.html', locals(), context_instance=RequestContext(request))

	return render_to_response('signup.html', locals(), context_instance=RequestContext(request))

@login_required
def account_view(request):
	if request.method == 'POST':
		if request.GET.get('form') == 'email':
			form = EmailForm(request.POST)
			if form.is_valid():
				success = _("Your email address has been changed to <tt>%s</tt>!") % form.cleaned_data['email']
				request.user.email = form.cleaned_data['email']
				request.user.save()
		elif request.GET.get('form') == 'password':
			form = PasswordForm(request.user, request.POST)
			if form.is_valid():
				request.user.set_password(form.cleaned_data['new_password1'])
				request.user.save()
				success = _("Your password has been changed!")

	return render_to_response('account.html', locals(), context_instance=RequestContext(request))

@login_required
def print_tickets_view(request, preorder_id, secret):
	if EVENT_DOWNLOAD_DATE and datetime.datetime.now() < datetime.datetime.strptime(EVENT_DOWNLOAD_DATE,'%Y-%m-%d %H:%M:%S'):
		messages.error(request, _("Tickets cannot be downloaded yet, please try again shortly before the event."))
		return redirect("my-tickets")

	preorder = get_object_or_404(CustomPreorder, Q(pk=preorder_id), Q(user_id=request.user.pk), Q(unique_secret=secret))

	# what to do if this preorder is not yet marked as paid?
	if not preorder.paid:
		messages.error(request, _("You cannot download your ticket until you paid for it."))
		return redirect("my-tickets")

	# check if this ticket is eligible for an invoice address and has not yet one saved
	single_ticket_over_limit = False
	billing_address = False
	if not preorder.get_billing_address():
		for tposition in preorder.get_tickets():
			amount = float(tposition['t'].price) * int(tposition['amount'])

			if amount >= EVENT_BILLING_ADDRESS_LIMIT:
				single_ticket_over_limit = True
				break

		if single_ticket_over_limit:
			if request.POST:
				p = request.POST
			else:
				p = None
			form = BillingAddressForm(p)

			if not request.POST.get('without_billingaddress') == 'yes':
				if form.is_valid():
					billing_address = PreorderBillingAddress()
					billing_address.company = form.cleaned_data['company']
					billing_address.firstname = form.cleaned_data['firstname']
					billing_address.lastname = form.cleaned_data['lastname']
					billing_address.address1 = form.cleaned_data['address1']
					billing_address.address2 = form.cleaned_data['address2']
					billing_address.city = form.cleaned_data['city']
					billing_address.zip = form.cleaned_data['zip']
					billing_address.country = form.cleaned_data['country']
					billing_address.preorder = preorder
					billing_address.save()
				else:
					limit = EVENT_BILLING_ADDRESS_LIMIT
					return render_to_response('billingaddress.html', locals(), context_instance=RequestContext(request))

	from pyqrcode import MakeQRImage
	from fpdf import FPDF
	import time
	from django.template.defaultfilters import floatformat
	from os import remove

	pdf=FPDF('P', 'pt', 'A4')

	#initialisation
	pdf.add_font(family='dejavu', fname="%sdejavu/DejaVuSans.ttf" % settings.STATIC_ROOT, uni=True)
	pdf.add_font(family='dejavu', style="B", fname="%sdejavu/DejaVuSans-Bold.ttf" % settings.STATIC_ROOT, uni=True)
	pdf.add_font(family='dejavu', style="I", fname="%sdejavu/DejaVuSans-ExtraLight.ttf" % settings.STATIC_ROOT, uni=True)
	font = 'dejavu'

	#############################################

	delete_files = []

	for position in preorder.get_positions():
		#Print a ticket page for each preorder position

		#Fix for old tickets, probably no longer needed
		if not position.uuid:
			from uuid import uuid4
			position.uuid = str(uuid4())
			position.save()

		#create the QR code for the current ticket position
		qrcode = MakeQRImage(position.uuid)
		qrcode.save('%stmp/%s.jpg' % (settings.STATIC_ROOT, position.uuid), format="JPEG")

		#add new page
		pdf.add_page()
		pdf.set_right_margin(0)

		ticket = position.ticket

		#PDF "header"
		pdf.image('%s%s' % (settings.STATIC_ROOT, settings.EVENT_LOGO), 15, 15, 200, 96)
		#pdf.set_font(font,'B',27)
		#pdf.text(20,50,"%s" % 'SIGINT 2013')
		pdf.set_font(font,'I',6)
		pdf.text(110,100,"%s" % 'July 5th - July 7th')
		pdf.text(110,107,"%s" % 'Mediapark, Cologne, Germany')
		pdf.text(110,114,"%s" % 'https://sigint.ccc.de/')

		pdf.set_font(font,'I',40)

		# if price > 150, this is an invoice
		if ticket.price < 150 and ticket.price > 0:
			pass
			#pdf.text(220,100,"RECEIPT")
		elif ticket.price >= 150:
			pdf.text(220,90,"RECEIPT")
		pdf.set_font(font,'B',40)
		pdf.text(220,50,"ONLINE TICKET")

		# print billing address - if eligible
		if ticket.price >= EVENT_BILLING_ADDRESS_LIMIT:
			if preorder.get_billing_address() or billing_address:

				from django.utils.encoding import smart_str

				pdf.set_font('Arial','B',13)
				pdf.text(20,150,"Billing address")
				pdf.set_font('Arial','',10)

				if not billing_address:
					billing_address = preorder.get_billing_address()

				ytmp = 0

				if billing_address.company:
					pdf.text(20,170,"%s" % billing_address.company)
					ytmp+=12
				pdf.text(20,170+ytmp,"%s %s" % (billing_address.firstname, billing_address.lastname))
				pdf.text(20,182+ytmp,"%s" % billing_address.address1)
				if billing_address.address2:
					pdf.text(20,194+ytmp,"%s" % billing_address.address2)
					ytmp+=12
				pdf.text(20,194+ytmp,"%s %s" % (billing_address.zip, billing_address.city))
				pdf.text(20,206+ytmp,"%s" % billing_address.country)


		# print ticket table
		pdf.set_font(font,'I',15)
		pdf.text(20,260,"Type")
		if ticket.price > 0:
			pdf.text(350,260,"Price")

		i = 0

		pdf.set_font(font,'B',20)
		pdf.set_y(270+i)
		pdf.set_x(20)
		pdf.set_right_margin(250)
		pdf.set_left_margin(17)
		pdf.write(17, "\n%s"%ticket.name)
		pdf.set_left_margin(20)
		pdf.set_font(font,'B',20)

		pdf.set_left_margin(20)

		if ticket.price > 0:
			pdf.text(350, 302, "%s %s" % (str(floatformat(ticket.price, 2)), "€" if ticket.currency == "EUR" else ticket.currency))

			pdf.set_font(font,'',11)
			price_vat = str(floatformat(float(ticket.price)-float(ticket.price)/(float(ticket.tax_rate)/100+1), 2))
			price_net = str(floatformat(float(ticket.price)/(float(ticket.tax_rate)/100+1), 2))
			#pdf.text(350, 320, "incl. %s%% VAT: %s %s" % (ticket.tax_rate, price_vat, ticket.currency))
			#if ticket.price >= 150:
			pdf.set_font(font,'',7)
			pdf.text(350, 314, "%(price_net)s %(currency)s net + %(tax_rate)s%% VAT (%(price_vat)s %(currency)s) = %(price)s %(currency)s total" % ({
				'tax_rate': ticket.tax_rate,
				'price': ticket.price,
				'price_net': price_net,
				'price_vat': price_vat,
				'currency': "€" if ticket.currency == "EUR" else ticket.currency,
				}))

		## special tickets
		special_tickets = {
			'Speaker Ticket': 'SPEAKER',
			'Booth Operator': 'BOOTH',
			'Member of the Press': 'PRESS'
		}
		if ticket.name in special_tickets.keys():
			pdf.set_font(font,'B',72)
			pdf.text(pdf.w/2-(pdf.get_string_width(special_tickets[ticket.name])/2), 490, '%s' % special_tickets[ticket.name])

		## special tickets

		i = i + 50

		# print qr code
		pdf.image('%stmp/%s.jpg' % (settings.STATIC_ROOT, position.uuid), 300, 540, 300, 300)
		# save file url to "delete array"
		delete_files.append('%stmp/%s.jpg' % (settings.STATIC_ROOT, position.uuid))

		# print human readable ticket code
		pdf.set_font(font,'I',8)
		pdf.text(23, 790, 'Payment reference: %s-%s' % (settings.EVENT_PAYMENT_PREFIX, preorder.unique_secret[:10]))
		pdf.text(23, 800, '%s' % position.uuid)
		pdf.text(23, 810, '%s' % preorder.unique_secret)



		#PDF "Footer"

		# print invoice information
		pdf.set_font(font, '', 15)
		pdf.set_y(550)
		pdf.write(20, '%s' % settings.EVENT_INVOICE_ADDRESS)
		pdf.set_font(font, '', 10)
		pdf.set_y(640)
		if ticket.price > 0:
			pdf.write(15, '%s' % settings.EVENT_INVOICE_LEGAL)
		pdf.set_font(font, '', 10)
		pdf.set_y(680)
		pdf.write(15, 'Issued: %s' % time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
		pdf.set_font(font, '', 8)
		pdf.set_y(720)
		pdf.set_right_margin(300)

		if ticket.price > 0 and ticket.price < 150:
			pdf.write(10, "Bis zu einem Ticketpreis von 150,00 EUR gilt das Ticket gleichzeitig als Kleinbetragsrechnung im Sinne von § 33 UStDV. Umtausch und Rückgabe ausgeschlossen.")
		elif ticket.price >= 150:
			pdf.write(10, "Umtausch und Rückgabe ausgeschlossen.")
	#are Credit Card payments enabled? If yes, is this a preorder paid by CC?
	""" commented out for sigint13
	if settings.EVENT_CC_ENABLE and preorder.paid_via=="creditcard":
		total = preorder.get_sale_amount()[0]['total']
		total_with_fees = (total + settings.EVENT_CC_FEE_FIXED) * (settings.EVENT_CC_FEE_PERCENTAGE/100+1)
		cc_fees = total_with_fees - total

		# 2 decimal places for the cc_fees. Todo: fix rounding for the saferpay foo
		slen = len('%.*f' % (2, cc_fees))
		cc_fees = str(cc_fees)[:slen]

		#Maybe Todo, see saferpay/views: dont hardcode currency
		cc_currency = "EUR"
		#check against the stored cc confirmation!!

		#create new page for creditcard receipt
		pdf.add_page()
		pdf.set_right_margin(0)
		pdf.set_font(font,'I',37)
		pdf.text(20,50,"%s" % 'N.O-T/M.Y-DE/PA.R-TM/EN.T')
		pdf.set_font(font,'B',37)
		pdf.text(20,85,"%s" % '2.9-C/3')
		pdf.set_font(font,'I',20)
		pdf.text(20,150,"%s" % '29th CHAOS COMMUNICATION CONGRESS')
		pdf.text(20,185,"%s" % 'DECEMBER 27th TO 30TH 2012')
		pdf.text(20,220,"%s" % 'CONGRESS CENTER HAMBURG, GERMANY')

		# this is an invoice for the cc fees
		pdf.set_font(font,'I',40)
		pdf.text(20,325,"RECEIPT")
		pdf.set_font(font,'B',40)
		pdf.text(20,290,"CREDIT CARD FEES")

		# print modified ticket table for credit card statement
		pdf.set_font(font,'I',15)
		pdf.text(20,420,"Type")
		pdf.text(350,420,"Price")
		pdf.set_font(font,'',25)
		pdf.set_font(font,'B',20)
		pdf.set_y(418)
		pdf.set_x(20)
		pdf.set_right_margin(250)
		pdf.set_left_margin(17)
		pdf.write(17, "\n%s"% "Credit Card Fee")
		pdf.set_left_margin(20)
		pdf.set_font(font,'B',20)

		pdf.set_left_margin(20)
		pdf.text(350, 450, "%s %s" % (str(floatformat(cc_fees, 2)), cc_currency))

		# print invoice information
		pdf.set_font(font, '', 15)
		pdf.set_y(550)
		pdf.write(20, '%s' % settings.EVENT_INVOICE_ADDRESS)
		pdf.set_font(font, '', 10)
		pdf.set_y(640)
		#Computer says no
		#pdf.write(15, '%s' % settings.EVENT_INVOICE_LEGAL)
		pdf.set_font(font, '', 10)
		pdf.set_y(680)
		pdf.write(15, 'Issued: %s' % time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
		pdf.set_font(font, '', 8)
		pdf.set_y(720)
		pdf.set_right_margin(300)
	"""


	response = HttpResponse(mimetype="application/pdf")
	response['Content-Disposition'] = 'inline; filename=%s-%s.pdf' % (settings.EVENT_PAYMENT_PREFIX, preorder.unique_secret[:10])
	#response['Content-Length'] = in_memory.tell()
	response.write(pdf.output('', 'S'))

	# delete qrcode
	for f in delete_files:
		remove(f)

	return response

@login_required
def passbook_view(request, preorder_id, secret):

	if not EVENT_PASSBOOK_ENABLE:
		messages.error(request, _("Passbook support has not been enabled for this event."))
		return redirect("my-tickets")

	if EVENT_DOWNLOAD_DATE and datetime.datetime.now() < datetime.datetime.strptime(EVENT_DOWNLOAD_DATE,'%Y-%m-%d %H:%M:%S'):
		messages.error(request, _("Tickets cannot be downloaded yet, please try again shortly before the event."))
		return redirect("my-tickets")

	preorder = get_object_or_404(CustomPreorder, Q(pk=preorder_id), Q(user_id=request.user.pk), Q(unique_secret=secret))

	# what to do if this preorder is not yet marked as paid?
	if not preorder.paid:
		messages.error(request, _("You cannot download your ticket until you paid for it."))
		return redirect("my-tickets")

	if request.GET.get('pos'):
		try:
			position_id = int(request.GET.get('pos'))
			# fetch position with preorder, which has already been checked..
			position = PreorderPosition.objects.get(pk=position_id, preorder=preorder)
		except:
			messages.error(request, _("Invalid preorder position given - please try again later."))
			return redirect("my-tickets")

		if not position.uuid:
			from uuid import uuid4
			position.uuid = str(uuid4())
			position.save()

		uuid = position.uuid

		from passbook_helper import make_passbook_file

		try:
			passbook_file = make_passbook_file({
				'ticket': position.ticket.name,
				'uuid': uuid,
				'from': EVENT_PASSBOOK_FROM,
				'to': EVENT_PASSBOOK_TO,
				'organisation': EVENT_PASSBOOK_ORGANISATION,
				'identifier': EVENT_PASSBOOK_IDENTIFIER,
				'teamidentifier': EVENT_PASSBOOK_TEAMIDENTIFIER,
				'desc': EVENT_PASSBOOK_DESCRIPTION,
				'bgcolor': EVENT_PASSBOOK_BG_COLOR,
				'fgcolor': EVENT_PASSBOOK_FG_COLOR,
				'logotext': EVENT_PASSBOOK_LOGO_TEXT,
				'filespath': EVENT_PASSBOOK_FILES_PATH,
				'password': EVENT_PASSBOOK_PASSWORD,
				'lat': EVENT_PASSBOOK_LOCATION[0],
				'long': EVENT_PASSBOOK_LOCATION[1],
				'relevant_date': EVENT_PASSBOOK_RELEVANT_DATE
			})
		except:
			messages.error(request, _("An error occurred while generating your Passbook file - please try again later."))
			return redirect("my-tickets")

		response = HttpResponse(mimetype="application/vnd.apple.pkpass")
		response['Content-disposition'] = 'attachment; filename=Passbook-%s.pkpass' % preorder.get_reference_hash()
		response.write(passbook_file.getvalue())
		passbook_file.close()
		return response

	return render_to_response('passbook.html', locals(), context_instance=RequestContext(request))
