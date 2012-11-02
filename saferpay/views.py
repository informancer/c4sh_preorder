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
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.template import Context

###### VIEWS #######

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
