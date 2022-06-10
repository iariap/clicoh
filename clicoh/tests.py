from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
# Create your tests here.


class Test_ProductTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_product_creation(self):
        p = {
            'name': 'Mesa de comedor',
            'price': 50,
            'stock': 10
        }
        response = self.client.post(reverse('product-list'), p, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertEqual(data['name'], p['name'])
        self.assertEqual(data['price'], p['price'])
        self.assertEqual(data['stock'], p['stock'])

    def test_product_edit(self):
        p = {
            'name': 'Mesa de comedor',
            'price': 50,
            'stock': 10
        }
        response = self.client.post(reverse('product-list'), p, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        

    def test_product_delete(self):
        ...

    def test_product_list(self):
        ...

    def test_product_stock_change(self):
        ...


class OrderTest(TestCase):
    ...


class OrderDetail(TestCase):
    ...
