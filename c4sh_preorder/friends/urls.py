# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.http import HttpResponse
from c4sh_preorder.settings import MEDIA_ROOT, STATIC_ROOT

urlpatterns = patterns('c4sh_preorder.friends.views',
    url(r'^$', 'friends_apply', name='friends-apply'),
    url(r'^b70f1a8fcc5047575f92200122b9a4dc2742aabf/(?P<secret>(\w+))/$', 'friends_review', name='friends-review'),
)
