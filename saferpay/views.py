# -*- coding: utf-8 -*-
import datetime, os, socket, re, datetime, random, hashlib, urlparse, requests
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
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template import Context
from saferpay import settings as safersettings
from c4sh_preorder import settings
import logging

logger = logging.getLogger('payment.saferpay')

###### VIEWS #######

@login_required
def pay_view(request):
    protocol = 'https'
    try:
        order = CustomPreorder.objects.filter(user_id=request.user.pk, paid=False)[0]
    except CustomPreorder.DoesNotExist:
        messages.error(request, "You have no preorder to pay.")
        return redirect("my-tickets")
    try:
        total = order.get_sale_amount()[0]['total']
    except KeyError:
        messages.error(request, "You have no preorder to pay.")
        return redirect("my-tickets")
    total = total * (safersettings.EVENT_CC_FEE_PERCENTAGE/100+1) + safersettings.EVENT_CC_FEE_FIXED
    domain = '%s://%s/' % (protocol, settings.APP_URL)
    data = {
        'AMOUNT': int(total * 100),
        'CURRENCY': 'EUR', # TODO: don't hard code this
        'DESCRIPTION': "Order %s-%s (including CC fees)" % (settings.EVENT_PAYMENT_PREFIX, order.get_reference_hash()),
        'LANGID': 'EN',
        'ALLOWCOLLECT': 'yes' if safersettings.ALLOW_COLLECT else 'no',
        'DELIVERY': 'yes' if safersettings.DELIVERY else 'no',
        'ACCOUNTID': safersettings.ACCOUNT_ID,
        'ORDERID': order.get_reference_hash(),
        'SUCCESSLINK': domain +  reverse('saferpay-complete'),
        'BACKLINK': domain + reverse('saferpay-abort'),
        'FAILLINK': domain + reverse('saferpay-fail'),
        
    }
    for style in ('BODYCOLOR', 'HEADCOLOR', 'HEADLINECOLOR', 'MENUCOLOR', 'BODYFONTCOLOR', 'HEADFONTCOLOR', 'MENUFONTCOLOR', 'FONT'):
        style_value = getattr(safersettings, style)
        if style_value is not None:
            data[style] = style_value
    
    response = requests.get(safersettings.PROCESS_URL, params=data)
    logger.info('Saferpay: order %d\tredirected to saferpay gateway', order.pk)
    return HttpResponseRedirect(response.content)

@login_required
def fail_view(request):
	messages.error(request, _("The credit card transaction failed. Please try again later or contact your credit card institute if the problem persists."))
	return redirect("my-tickets")

@login_required
def abort_view(request):
	messages.info(request, _("The credit card payment has been aborted."))
	return redirect("my-tickets")

@login_required
def complete_view(request):
	# TODO: check if we actually know about a payment
	messages.success(request, _("Credit card payment was successful."))
	return redirect("my-tickets")

def response_view(request):
	# TODO: only allow from saferpay
	pass
