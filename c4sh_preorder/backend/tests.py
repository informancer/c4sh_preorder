from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
import logging


logger = logging.getLogger(__name__)


class AdminDefaultViewTestCase(TestCase):
    fixtures = ['users.json']
    
    def test_unauthenticated_user(self):
        response = self.client.get(reverse('admin'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin')))
        response = self.client.post(reverse('admin'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin')))

    def test_authenticated_user(self):
        response = self.client.login(username='normaluser', 
                                     password='test')
        response = self.client.get(reverse('admin'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin')))
        response = self.client.post(reverse('admin'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser', 
                                     password='test')
        response = self.client.get(reverse('admin'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/default.html')
        response = self.client.post(reverse('admin'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/default.html')

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser', 
                                     password='vagrant')
        response = self.client.get(reverse('admin'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/default.html')
        response = self.client.post(reverse('admin'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/default.html')


class AdminStatsViewTestCase(TestCase):
    fixtures = ['users.json']
    
    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('admin-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics')))
        response = self.client.post(reverse('admin-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics')))

    def test_authenticated_user(self):
        response = self.client.login(username='normaluser', 
                                     password='test')
        response = self.client.get(reverse('admin-statistics'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics')))
        response = self.client.post(reverse('admin-statistics'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser', 
                                     password='test')
        response = self.client.get(reverse('admin-statistics'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/statistics.html')
        response = self.client.post(reverse('admin-statistics'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/statistics.html')

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser', 
                                     password='vagrant')
        response = self.client.get(reverse('admin-statistics'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/statistics.html')


class AdminStatsChartsViewTestCase(TestCase):
    fixtures = ['users.json']
    
    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('admin-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics-charts')))
        response = self.client.post(reverse('admin-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics-charts')))

    def test_authenticated_user(self):
        response = self.client.login(username='normaluser', 
                                     password='test')
        response = self.client.get(reverse('admin-statistics-charts'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics-charts')))
        response = self.client.post(reverse('admin-statistics-charts'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-statistics-charts')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser', 
                                     password='test')
        response = self.client.get(reverse('admin-statistics-charts'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/statistics_charts.html')
        response = self.client.post(reverse('admin-statistics-charts'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/statistics_charts.html')

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser', 
                                     password='vagrant')
        response = self.client.get(reverse('admin-statistics-charts'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/statistics_charts.html')


class AdminCsvImportViewTestCase(TestCase):
    fixtures = ['users.json']
    
    def test_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('admin-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-import-csv')))
        response = self.client.post(reverse('admin-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-import-csv')))

    def test_authenticated_user(self):
        response = self.client.login(username='normaluser', 
                                     password='test')
        response = self.client.get(reverse('admin-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-import-csv')))
        response = self.client.post(reverse('admin-import-csv'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-import-csv')))

    def test_authenticated_staffuser(self):
        response = self.client.login(username='staffuser', 
                                     password='test')
        response = self.client.get(reverse('admin-import-csv'), follow=False)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-import-csv')))
        response = self.client.post(reverse('admin-import-csv'), follow=True)
        self.assertRedirects(response, '{}?next={}'.format(reverse('login'),
                                                           reverse('admin-import-csv')))

    def test_authenticated_superuser(self):
        response = self.client.login(username='superuser', 
                                     password='vagrant')
        response = self.client.get(reverse('admin-import-csv'), follow=False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('admin/import_csv.html')
