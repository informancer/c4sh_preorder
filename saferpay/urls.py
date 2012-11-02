from django.conf.urls import patterns, url, include

urlpatterns = patterns('saferpay.views',
    url(r'^saferpay/f/$', 'fail_view', name='saferpay-fail'),
    url(r'^saferpay/a/$', 'abort_view', name='saferpay-abort'),
    url(r'^saferpay/r/$', 'response_view', name='saferpay-response'),
    url(r'^saferpay/c/$', 'complete_view', name='saferpay-complete'),
)