from django.db import models
from .services import DolarService
from django.core.validators import MinValueValidator

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255, blank=False)
    price = models.FloatField(blank=False)
    stock = models.PositiveIntegerField(blank=False)


class Order(models.Model):
    date_time = models.DateTimeField(auto_now=True)

    def get_total(self):
        return sum([order.quantity * order.product.price for order in OrderDetail.objects.filter(order_id=self.id)])

    def get_total_usd(self):
        cotizacion = DolarService.get_cotizacion()
        return self.get_total() * cotizacion


class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=False, related_name='order_detail')
    quantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)

    class Meta:
        # * que no se repitan productos en el mismo pedido
        unique_together = ('order', 'product')
