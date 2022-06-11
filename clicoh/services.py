# services goes here
import requests
from functools import cache


class DolarService():

    @cache
    def cotizacion():
        cotizacion = "0"        
        try:
            casas = requests.get(
                "https://www.dolarsi.com/api/api.php?type=valoresprincipales").json()

            for casa in casas:
                if casa["casa"]["nombre"] == "Dolar Blue":
                    cotizacion = casa["casa"]["venta"]
                    break
        except:
            pass

        return float(cotizacion.replace(",", "."))
