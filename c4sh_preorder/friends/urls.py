# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from c4sh_preorder.settings import MEDIA_ROOT, STATIC_ROOT

urlpatterns = patterns('c4sh_preorder.friends.views',
    url(r'^$', 'friends_apply', name='friends-apply'),
    url(r'^review/(?P<secret>(\w+))/$', 'friends_review', name='friends-review'),
)
