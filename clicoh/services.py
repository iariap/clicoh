# services goes here
import requests
from functools import cache


class DolarService():

    @cache
    def cotizacion():
        casas = requests.get(
            "https://www.dolarsi.com/api/api.php?type=valoresprincipales").json()

        cotizacion = 0

        for casa in casas:
            if casa["casa"]["nombre"] == "Dolar Blue":
                cotizacion = casa["casa"]["venta"]
                break

        return float(cotizacion.replace(",", "."))
