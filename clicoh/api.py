from django.db.models import F
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, serializers
from .models import Order, OrderDetail, Product


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(min_value=0)
    stock = serializers.IntegerField(min_value=0)

    class Meta:
        model = Product
        fields = ('id', 'price', 'stock', 'name',)


@permission_classes([IsAuthenticated])
class ProductViewSet(viewsets.ModelViewSet):
    """API de Productos """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderDetailProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    price = serializers.FloatField(read_only=True)
    stock = serializers.FloatField(read_only=True)
    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock')


class OrderDetailSerializer(serializers.ModelSerializer):
    product = OrderDetailProductSerializer()
    quantity = serializers.IntegerField(min_value=0)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = OrderDetail
        fields = ('id', 'quantity', 'product',)


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.FloatField(source='get_total', read_only=True)
    total_usd = serializers.FloatField(source='get_total_usd', read_only=True)
    order_detail = OrderDetailSerializer(many=True)
    date_time = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Order
        fields = ('id', 'date_time', 'total', 'total_usd', 'order_detail',)

    def create(self, validated_data):
        order_detail_data = validated_data.pop('order_detail')

        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for od in order_detail_data:
                order.order_detail.create(
                    quantity=od["quantity"],
                    product_id=od["product"]["id"]
                )

                # actualiza el stock del producto
                try:
                    with transaction.atomic():  # create a savepoint
                        Product.objects.filter(pk=od["product"]["id"]).update(
                            stock=F("stock") - od["quantity"])

                except IntegrityError as ie:
                    raise serializers.ValidationError({"order_detail":
                                                       "El producto debe tener stock suficiente para registrar la orden"})

            return order

    def update(self, order: Order, validated_data):
        order_detail_data = validated_data.pop('order_detail')
        try:
            with transaction.atomic():
                order.date_time = validated_data["date_time"]
                for od_data in order_detail_data:
                    order_detail: OrderDetail = order.order_detail.get(
                        pk=od_data["id"])

                    nuevo_stock = od_data["quantity"] - order_detail.quantity

                    # hubo cambios en el stock?
                    if nuevo_stock:
                        Product.objects.filter(pk=order_detail.product_id).update(
                            stock=F("stock") - nuevo_stock)

                        # si la cantidad quedo en 0 se borra el item
                        if not od_data["quantity"]:
                            order_detail.delete()
                        else:
                            order.order_detail.filter(pk=od_data["id"]).update(
                                quantity=od_data["quantity"])

                return order
        except IntegrityError as ie:
            raise APIException(f"Error de integridad de datos ({ie.args[0]})")

    def validate_order_detail(self, order_detail_attrs):
        # no puede haber productos repetidos en la orden

        # me quedo con los ids de los productos
        id_productos = [detail["product"]["id"]
                        for detail in order_detail_attrs]

        # si hay alguno que aparezca mas de una vez hace el raise
        if max([id_productos.count(id) for id in id_productos]) > 1:
            raise serializers.ValidationError(
                "Los productos no pueden repetirse dentro de la misma orden")

        return order_detail_attrs


@permission_classes([IsAuthenticated])
class OrderViewSet(viewsets.ModelViewSet):
    """API de Ordenes """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_destroy(self, instance):
        order: Order = self.get_object()

        # devuelve el stock a los productos
        bulk_product_updates = []

        for order_detail in order.order_detail.all():
            order_detail.product.stock = F("stock") + order_detail.quantity
            bulk_product_updates.append(order_detail.product)

        Product.objects.bulk_update(bulk_product_updates, ['stock'])

        return super().perform_destroy(instance)
