from enum import Enum
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

# Definición de los distintos tipos de eventos
class EventType(str, Enum):
    """
    Enumeration class representing different types of events.
    
    Attributes:
        DATA: Represents a data event.
        SIGNAL: Represents a signal event.
        SIZING: Represents a sizing event.
        ORDER: Represents an order event.
        EXECUTION: Represents an execution event.
        PENDING: Represents a pending event.
    """
    DATA = "DATA"
    SIGNAL = "SIGNAL"
    SIZING = "SIZING"
    ORDER = "ORDER"
    EXECUTION = "EXECUTION"
    PENDING = "PENDING"

    """
    BaseModel es el bloque de construcción fundamental de Pydantic, diseñado para definir esquemas de datos que realizan validación, conversión y serialización automática en tiempo de ejecución utilizando las anotaciones de tipos (type hints) de Python.

Características principales
Validación en tiempo de ejecución: Al instanciar una clase que hereda de BaseModel, Pydantic comprueba de inmediato que los datos coincidan estrictamente con los tipos declarados. Si hay una discrepancia que no puede resolverse, lanza un error detallado del tipo ValidationError.

Coerción de tipos: Si pasas un valor de un formato compatible (por ejemplo, el texto "42" a un campo definido como int), Pydantic lo convierte automáticamente al tipo correcto sin interrumpir el flujo.

Serialización nativa: Facilita la exportación de los datos estructurados a diccionarios o estructuras JSON mediante métodos integrados como model_dump() y model_dump_json().

Soporte para valores por defecto y opcionales: Permite establecer campos obligatorios, campos con valores predeterminados fijos o campos opcionales que aceptan valores nulos (None).

Ejemplo básico
Python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool = True

# Instanciación correcta (incluso convierte el string "99.99" a float)
item = Product(name="Teclado", price="99.99")
print(item.price)  # 99.99 (es un float)
print(item.model_dump())  # {'name': 'Teclado', 'price': 99.99, 'in_stock': True}
    """

class BaseEvent(BaseModel):
    """
    Base class for all events.
    """
    event_type: EventType #O sea, ya que estamos usando BaseModel de pydantic, en tiempo de ejecucion va a validar que el tipo de evento sea uno de los definidos en EventType

    class Config:
        """
        Configuration class for Pydantic BaseModel.
        """
        arbitrary_types_allowed = True  # Esto permite que se puedan usar tipos arbitrarios en los modelos de Pydantic, como por ejemplo pd.Series, que no es un tipo nativo de Python.

class DataEvent(BaseEvent):
    """
    Represents an event that contains data for a specific symbol.

    Attributes:
        event_type (EventType): The type of the event (always EventType.DATA).
        symbol (str): The symbol associated with the data.
        data (pd.Series): The data associated with the event.
    """
    event_type: EventType = EventType.DATA #esto es fijo
    symbol: str #esto se define al instanciar la clase, es decir, cuando creemos un DataEvent, le pasaremos el simbolo
    data: pd.Series #esto se define al instanciar la clase, es decir, cuando creemos un DataEvent, le pasaremos la serie de datos (una fila del dataframe de velas)