# -*- coding: utf-8 -*-
import datetime, os, socket, re, datetime, random, hashlib
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from preorder.models import *
from settings import * 
from preorder.forms import *
from django.db.models import Q, F
from preorder.decorators import preorder_check, payload_check
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template import Context
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
		quota_raw = PreorderQuota.objects.filter(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False))
		quota = []

		for q in quota_raw:
			if len([item for item in quota if item['ticket'] == q.ticket]) == 0:
				quota.append({'quota': q, 'ticket': q.ticket})

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
		for q in cart:
			amount = float(q['quota'].ticket.price)*int(q['amount'])
			taxes = float(amount) - (float(amount) * float((100-q['quota'].ticket.tax_rate)/float(100)))

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
			quota = PreorderQuota.objects.get(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False), Q(pk=quota_id))
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
			quota = PreorderQuota.objects.get(Q(sold__lt=F('quota')), Q(ticket__active=True), Q(ticket__deleted=False), Q(pk=quota_id))
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
					paid=True,
					paid_time=datetime.datetime.now(),
					paid_via="goldentoken", # do not change this!
					cached_sum=0
				)

				preorder.save()
				PreorderPosition(preorder=preorder, ticket=ticket).save()
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
	
	return render_to_response('tickets.html', locals(), context_instance=RequestContext(request))

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
			user.save()
		
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

	from pyqrcode import MakeQRImage
	from fpdf import FPDF
	import time
	from django.template.defaultfilters import floatformat
	from os import remove

	pdf=FPDF('P', 'pt', 'A4')

	# invoice 
	"""pdf.add_page()

	# print logo
	pdf.image('%s%s' % (settings.STATIC_ROOT,settings.EVENT_LOGO), 280, 10, 1000*0.3, 580*0.3)   
    pdf.set_font('Arial','B',20)
	pdf.text(20,50,"%s Overview" % settings.EVENT_NAME_SHORT)
	pdf.set_font('Arial','B',10)
	pdf.text(20,70,"These are your presale's positions. This is not an invoice.")

	# print ticket table
	pdf.set_font('Arial','B',15)
	pdf.text(150,220,"Type")
	pdf.text(360,220,"Price")
	pdf.text(480,220,"Price total")

	i = 0
	for ticket in preorder.get_tickets():


		#for ticket in preorder.get_tickets():
		pdf.set_font('Arial','',25)
		pdf.text(50, 260+i, '%sx' % str(ticket['amount']))
		
		pdf.set_font('Arial','B',25)
		pdf.text(150, 260+i, '%s' % ticket['t'].name)
		pdf.set_font('Arial','',17)
		
		if preorder.paid_via == 'goldentoken':
			pdf.text(360, 250+i, 'GOLDEN TOKEN')
		else:
			pdf.text(360, 260+i, "%s %s" % (str(floatformat(ticket['t'].price, 2)), ticket['t'].currency))
			pdf.text(480, 260+i, "%s %s" % (str(floatformat(ticket['t'].price*ticket['amount'], 2)), ticket['t'].currency))
		i = i + 50

	for t in preorder.get_sale_amount():
		pdf.text(430, 250+i, "===============")
		pdf.text(430, 270+i, "%s %s" % (str(floatformat(t['total'], 2)), t['currency']))
		for tax in t['taxes']:
			pdf.set_font('Arial','',11)
			pdf.text(430, 285+i, "incl. %s%% taxes: %s %s" % (tax['rate'], str(floatformat(tax['amount'], 2)), t['currency']))

	# print human readable preorder code
	pdf.set_font('Arial','',20)
	pdf.text(10, 800, '%s' % preorder.unique_secret)

	# print invoice information
	pdf.set_font('Arial', '', 10)
	pdf.text(10, 830, '%s' % settings.EVENT_INVOICE_ADDRESS)
	"""

	#############################################

	delete_files = []

	for position in preorder.get_positions():

		if not position.uuid:
			from uuid import uuid4
			position.uuid = str(uuid4())
			position.save()

		qrcode = MakeQRImage(position.uuid)
		qrcode.save('%stmp/%s.jpg' % (settings.STATIC_ROOT, position.uuid), format="JPEG")

		pdf.add_page()
		pdf.set_right_margin(0)

		ticket = position.ticket

		# print logo
		pdf.image('%s%s' % (settings.STATIC_ROOT,settings.EVENT_LOGO), 280, 10, 1000*0.3, 580*0.3)
		pdf.set_font('Arial','B',50)
		pdf.text(20,60,"%s" % settings.EVENT_NAME_SHORT)

		pdf.set_font('Arial','B',20)
		if ticket.price <= 150 and ticket.price > 0:
			pdf.text(20,100,"Online Ticket / Invoice")
		else:
			pdf.text(20,100,"Online Ticket")

		# print ticket table
		pdf.set_font('Arial','B',15)
		pdf.text(150,220,"Type")
		pdf.text(430,220,"Price")

		i = 0

		#for ticket in preorder.get_tickets():
		pdf.set_font('Arial','',25)
		#pdf.text(50, 260+i, '%sx' % str(ticket['amount']))
		
		pdf.set_font('Arial','B',25)
		pdf.text(150, 260+i, '%s' % ticket.name)
		pdf.set_font('Arial','',17)
		
		if ticket.price == 0:
			pdf.text(430, 260+i, 'Free')
		else:
			"""for t in preorder.get_sale_amount():
				pdf.text(430, 250+i, "%s %s" % (str(floatformat(t['total'], 2)), t['currency']))
				for tax in t['taxes']:
					pdf.set_font('Arial','',11)
					pdf.text(430, 270+i, "incl. %s%% taxes: %s %s" % (tax['rate'], str(floatformat(tax['amount'], 2)), t['currency']))
			"""
			pdf.text(430, 260+i, "%s %s" % (str(floatformat(ticket.price, 2)), ticket.currency))

			pdf.set_font('Arial','',11)
			pdf.text(430, 285+i, "incl. %s%% VAT: %s %s" % (ticket.tax_rate, str(floatformat(float(ticket.price)-float(ticket.price)/(float(ticket.tax_rate)/100+1), 2)), ticket.currency))

		## special tickets
		special_tickets = {
			'Speakerticket': 'SPEAKER',
			'Standbetreiber-Ticket': 'STAND',
			'Presseticket': 'PRESSE'
		}
		if ticket.name in special_tickets.keys():
			pdf.set_font('Arial','B',72)
			pdf.text(120, 420, '%s' % special_tickets[ticket.name])

		## special tickets

		i = i + 50

		"""for t in preorder.get_sale_amount():
			pdf.text(430, 250+i, "=============")
			pdf.text(430, 270+i, "%s %s" % (str(floatformat(t['total'], 2)), t['currency']))
			for tax in t['taxes']:
				pdf.set_font('Arial','',11)
				pdf.text(430, 285+i, "incl. %s%% taxes: %s %s" % (tax['rate'], str(floatformat(tax['amount'], 2)), t['currency']))"""

		# print qr code
		pdf.image('%stmp/%s.jpg' % (settings.STATIC_ROOT, position.uuid), 300, 540, 300, 300)
		# save file url to "delete array"
		delete_files.append('%stmp/%s.jpg' % (settings.STATIC_ROOT, position.uuid))

		# print human readable ticket code
		pdf.set_font('Arial','',10)
		pdf.text(330, 545, 'Payment reference: %s-%s' % (settings.EVENT_NAME, preorder.unique_secret[:10]))
		pdf.text(330, 555, '%s' % preorder.unique_secret)
		pdf.text(330, 565, '%s' % position.uuid)

		# print invoice information
		pdf.set_font('Arial', '', 15)
		pdf.set_y(500)
		pdf.write(20, '%s' % settings.EVENT_NAME)
		pdf.set_font('Arial', '', 10)
		pdf.set_y(515)
		pdf.write(20, '%s' % settings.EVENT_TIME_AND_LOCATION)
		pdf.set_font('Arial', '', 15)
		pdf.set_y(570)
		pdf.write(20, '%s' % settings.EVENT_INVOICE_ADDRESS)
		pdf.set_font('Arial', '', 10)
		pdf.set_y(660)
		pdf.write(15, '%s' % settings.EVENT_INVOICE_LEGAL)
		pdf.set_font('Arial', '', 10)
		pdf.set_y(700)
		pdf.write(15, 'Issued: %s' % time.strftime('%Y-%m-%d %H:%M', time.gmtime()))
		pdf.set_font('Arial', '', 8)
		pdf.set_y(730)
		pdf.set_right_margin(300)
		if ticket.price > 0:
			pdf.write(10, "Bis zu einem Ticketpreis von 150,00 EUR gilt das Ticket gleichzeitig als Kleinbetragsrechnung im Sinne von Paragraph 33 UStDV. Eine Berechtigung zum Vorsteuerabzug besteht bei einem Ticketpreis von mehr als 150,00 EUR nur in Verbindung mit einer separaten Rechnung. Umtausch und Rueckgabe ausgeschlossen.")
		

		#pdf.set_font('Arial', '', 10)
		#pdf.text(10, 830, '%s' % settings.EVENT_INVOICE_ADDRESS)

	response = HttpResponse(mimetype="application/pdf")
	response['Content-Disposition'] = 'inline; filename=%s-%s.pdf' % (settings.EVENT_NAME, preorder.unique_secret[:10])
    #response['Content-Length'] = in_memory.tell()
	response.write(pdf.output('', 'S'))

	# delete qrcode
	for f in delete_files:
		remove(f)

	return response
