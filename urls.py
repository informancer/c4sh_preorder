# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from c4sh_preorder.settings import MEDIA_ROOT, STATIC_ROOT

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT, 'show_indexes': False}),
)

import sys
if (sys.argv[1] == 'runserver'):
    urlpatterns += patterns('',
        url(r'^admin42/', include(admin.site.urls)),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': STATIC_ROOT, 'show_indexes': False}),
    )

urlpatterns += patterns('c4sh_preorder.preorder.app_views',
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
    url(r'^passbook/(?P<preorder_id>(\d+))/(?P<secret>(\w+))/$', 'passbook_view', name='passbook'),
)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
    url(r'^cc/', include('saferpay.urls')),
)

urlpatterns += patterns('c4sh_preorder.preorder.admin_views',
    url(r'^admin/$', 'default_view', name='admin'),
    url(r'^admin/import-csv/$', 'import_csv_view', name='admin-import-csv'),
    url(r'^admin/statistics/$', 'statistics_view', {'section': False}, name='admin-statistics'),
    url(r'^admin/statistics/charts/$', 'statistics_view', {'section': 'charts'}, name='admin-statistics-charts'),

    url(r'^admin/api/get-preorder.json$', 'api_get_preorder_view', name='admin-api-get-preorder')
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'default.html'}, name="login"),
    url(r'^logout/$', 'logout', {'next_page': '/'}, name="logout"),
    url(r'^password-reset/$', 'password_reset', {'is_admin_site': False, 'template_name': 'base/password_reset.html'}, name="password-reset"),
    url(r'^password-reset/done/$', 'password_reset_done', {'template_name': 'base/password_reset_confirm.html'}, name="password-reset-done"),
    url(r'^password-reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm', {'template_name': 'base/password_reset_form.html'}, name="password-reset-confirm"),
    url(r'^password-reset/complete/$', 'password_reset_complete', {'template_name': 'base/password_reset_complete.html'}, name="password-reset-complete")
)
