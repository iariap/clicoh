from django.db import IntegrityError, transaction
from django.db.models import F
from requests import delete
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderDetail, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'price', 'stock', 'name')


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderDetail
        fields = ('id', 'quantity', 'product')


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.FloatField(source='get_total', read_only=True)
    total_usd = serializers.FloatField(source='get_total_usd', read_only=True)
    order_detail = serializers.ListSerializer(child=OrderDetailSerializer())

    class Meta:
        model = Order
        fields = ('id', 'date_time', 'total', 'total_usd', 'order_detail')


class ProductStockSerializer(serializers.Serializer):
    stock = serializers.IntegerField(min_value=0)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['POST'], name='Change Stock', serializer_class=ProductStockSerializer)
    def stock(self, request, pk=None):
        """Update the product's stock."""
        product = self.get_object()
        serializer = ProductStockSerializer(data=request.data)
        if serializer.is_valid():
            product.stock = serializer.validated_data['stock']
            product.save()
            return Response({'status': 'stock set'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class OrderCreationProductsSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()
    # que la cantidad de cada producto sea mayor a 0
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        product = Product.objects.get(pk=attrs["product_id"])
        if product.stock < attrs["quantity"]:
            raise serializers.ValidationError(
                f"La cantidad de {attrs['quantity']} {product.name} solicitada supera el stock de {product.stock} unidades disponibles")
        return attrs


class OrderCreationSerializer(serializers.Serializer):

    products = serializers.ListField(
        child=OrderCreationProductsSerializer(), min_length=1)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                order = Order()
                order.save()
                for product_to_place in validated_data["products"]:

                    # actualiza el stock
                    Product.objects.filter(pk=product_to_place["product_id"]).update(
                        stock=F("stock") - product_to_place["quantity"])

                    # genera el detalle para el producto
                    OrderDetail(
                        order=order, product_id=product_to_place["product_id"], quantity=product_to_place["quantity"]).save()

                return order
        except IntegrityError as ie:
            raise serializers.ValidationError(
                "El producto se encuentra mas de una vez para la orden")


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        ...

    @action(detail=False, methods=['POST'], name='Place an order', serializer_class=OrderCreationSerializer)
    def place_order(self, request):
        serializer = OrderCreationSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(OrderSerializer(instance).data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()

        # devuelve el stock a los productos
        for order_detail in order.order_detail.all():
            Product.objects.filter(pk=order_detail.product_id).update(
                stock=F("stock") + order_detail.quantity)

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # * Editar una orden (inclusive sus detalles). Debe actualizar el stock del producto
        # TODO FALTA SEGUIR CON ESTE
        return super().update(request, *args, **kwargs)


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
