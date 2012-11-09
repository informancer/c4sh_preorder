# -*- coding: utf-8 -*-
import datetime, os, socket, re, datetime, random, hashlib, urlparse, requests
from django.core import serializers
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import Http404, HttpResponseServerError, HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from preorder.models import *
from settings import * 
from preorder.forms import *
from django.db.models import Q, F
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template import Context
from saferpay import settings as safersettings
from c4sh_preorder import settings
from xml.etree import ElementTree as ET
import logging


logger = logging.getLogger('c4sh_preorder.saferpay')

###### VIEWS #######

@login_required
def pay_view(request):
    protocol = 'https'
    try:
        order = CustomPreorder.objects.filter(user_id=request.user.pk, paid=False)
        if len(order)>0:
            order = order[0]
        else:
            messages.error(request, "You have no preorder to pay.")
            return redirect("my-tickets")

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
        'CURRENCY': 'EUR', # Maybe TODO: don't hard code this
        'DESCRIPTION': "Order %s-%s (including CC fees)" % (settings.EVENT_PAYMENT_PREFIX, order.get_reference_hash()),
        'LANGID': 'EN',
        'ALLOWCOLLECT': 'yes' if safersettings.ALLOW_COLLECT else 'no',
        'DELIVERY': 'yes' if safersettings.DELIVERY else 'no',
        'ACCOUNTID': safersettings.ACCOUNT_ID,
        'ORDERID': order.get_reference_hash(),
        'NOTIFYURL': domain + reverse('saferpay-response'), 
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
    #Check whether the order has been paid or blame someone. Hopefully the CC people
    try:
        order = CustomPreorder.objects.filter(user_id=request.user.pk, paid=False)
    except CustomPreorder.DoesNotExist,IndexError:
        pass    
    
    if len(order)<1:
        messages.success(request, _("Credit card payment was successful."))
    else:
        messages.info(request, _("Credit card payment was not successful. Please contact the tickets team"))
    return redirect("my-tickets")


#this is the view where we mark the payment as completed
#To allow saferpay to access the URL, we need to exclude it from the CSRF checking
@csrf_exempt
def response_view(request):
    # TODO: only allow from saferpay - not really needed, as we check with the VerifyURL against Saferpay
    # We get the PayConfirm per POST, lets check it
    data = {
    	'SIGNATURE': request.POST.get('SIGNATURE', ''),
        'DATA': request.POST.get('DATA', ''),
    	}
    if request.method == 'POST' and len(data['DATA'])>0:
        #Parse the data XML, returns a dict with the order data
        orderdata = ET.XML(data['DATA']).attrib    
        logger.info('Saferpay: Verifying DATA: %s, SIGNATURE %s', data['DATA'], data['SIGNATURE'])
        #Send the received Request to saferpay for checking whether it is a valid request 
        logger.debug('Saferpay: Sending request to %s with params %s', safersettings.VERIFY_URL, data)       
        response = requests.get(safersettings.VERIFY_URL, params=data)
        logger.info('Saferpay: Checking payment')
        if response.status_code == 200 and response.content.startswith('OK'):
            #response data looks like OK:ID=LOOOOONGID
            response_data = urlparse.parse_qs(response.content[3:])
            transaction_id = response_data['ID'][0]
            logger.info('Saferpay: Payment successfully checked, transaction ID %s, order ID %s', transaction_id, orderdata['ID'])

            #try to claim the money
            # If the transaction id from verify matches the former transaction id, get the UniqueId from the first request
            if transaction_id == orderdata['ID']:
                claimdata = {'ACCOUNTID':safersettings.ACCOUNT_ID,'ID':transaction_id}
                logger.info('Saferpay: Claiming %s', orderdata['ID'])
                logger.debug('Saferpay: Sending claiming request to %s with params %s', safersettings.PAYMENT_COMPLETE_URL, claimdata)
                claimresponse = requests.get(safersettings.PAYMENT_COMPLETE_URL, params=claimdata) 
                logger.debug('Claimrespone: %s', claimresponse.content)
                if claimresponse.status_code == 200 and claimresponse.content.startswith('OK'):
                    logger.info('Saferpay: Claim %s successfull', orderdata['ID'])
                    #money has been claimed!
                    try:
                        order = CustomPreorder.objects.get(Q(unique_secret__icontains=orderdata['ORDERID']))
                    except CustomPreorder.DoesNotExist:
                        logger.info('Saferpay: order failed, no preorder to pay')
                        return self.failure(request)
                    try:
                        total = order.get_sale_amount()[0]['total']
                        total_with_fees = total * (safersettings.EVENT_CC_FEE_PERCENTAGE/100+1) + safersettings.EVENT_CC_FEE_FIXED
                        total_with_fees = '%i' % (total_with_fees*100)

                        logger.debug('Fees: Computed: %s From CC: %s ', total_with_fees, orderdata['AMOUNT'])
                        if total_with_fees == orderdata['AMOUNT']:
                            order.paid = True
                            order.paid_time = datetime.datetime.now()
                            order.paid_via = "creditcard"
                            order.additional_info = "Paid by creditcard. Data: %s\nAmount Paid: %s" % (orderdata, total_with_fees)
                            order.save()
                            
                            logger.info('Order %s over %s marked as paid',order ,total)
                                                                         
                            if order.get_user().email:
                            # send notification email if email is set
                                send_mail("[%s] Update notification" % settings.EVENT_NAME_UNIX, settings.EVENT_PAYMENT_ACK_MAIL_TEXT, "%s <%s>" % (settings.EVENT_NAME_UNIX, settings.EVENT_CONTACT_MAILTO), (order.get_user().email,))
                            pass
                        else:
                            logger.info('Saferpay: order failed, the Amounts from CC handler and in the system don\'t match')
                            return self.failure(request)   
                    except KeyError:
                        logger.info('Saferpay: order failed, no preorder to pay')
                        return self.failure(request)
            logger.info('Saferpay: order %i\ttransaction: %s\tpayment verified', order.pk, transaction_id)                                                  
            order.save()
            
            return HttpResponse("Dave, this conversation can serve no purpose anymore. Goodbye.", content_type="text/plain")
    return redirect("my-tickets")
