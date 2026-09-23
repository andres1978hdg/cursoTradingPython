# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from pydantic import BaseModel

class BaseSizerProps(BaseModel):
    pass 

class MinSizingProps(BaseSizerProps):
    pass # no se necesitan propiedades para este Position Sizer pq el volumen viene del broker, no del codigo.

class FixedSizingProps(BaseSizerProps):
    """
    Represents the properties for fixed sizing of positions.

    Attributo:
        volume (float): The fixed volume for each position.
    """
    volume: float # volume en java es una variable, pero no una variable de instancia, es decir, no es un atributo de la clase, sino una variable local que se utiliza para inicializar el atributo self.volume. En este caso, volume es un parámetro del constructor de la clase FixedSizingProps y se utiliza para establecer el valor del atributo self.volume que representa el volumen fijo para cada posición.

class RiskPctSizingProps(BaseSizerProps):
    """
    Properties for risk percentage position sizing.

    Attributes:
        risk_pct (float): The risk percentage for position sizing.
    """
    risk_pct: float