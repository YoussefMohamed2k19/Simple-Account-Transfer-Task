from rest_framework.test import APIClient
from .models import Account, Transaction
from rest_framework import status
from django.test import TestCase
import csv
import io

class AccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_account(self):
        response = self.client.post('/api/accounts/', {'id': 'cc26b56c-36f6-41f1-b689-d1d5065b95yx','name': 'Test Account', 'balance': 1000})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_transfer_funds(self):
        acc1 = Account.objects.create(id='cc26b56c-36f6-41f1-b689-d1d5065b95ax', name='Account 1', balance=1000)
        acc2 = Account.objects.create(id="cc26b56c-36f6-41f1-b689-d1d5065b95ay", name='Account 2', balance=500)
        response = self.client.post(f'/api/accounts/{acc1.id}/transfer/', {'to_account': acc2.id, 'amount': 200})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_import_accounts(self):
        file = io.StringIO()
        writer = csv.writer(file)
        writer.writerow(['id','name', 'balance'])
        writer.writerow(['Account 1', 1000])
        writer.writerow(['Account 2', 500])
        file.seek(0)
        response = self.client.post('/api/accounts/import_accounts/', {'file': file})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
