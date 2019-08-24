import datetime
import pytz

from django.contrib.auth.models import User
from django.test import TestCase

from core.models import Book

try:
    from django.core.urlresolvers import reverse
except ImportError:  # Django 2.0
    from django.urls import reverse


class DjangoQLAdminTest(TestCase):
    def setUp(self):
        self.credentials = {'username': 'test', 'password': 'lol'}
        User.objects.create_superuser(email='herp@derp.rr', **self.credentials)
        _users = [
            {'username': 'user1', 'password': 'lol', 'email': 'user1@derp.rr'},
            {'username': 'User1', 'password': 'lol', 'email': 'user_1@derp.rr'},
            {'username': 'user2', 'password': 'lol', 'email': 'user2@derp.rr'},
            {'username': 'user3', 'password': 'lol', 'email': 'user3@derp.rr'},
        ]
        User.objects.bulk_create([User(**user) for user in _users])

        users = {user.username: user for user in User.objects.all()}
        _books = [
            {'name': 'Dive into Python', 'author': 'user1', 'genre': 1,
             'written': datetime.datetime(year=2017, month=3, day=15, tzinfo=pytz.utc),
             'is_published': True, 'rating': 5.0, 'price': 1234.56},
            {'name': 'Python cookbook', 'author': 'User1', 'genre': 2,
             'written': datetime.datetime(year=2018, month=4, day=25, tzinfo=pytz.utc),
             'is_published': True, 'rating': 6.0, 'price': 2233.55},
            {'name': 'Python programming', 'author': 'user1', 'genre': 2,
             'written': datetime.datetime(year=2018, month=1, day=5, tzinfo=pytz.utc),
             'is_published': True, 'rating': 4.0, 'price': 3322.77},
            {'name': 'Django framework', 'author': 'user2', 'genre': 3,
             'written': datetime.datetime(year=2019, month=7, day=11, tzinfo=pytz.utc),
             'is_published': False},
            {'name': 'Ruby on Rails', 'author': 'user3', 'genre': 1,
             'written': datetime.datetime(year=2018, month=2, day=10, tzinfo=pytz.utc),
             'is_published': True, 'rating': 7.0, 'price': 2131.91},
            {'name': 'Yii2 framework', 'author': 'user2', 'genre': 3,
             'written': datetime.datetime(year=2017, month=9, day=24, tzinfo=pytz.utc),
             'is_published': True, 'rating': 6.5, 'price': 2315.54},
        ]

        for item in _books:
            item['author'] = users[item['author']]

        Book.objects.bulk_create([Book(**data) for data in _books])

    def test_sync(self):
        url = reverse('admin:core_book_changelist')
        self.assertTrue(self.client.login(**self.credentials))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(set(Book.objects.all()), set(response.context['cl'].result_list))

    def test_async(self):
        url = reverse('admin:core_book_changelist')
        self.assertTrue(self.client.login(**self.credentials))
        response = self.client.get(url, {"q": "is_published = True"}, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(200, response.status_code)
        djangoql_result_limit = response.context['cl'].model_admin.djangoql_result_limit
        self.assertEqual(set(Book.objects.filter(is_published=True).order_by('-pk')[:djangoql_result_limit]),
                         set(response.context['cl'].result_list))
