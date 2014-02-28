from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
import logging


logger = logging.getLogger(__name__)


class DefaultViewTestCase(TestCase):
    """Series of tests to see if a user is presented with a link to the staff pages"""
    fixtures = ['users.json']

    def setUp(self):
        # Because the fixture might screw up permissions:
        user = User.objects.get(username='statsuser')
        perm = Permission.objects.get(codename='view_stats')
        user.user_permissions.add(perm)

        user = User.objects.get(username='csvuser')
        perm = Permission.objects.get(codename='change_paid_status')
        user.user_permissions.add(perm)


    def test_authenticated_user(self):
        response = self.client.get(reverse('default'), follow=False)
        self.assertNotContains(response,reverse('staff'))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        response = self.client.post(reverse('default'), follow=True)
        self.assertNotContains(response,reverse('staff'))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))


    def test_authenticated_user(self):
        response = self.client.login(username='normaluser',
                                     password='test')
        response = self.client.get(reverse('default'), follow=False)
        self.assertNotContains(response,reverse('staff'))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        response = self.client.post(reverse('default'), follow=True)
        self.assertNotContains(response,reverse('staff'))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))


    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser',
                                     password='test')
        response = self.client.get(reverse('default'), follow=False)
        self.assertNotContains(response,reverse('staff'))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        response = self.client.post(reverse('default'), follow=True)
        self.assertNotContains(response,reverse('staff'))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))


    def test_authenticated_statsuser(self):
        response = self.client.login(username='statsuser',
                                     password='test')
        response = self.client.get(reverse('default'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')

        response = self.client.post(reverse('default'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')

    def test_authenticated_csvuser(self):
        response = self.client.login(username='csvuser',
                                     password='test')
        response = self.client.get(reverse('default'), follow=False)
        logger.debug(response)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')
        response = self.client.post(reverse('default'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser',
                                     password='test')
        response = self.client.get(reverse('default'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')
        response = self.client.post(reverse('default'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')


class StaffDefaultViewTestCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        # Because the fixture might screw up permissions:
        user = User.objects.get(username='statsuser')
        perm = Permission.objects.get(codename='view_stats')
        user.user_permissions.add(perm)

        user = User.objects.get(username='csvuser')
        perm = Permission.objects.get(codename='change_paid_status')
        user.user_permissions.add(perm)

    def test_unauthenticated_user(self):
        response = self.client.get(reverse('staff'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff')))
        response = self.client.post(reverse('staff'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff')))


    def test_authenticated_user(self):
        response = self.client.login(username='normaluser',
                                     password='test')
        response = self.client.get(reverse('staff'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff')))
        response = self.client.post(reverse('staff'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser',
                                     password='test')
        response = self.client.get(reverse('staff'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff')))
        response = self.client.post(reverse('staff'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff')))

    def test_authenticated_statsuser(self):
        response = self.client.login(username='statsuser',
                                     password='test')
        response = self.client.get(reverse('staff'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')
        response = self.client.post(reverse('staff'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertNotContains(response,reverse('staff-import-csv'))
        self.assertContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')

    def test_authenticated_csvuser(self):
        response = self.client.login(username='csvuser',
                                     password='test')
        response = self.client.get(reverse('staff'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')
        response = self.client.post(reverse('staff'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertContains(response,reverse('staff-import-csv'))
        self.assertNotContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser',
                                     password='test')
        response = self.client.get(reverse('staff'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertContains(response,reverse('staff-import-csv'))
        self.assertContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')
        response = self.client.post(reverse('staff'), follow=False)
        self.assertContains(response,'<a href="{}">'.format(reverse('staff')))
        self.assertContains(response,reverse('staff-import-csv'))
        self.assertContains(response,reverse('staff-statistics'))
        self.assertNotContains(response,reverse('staff-statistics-charts'))
        self.assertTemplateUsed('staff/default.html')


class StaffStatsViewTestCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        # Because the fixture might screw up permissions:
        user = User.objects.get(username='statsuser')
        perm = Permission.objects.get(codename='view_stats')
        user.user_permissions.add(perm)

        user = User.objects.get(username='csvuser')
        perm = Permission.objects.get(codename='change_paid_status')
        user.user_permissions.add(perm)

    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('staff-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))
        response = self.client.post(reverse('staff-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))

    def test_authenticated_user(self):
        response = self.client.login(username='normaluser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))
        response = self.client.post(reverse('staff-statistics'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))
        response = self.client.post(reverse('staff-statistics'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))

    def test_authenticated_statsuser(self):
        response = self.client.login(username='statsuser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/default.html')
        response = self.client.post(reverse('staff-statistics'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/statistics.html')

    def test_authenticated_csvuser(self):
        response = self.client.login(username='csvuser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))
        response = self.client.post(reverse('staff-statistics'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics')))

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/statistics.html')


class StaffStatsChartsViewTestCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        # Because the fixture might screw up permissions:
        user = User.objects.get(username='statsuser')
        perm = Permission.objects.get(codename='view_stats')
        user.user_permissions.add(perm)

        user = User.objects.get(username='csvuser')
        perm = Permission.objects.get(codename='change_paid_status')
        user.user_permissions.add(perm)

    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('staff-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))
        response = self.client.post(reverse('staff-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))

    def test_authenticated_user(self):
        response = self.client.login(username='normaluser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))
        response = self.client.post(reverse('staff-statistics-charts'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))
        response = self.client.post(reverse('staff-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))

    def test_authenticated_statsuser(self):
        response = self.client.login(username='statsuser',
                                     password='test')
        response = self.client.get(reverse('staff'), follow=False)
        response = self.client.get(reverse('staff-statistics-charts'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/statistics_charts.html')
        response = self.client.post(reverse('staff-statistics-charts'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/statistics_charts.html')

    def test_authenticated_csvuser(self):
        response = self.client.login(username='csvuser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))
        response = self.client.post(reverse('staff-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-statistics-charts')))

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser',
                                     password='test')
        response = self.client.get(reverse('staff-statistics-charts'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/statistics_charts.html')
        response = self.client.post(reverse('staff-statistics-charts'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/statistics_charts.html')


class StaffCsvImportViewTestCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        # Because the fixture might screw up permissions:
        user = User.objects.get(username='statsuser')
        perm = Permission.objects.get(codename='view_stats')
        user.user_permissions.add(perm)

        user = User.objects.get(username='csvuser')
        perm = Permission.objects.get(codename='change_paid_status')
        user.user_permissions.add(perm)

    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('staff-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))
        response = self.client.post(reverse('staff-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))

    def test_authenticated_user(self):
        response = self.client.login(username='normaluser',
                                     password='test')
        response = self.client.get(reverse('staff-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))
        response = self.client.post(reverse('staff-import-csv'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser',
                                     password='test')
        response = self.client.get(reverse('staff-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))
        response = self.client.post(reverse('staff-import-csv'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))

    def test_authenticated_statsuser(self):
        response = self.client.login(username='statsuser',
                                     password='test')
        response = self.client.get(reverse('staff-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))
        response = self.client.post(reverse('staff-import-csv'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('staff-import-csv')))

    def test_authenticated_csvuser(self):
        response = self.client.login(username='csvuser',
                                     password='test')
        response = self.client.get(reverse('staff-import-csv'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/import_csv.html')
        response = self.client.post(reverse('staff-import-csv'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/import_csv.html')

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser',
                                     password='test')
        response = self.client.get(reverse('staff-import-csv'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('staff/import_csv.html')
