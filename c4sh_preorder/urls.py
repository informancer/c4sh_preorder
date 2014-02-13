# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from django.contrib import admin
from c4sh_preorder.settings import MEDIA_ROOT, STATIC_ROOT, EVENT_BEZAHLCODE_ENABLE
admin.autodiscover()

urlpatterns = patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT, 'show_indexes': False}),
)

import sys
import os
if (sys.argv[1] in ['runserver', 'runserver_plus'] or os.environ.get('ENABLE_ADMIN_ROUTES', False)):
	urlpatterns += patterns('',
		url(r'^admin42/', include(admin.site.urls)),
		(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT, 'show_indexes': False}),
	)

urlpatterns += patterns('c4sh_preorder.backend.views',
			url(r'^staff/$', 'default_view', name='staff'),
			url(r'^staff/import-csv/$', 'import_csv_view', name='staff-import-csv'),
			url(r'^staff/statistics/$', 'statistics_view', {'section': False}, name='staff-statistics'),
			url(r'^staff/statistics/charts/$', 'statistics_view', {'section': 'charts'}, name='staff-statistics-charts'),
			url(r'^staff/api/get-preorder\.json$', 'api_get_preorder_view', name='staff-api-get-preorder')
	)
urlpatterns += patterns('c4sh_preorder.preorder.views',
	url(r'^$', 'default_view', name='default'),
	url(r'^signup/$', 'signup_view', name='signup'),
	url(r'^account/$', 'account_view', name='account'),
	url(r'^cart/add/$', 'cart_view', {'action': 'add'}, name='cart-add'),
	url(r'^cart/amend/$', 'cart_view', {'action': 'amend'}, name='cart-amend'),
	url(r'^cart/delete/$', 'cart_view', {'action': 'delete'}, name='cart-delete'),
	url(r'^checkout/$', 'checkout_view', name='checkout'),
	url(r'^order/$', 'order_view', name='order'),
	url(r'^tickets/$', 'tickets_view', name='my-tickets'),
	url(r'^redeem-token/$', 'redeem_token_view', name='redeem-token'),
	url(r'^whoops/$', 'no_view', name='no-more-preorder'),
	url(r'^print/(?P<preorder_id>(\d+))/(?P<secret>(\w+))/$', 'print_tickets_view', name='print-tickets'),
	url(r'^invoice/(?P<preorder_id>(\d+))/(?P<secret>(\w+))/$', 'print_invoice_view', name='print-invoice'),
	url(r'^passbook/(?P<preorder_id>(\d+))/(?P<secret>(\w+))/$', 'passbook_view', name='passbook'),
)

if EVENT_BEZAHLCODE_ENABLE:
	urlpatterns += patterns('c4sh_preorder.preorder.views', url(r'^tickets/bezahlcode\.png$', 'bezahlcode_view', name='bezahlcode'))

urlpatterns += patterns('',
	url(r'^captcha/', include('captcha.urls')),
	url(r'^friends/', include('c4sh_preorder.friends.urls')),
	url(r'^cc/', include('saferpay.urls')),
	url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", mimetype="text/plain"))
)

urlpatterns += patterns('django.contrib.auth.views',
	url(r'^login/$', 'login', {'template_name': 'default.html'}, name="login"),
	url(r'^logout/$', 'logout', {'next_page': '/'}, name="logout"),
	url(r'^password-reset/$', 'password_reset', {'is_admin_site': False, 'template_name': 'base/password_reset.html'}, name="password-reset"),
	url(r'^password-reset/done/$', 'password_reset_done', {'template_name': 'base/password_reset_confirm.html'}, name="password-reset-done"),
	url(r'^password-reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm', {'template_name': 'base/password_reset_form.html'}, name="password-reset-confirm"),
	url(r'^password-reset/complete/$', 'password_reset_complete', {'template_name': 'base/password_reset_complete.html'}, name="password-reset-complete")
)
