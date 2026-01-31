from django.test import TestCase
from django.urls import reverse

class PollsTest(TestCase):
    def test_admin_accessible(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
