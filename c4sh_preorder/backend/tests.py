from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
import logging


__doc__ = "Tests for the different admin views and access related links"

logger = logging.getLogger(__name__)


# Because the access tests are extremely repetitive
# and I didn't want to put stuff all around:
# let's generate some tests.

# Each view can be tested along different axes:
# - User status (logged in or not) and their permissions.
# - Access to a given view or not
# - Given the access, should a link to a page be shown?

# Let's start by checking what kind of users we'll use:

# All passwords are set to 'test'
USERS = [None,
         'normaluser',
         # Stats users can see the stats,
         # but can't do anything about payments.
         'statsuser',
         # CSV Users can upload csvs and change the status of a
         # payment,
         # they don't really need to see the stats.
         'csvuser', 
         # Staff user can log in the admin site,
         # does not mean they should be able to see stats
         # or change the status of a payment.
         'staffuser',
         # Superusers have all rights, per definition.
         'superuser']


# This gives us the following access rights:
ACCESS = {'default': {None: True,
                      'normaluser': True,
                      'statsuser': True,
                      'csvuser': True,
                      'staffuser': True,
                      'superuser': True},
          'staff': {None: False,
                    'normaluser': False,
                    'statsuser': True,
                    'csvuser': True,
                    'staffuser': False,
                    'superuser': True},
          'staff-statistics': {None: False,
                               'normaluser': False,
                               'statsuser': True,
                               'csvuser': False,
                               'staffuser': False,
                               'superuser': True},
          'staff-statistics-charts': {None: False,
                                      'normaluser': False,
                                      'statsuser': True,
                                      'csvuser': False,
                                      'staffuser': False,
                                      'superuser': True},
          'staff-import-csv': {None: False,
                               'normaluser': False,
                               'statsuser': False,
                               'csvuser': True,
                               'staffuser': False,
                               'superuser': True}}

# All these view have a template:
TEMPLATES = {'default': 'default.html',
             'staff': 'staff/default.html',
             'staff-statistics': 'staff/statistics.html',
             'staff-statistics-charts': 'staff/statistics_charts.html',
             'staff-import-csv': 'staff/import_csv.html'}


# Not all links are available in all templates,
# so we'll nee a representation 
LINKS = {'default': {'default': True,
                     'staff': True,
                     'staff-statistics': False,
                     'staff-statistics-charts': False,
                     'staff-import-csv': False},
         'staff': {'default': True,
                   'staff': True,
                   'staff-statistics': True,
                   'staff-statistics-charts': False,
                   'staff-import-csv': True},
         'staff-statistics': {'default': True,
                              'staff': True,
                              'staff-statistics': True,
                              'staff-statistics-charts': True,
                              'staff-import-csv': True},
         'staff-statistics-charts': {'default': True,
                                     'staff': True,
                                     'staff-statistics': True,
                                     'staff-statistics-charts': True,
                                     'staff-import-csv': True},
         'staff-import-csv': {'default': True,
                              'staff': True,
                              'staff-statistics': True,
                              'staff-statistics-charts': False,
                              'staff-import-csv': True}}

# And now, we only need to create methods out of all this data,
# and attach them to

class AccessTestCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        # Because the fixture might screw up permissions:
        user = User.objects.get(username='statsuser')
        perm = Permission.objects.get(codename='view_stats')
        user.user_permissions.add(perm)

        user = User.objects.get(username='csvuser')
        perm = Permission.objects.get(codename='change_paid_status')
        user.user_permissions.add(perm)

    def TestAccess(self):
        for view, access in ACCESS.iteritems():
            logger.debug('Checking access for view: %s', view)
            for user in USERS:
                logger.debug('Checking user: %s', user)
                # Log in if we need to
                if user:
                    response = self.client.login(username=user,
                                                 password='test')
                # We want to try both http methods.
                for method in ['get', 'post']:
                    response = getattr(self.client, method)(reverse(view), follow=False)
                    if access[user]:
                        # We have access, let's check the template
                        self.assertTemplateUsed(TEMPLATES[view])
                        # And see if we only see the relevant links.
                        for link, present in LINKS[view].iteritems():
                            if present and ACCESS[link][user]:
                                logger.debug('Checking availability of link to %s',
                                             link)
                                self.assertContains(response,reverse(link))
                            else:
                                logger.debug('Checking unavailability of link to %s',
                                             link)
                                self.assertNotContains(response,reverse(link))
                    else:
                        # Nope, no access, just check that we got redirected.
                        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                                           reverse(view)),
                                             msg_prefix='{}@{}'.format(user, view))
                self.client.logout()


