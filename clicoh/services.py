# services goes here
import requests
from functools import cache


class DolarService():

    @cache
    def get_cotizacion():
        # https://www.dolarsi.com/api/api.php?type=valoresprincipales
        casas = requests.get(
            "https://www.dolarsi.com/api/api.php?type=valoresprincipales").json()

        cotizacion = 0

        for casa in casas:
            if casa["casa"]["nombre"] == "Dolar Blue":
                cotizacion = casa["casa"]["venta"].replace(",", ".")
                break

        return float(cotizacion)
