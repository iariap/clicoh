# Login

```bash
access_token=$(http POST https://iariap.pythonanywhere.com/api/token/ username=admin password=admin | jq '.access' -)
access_token=${access_token//\"}
```


# productos

## Listado de productos
```bash
http https://iariap.pythonanywhere.com/api/product/ Authorization:"Bearer ${access_token}"
```

## Registrar/Editar
```bash
http POST https://iariap.pythonanywhere.com/api/product/ name="Lapicera" price=200 stock=1 Authorization:"Bearer ${access_token}"
```

## Eliminar
```bash
http DELETE https://iariap.pythonanywhere.com/api/product/2/ Authorization:"Bearer ${access_token}"
```

## Consultar un producto
```bash
http https://iariap.pythonanywhere.com/api/product/2/ Authorization:"Bearer ${access_token}"
```

## Modificar el stock
```bash
http PATCH https://iariap.pythonanywhere.com/api/product/1/ stock=26 Authorization:"Bearer ${access_token}"
```

# Crear una orden
## Con quantity mas grande que el stock
```bash
http POST https://iariap.pythonanywhere.com/api/order/ date_time="2022-06-14" order_detail:='[{"product":{"id": 1}, "quantity":2}, {"product":{"id":2}, "quantity":2000}]' Authorization:"Bearer ${access_token}"
```

## El producto se encuentra repetido en la orden
```bash
http POST https://iariap.pythonanywhere.com/api/order/ date_time="2022-06-14" order_detail:='[{"product":{"id": 1}, "quantity":2}, {"product":{"id":1}, "quantity":2}]' Authorization:"Bearer ${access_token}"
```

## Creacion OK
```bash
http POST https://iariap.pythonanywhere.com/api/order/ products:='{date_time:"2022-06-14", order_detail:[{"product_id":1, "quantity":2}, {"product_id":2, "quantity":2}]}' Authorization:"Bearer ${access_token}"
```

## Borrado de la Orden OK
```bash
http DELETE https://iariap.pythonanywhere.com/api/order/1/ Authorization:"Bearer ${access_token}"
```

# Docker
## Construir la imagen
```bash
docker build . -t backend-clickoh:latest
```
## Levantar el backend

Si la base de datos no esta creada crearla con el comando:
 ```bash
 touch db.sqlite3
```
Y luego para levantar el servicio ejecutar:

```bash
docker run -it -p 8000:8000 --mount type=bind,source=$(pwd)/db.sqlite3,target=/code/db.sqlite3 backend-clickoh:latest 
```