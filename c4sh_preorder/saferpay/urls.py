from django.conf.urls import patterns, url, include

urlpatterns = patterns('saferpay.views',
    url(r'^f/$', 'fail_view', name='saferpay-fail'),
    url(r'^a/$', 'abort_view', name='saferpay-abort'),
    url(r'^r/$', 'response_view', name='saferpay-response'),
    url(r'^c/$', 'complete_view', name='saferpay-complete'),
    url(r'^p/$', 'pay_view', name='saferpay-pay'),
)