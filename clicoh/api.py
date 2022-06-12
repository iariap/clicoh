from requests import delete
from rest_framework import viewsets, serializers, status
from .models import Order, OrderDetail, Product
from django.db.models import F
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(min_value=0)
    stock = serializers.IntegerField(min_value=0)

    class Meta:
        model = Product
        fields = ('id', 'price', 'stock', 'name',)


class ProductViewSet(viewsets.ModelViewSet):
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
        try:
            order_detail_data = validated_data.pop('order_detail')
            with transaction.atomic():
                order = Order.objects.create(**validated_data)
                for od in order_detail_data:
                    order.order_detail.create(
                        quantity=od["quantity"],
                        product_id=od["product"]["id"]
                    )
                    # actualiza el stock del producto
                    Product.objects.filter(pk=od["product"]["id"]).update(
                        stock=F("stock") - od["quantity"])
                return order
        except IntegrityError as ie:
            raise serializers.ValidationError(
                "El producto se encuentra mas de una vez para la orden", code=500)

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

                return order
        except IntegrityError as ie:
            raise APIException(f"Error de integridad de datos ({ie.args[0]})")


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)