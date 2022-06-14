from datetime import datetime
from distutils.log import error
from itertools import product
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from clicoh.models import Order, OrderDetail, Product


class ClickOhTest(TestCase):

    def setUp(self):

        get_user_model().objects.create_user(
            username='user', password='pass', is_active=True)

        self.client = APIClient()
        response = self.client.post(reverse(
            'api-jwt-auth'), {'username': 'user', 'password': 'pass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_login(self):
        response = self.client.get(
            reverse('product-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductTest(ClickOhTest):
    def setUp(self):
        super().setUp()
        self.product_data = {
            'name': 'Mesa de comedor',
            'price': 50,
            'stock': 10
        }
        self.product = Product.objects.create(**self.product_data)

    def test_product_creation(self):
        self.product_data["nombre"] = "Silla"
        response = self.client.post(
            reverse('product-list'), self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        self.assertIsNotNone(data['id'])
        self.assertEqual(data['name'], self.product_data['name'])
        self.assertEqual(data['price'], self.product_data['price'])
        self.assertEqual(data['stock'], self.product_data['stock'])

    def test_product_edit(self):
        self.product_data['name'] = 'new_name'
        response = self.client.put(reverse(
            'product-list') + f'{self.product.id}/', self.product_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['name'], 'new_name')

    def test_product_delete(self):
        response = self.client.delete(
            reverse('product-list') + f'{self.product.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Product.objects.all()), 0)

    def test_product_list(self):
        response = self.client.get(
            reverse('product-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(len(data), 1)
        p = data[0]
        self.assertEqual(p['name'], self.product_data['name'])
        self.assertEqual(p['price'], self.product_data['price'])
        self.assertEqual(p['stock'], self.product_data['stock'])

    def test_product_stock_change(self):
        new_stock = 100
        response = self.client.patch(
            reverse('product-list') + f'{self.product.id}/', {'stock': new_stock}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['stock'], new_stock)


class OrderCreationTest(ClickOhTest):
    def setUp(self) -> None:
        super().setUp()
        self.order_data = {
            "date_time": "2022-06-12",
            "order_detail": [
                {
                    "quantity": 1,
                    "product": {"id": 1}
                },
                {
                    "quantity": 2,
                    "product": {"id": 2}
                }
            ]
        }
        Product.objects.create(name="Silla", stock=100, price=100)
        Product.objects.create(name="Mesa", stock=100, price=200)

    def test_creacion_ok(self):
        response = self.client.post(
            reverse('order-list'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_data = response.data
        self.assertEqual(len(order_data["order_detail"]), 2)
        self.assertIsNotNone(order_data["total"])
        self.assertIsNotNone(order_data["total_usd"])
        self.assertEqual(Product.objects.get(pk=1).stock, 99)
        self.assertEqual(Product.objects.get(pk=2).stock, 98)

    def test_creacion_product_repeated(self):
        p = self.order_data["order_detail"].append({
            "quantity": 1,
            "product": {"id": 2}
        })
        response = self.client.post(
            reverse('order-list'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.get(pk=1).stock, 100)
        self.assertEqual(Product.objects.get(pk=2).stock, 100)
        error_data = response.data
        self.assertTrue('order_detail' in error_data)
        errors = error_data["order_detail"]
        self.assertTrue(len(errors) >= 1)
        
    def test_creacion_product_not_enough_stock(self):
        self.order_data["order_detail"][0]["quantity"] = 500

        response = self.client.post(
            reverse('order-list'), self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.get(pk=1).stock, 100)
        self.assertEqual(Product.objects.get(pk=2).stock, 100)
        error_data = response.data
        self.assertTrue('order_detail' in error_data)
        errors = error_data["order_detail"]
        self.assertTrue(len(errors) >= 1)        

class OrderEditingTest(ClickOhTest):
    def setUp(self) -> None:
        super().setUp()
        p1 = Product.objects.create(name="Silla", stock=99, price=100)
        p2 = Product.objects.create(name="Mesa", stock=99, price=200)
        p3 = Product.objects.create(name="Banco", stock=99, price=300)
        self.order = Order.objects.create(date_time=datetime(2022, 5, 17))
        self.order.order_detail.create(quantity=1, product=p1)
        self.order.order_detail.create(quantity=1, product=p2)
        self.order.order_detail.create(quantity=10, product=p3)

    def test_order_edit(self):
        data = {
            "date_time": "2022-01-01",
            "order_detail": [
                {
                    "id": 1,
                    "quantity": 100,
                    "product": {"id": 1}
                },
                {
                    "id": 2,
                    "quantity": 50,
                    "product": {"id": 2}
                },
                {
                    "id": 3,
                    "quantity": 0,
                    "product": {"id": 3}
                }
            ]
        }
        response = self.client.put(
            reverse('order-list') + '1/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = response.data
        self.assertEqual(order_data["date_time"], "2022-01-01")
        self.assertEqual(len(order_data["order_detail"]), 2)
        self.assertEqual(Product.objects.get(pk=1).stock, 0)
        self.assertEqual(Product.objects.get(pk=2).stock, 50)
        od = OrderDetail.objects.filter(product_id=1).first()
        self.assertEqual(od.quantity, 100)

    def test_order_edit_stock_unavailable(self):
        data = {
            "date_time": "2022-01-01",
            "order_detail": [
                {
                    "id": 1,
                    "quantity": 100,
                    "product": {"id": 1}
                },
                {
                    "id": 2,
                    "quantity": 50,
                    "product": {"id": 2}
                },
                {
                    "id": 3,
                    "quantity": 200,
                    "product": {"id": 3}
                }
            ]
        }
        response = self.client.put(
            reverse('order-list') + '1/', data, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = response.data
        self.assertEqual(
            response_data["detail"], "Error de integridad de datos (CHECK constraint failed: clicoh_product)")


class OrderDeletionTestCase(ClickOhTest):
    def setUp(self) -> None:
        super().setUp()
        p1 = Product.objects.create(name="Silla", stock=100, price=100)
        self.order = Order.objects.create(date_time=datetime(2022, 5, 17))
        self.order.order_detail.add(OrderDetail(
            quantity=10, product=p1), bulk=False)

    def test_delete(self):
        response = self.client.delete(
            reverse('order-list') + '1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Order.objects.count(), 0)
        product = Product.objects.get(pk=1)
        self.assertEqual(product.stock, 110)
