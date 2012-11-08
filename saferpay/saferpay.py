import urlparse

from django.conf.urls.defaults import patterns, url
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.utils.translation import get_language, ugettext_lazy as _
import requests

import settings
import logging

logger = logging.getLogger('payment.saferpay')


def pay(request):
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
    total = total * (settings.EVENT_CC_FEE_PERCENTAGE/100+1) + settings.EVENT_CC_FEE_FIXED
    domain = '%s://%s/' % (protocol, settings.APP_URL)
    data = {
        'AMOUNT': int(total * 100),
        'CURRENCY': 'EUR', # TODO: don't hard code this
        'DESCRIPTION': "Order %s-%s (including CC fees)" % (settings.EVENT_PAYMENT_PREFIX, order.get_reference_hash()),
        'LANGID': 'EN',
        'ALLOWCOLLECT': 'yes' if settings.ALLOW_COLLECT else 'no',
        'DELIVERY': 'yes' if settings.DELIVERY else 'no',
        'ACCOUNTID': settings.ACCOUNT_ID,
        'ORDERID': order.get_reference_hash(),
        'SUCCESSLINK': domain +  reverse('saferpay-verify'),
        'BACKLINK': domain + reverse('saferpay-abort'),
        'FAILLINK': domain + reverse('saferpay-fail'),
        
    }
    for style in ('BODYCOLOR', 'HEADCOLOR', 'HEADLINECOLOR', 'MENUCOLOR', 'BODYFONTCOLOR', 'HEADFONTCOLOR', 'MENUFONTCOLOR', 'FONT'):
        style_value = getattr(settings, style)
        if style_value is not None:
            data[style] = style_value
    
    response = requests.get(settings.PROCESS_URL, params=data)
    logger.info('Saferpay: order %d\tredirected to saferpay gateway', order.pk)
    return HttpResponseRedirect(response.content)
"""

def verify(self, request):
    order = self.shop.get_order(request)
    if not order:
        return self.failure(request)
    data = {
        'SIGNATURE': request.GET.get('SIGNATURE', ''),
        'DATA': request.GET.get('DATA', ''),
    }
    logger.info('Saferpay: order %i\tverifying , DATA: %s, SIGNATURE %s', order.pk, data['DATA'], data['SIGNATURE'])
    response = requests.get(settings.VERIFY_URL, params=data)
    if response.status_code == 200 and response.content.startswith('OK'):
        response_data = urlparse.parse_qs(response.content[3:])
        transaction_id = response_data['ID'][0]
        self.shop.confirm_payment(order, self.shop.get_order_total(order), transaction_id, self.backend_name)
        params = {'ACCOUNTID': settings.ACCOUNT_ID, 'ID': transaction_id, 'spPassword': settings.ACCOUNT_PASSWORD}
        logger.info('Saferpay: order %i\ttransaction: %s\tpayment verified', order.pk, transaction_id)
        if settings.USE_CELERY:
            payment_complete.delay(params=params, order_id=order.pk)
        else:
            try:
                payment_complete(params=params, order_id=order.pk)
            except Exception:
                pass # this is already logged in payment_complete
        order.save()  # force order.modified to be bumped (we rely on this in the "thank you" view)
        return self.success(request)
    return self.failure(request)

def finish(url=settings.PAYMENT_COMPLETE_URL, params=None, order_id=None):
    if params is None:
        params = {}
    if settings.USE_PAYMENT_COMPLETE_URL:
        try:
            response = requests.get(url, timeout=10, params=params)
            if response.ok:
                logger.info('Saferpay: order %i\tcompletion of payment SUCCEEDED', order_id)
                return response.content
            else:
                raise response.error
        except Exception, exc:
            if celery_task:
                payment_complete.retry(exc=exc, countdown=5*60)
            else:
                logger.error('Saferpay: order %i\tcompletion of payment FAILED', order_id)
                raise
"""
