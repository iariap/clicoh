# Login

```bash
http POST http://localhost:8000/api/token/ username=admin password=admin
```

# producto

## Listado de productos
```bash
http http://127.0.0.1:8000/api/product/ Authorization:"Bearer XXX"
```

## Registrar/Editar
```bash
http POST http://127.0.0.1:8000/api/product/ name="Lapicera" price=200 stock=1 Authorization:"Bearer XXX"
```

## Eliminar
```bash
http DELETE http://127.0.0.1:8000/api/product/2/ Authorization:"Bearer XXX"
```

## Consultar un producto
```bash
http http://127.0.0.1:8000/api/product/2/ Authorization:"Bearer XXX"
```

## Modificar el stock
```bash
http PATCH http://127.0.0.1:8000/api/product/1/ stock=26 Authorization:"Bearer XXX"
```

# Crear una orden
## Con quantity mas grande que el stock
```bash
http POST http://localhost:8000/api/order/ products:='[{"product_id":1, "quantity":20}]'
```

## El producto se encuentra repetido en la orden
```bash
http POST http://localhost:8000/order/place_order/ products:='[{"product_id":1, "quantity":2}, {"product_id":1, "quantity":2}]'
```

## Creacion OK
```bash
http POST http://localhost:8000/order/place_order/ products:='[{"product_id":1, "quantity":2}, {"product_id":2, "quantity":2}]'
```