# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from pydantic import BaseModel

class BaseRiskProps(BaseModel):
    pass # esto quiere decir que no tiene ningun atributo, es una clase base que sirve como plantilla para otras clases de propiedades de riesgo. 
#Al heredar de BaseModel, las clases derivadas pueden aprovechar las funcionalidades de validación y serialización que ofrece Pydantic, lo que facilita la gestión de datos y la configuración de propiedades de riesgo en el framework de trading.

class MaxLeverageFactorRiskProps(BaseRiskProps):
    """
    Risk properties for managing maximum leverage factor.
    """

    max_leverage_factor: float #este es un atributo que representa el factor de apalancamiento máximo permitido por el broker. Es un valor flotante que indica cuántas veces se puede multiplicar el capital disponible para abrir posiciones en el mercado. Por ejemplo, si el max_leverage_factor es 100, significa que se puede operar con hasta 100 veces el capital disponible en la cuenta. Este valor es importante para gestionar el riesgo y evitar sobreapalancamiento en las operaciones de trading.