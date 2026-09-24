# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import RiskPctSizingProps
import MetaTrader5 as mt5

class RiskPctPositionSizer(IPositionSizer):

    def __init__(self, properties: RiskPctSizingProps):
        
        self.risk_pct = properties.risk_pct

    def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
       
        # Revisar que el riesgo sea positivo
        if self.risk_pct <= 0.0:
            print(f"- ERROR (RiskPctPositionSizer): El porcentaje de riesgo introducido: {self.risk_pct} no es válido.")
            return 0.0

        # Revisar que el sl != 0, o sea tiene q existir un stop loss.
        if signal_event.sl <= 0.0:
            print(f"- ERROR (RiskPctPositionSizer): El valor del SL: {signal_event.sl} no es válido.")
            return 0.0
        
        # Acceder a la información de la cuenta (para obtener divisa de la cuenta)
        account_info = mt5.account_info()
        
        # Acceder a la información del símbolo (para poder calcular el riesgo)
        symbol_info = mt5.symbol_info(signal_event.symbol)

        
        # Recuperamos el precio de entrada:
        # Si es una orden a mercado
        if signal_event.target_order == "MARKET":
            # Obtener el último precio disponible en el mercado (ask o bid)
            last_tick = data_provider.get_latest_tick(signal_event.symbol)
            entry_price = last_tick['ask'] if signal_event.signal == "BUY" else last_tick['bid'] #que acceda a la clave del diccionario 'ask' si hay una señal de compra; si no hay una señal de compra q acceda a la clave 'bid'
        
        # Si es una orden pendiente ( no "MARKET", sino limit o stop)
        else:
            # Cogemos el precio del propio signal event
            entry_price = signal_event.target_price

        # Conseguimos los valores que nos faltan para los cálculos
        equity = account_info.equity #dijo q se puede calcular con el balance tambien, pero el equity es mejor porque tiene en cuenta las posiciones abiertas y el balance no. El equity es el valor total de la cuenta, incluyendo el balance y las ganancias o pérdidas no realizadas de las posiciones abiertas.
        volume_step = symbol_info.volume_step               # Cambio mínimo de volumen. Por ejemplo, si el volume step es 0.01, significa que podemos abrir posiciones de 0.01 lotes, 0.02 lotes, 0.03 lotes, etc., pero no podemos abrir posiciones de 0.015 lotes o 0.025 lotes.
        tick_size = symbol_info.trade_tick_size             # Cambio mínimo de precio, que es lo mismo q el tamaño del tick, es decir, la mínima variación de precio que tiene un símbolo en el mercado para justamente generar un nuevo tick. Por ejemplo, si el tick size es 0.0001, significa que el precio del símbolo puede variar en incrementos de 0.0001 unidades de su divisa base.
        account_ccy = account_info.currency                 # divisa de la cuenta
        #Esto me lo dijo gemini: DIVISABASE/DIVISACOTIZADA (o sea EUR/USD que es lo mismo que EURUSD). DIVISABASE = ACTIVO QUE ESTAS COMPRANDO O VENDIENDO. DIVISACOTIZADA = LA MONEDA CON LA QUE PAGAS O COBRAS (LLAMADA TAMBIEN DIVISA DE PROFIT EN EL CURSO)
        symbol_profit_ccy = symbol_info.currency_profit     # divisa del profit del símbolo. Por ejemplo, si estamos operando con el símbolo EURUSD, la divisa de profit es USD, porque las ganancias o pérdidas se calculan en dólares estadounidenses. Si estamos operando con el símbolo USDJPY, la divisa de profit es JPY, porque las ganancias o pérdidas se calculan en yenes japoneses.
        contract_size = symbol_info.trade_contract_size     # tamaño del contrato (ej 1 lote estándar valdra 100.000 unidades de la divisa base del símbolo, es decir, si estamos operando con el símbolo EURUSD, 1 lote estándar valdrá 100.000 euros; si estamos operando con el símbolo USDJPY, 1 lote estándar valdrá 90.000 dólares estadounidenses por ejemplo). Esto es importante porque el tamaño del contrato afecta directamente al valor del tick y al riesgo monetario de la operación. Para cada divisa el contract_size es diferente.
        

        # Cálculos auxiliares
        tick_value_profit_ccy = contract_size * tick_size              # Cantidad ganada o perdida por cada lote y por cada tick

        # Convertick el tick value en profit ccy del symbol a la divisa de nuestra cuenta. Para el caso de EURUSD, la divisa de profit es USD. Para el caso de USDEUR la divisa de profit es EUR y la divisa de nuestra cuenta sera por ejemplo CLP  
        # tick_value_account_ccy = Utils.convert_currency_amount_to_another_currency(tick_value_profit_ccy, symbol_profit_ccy, account_ccy)
        tick_value_account_ccy= 5
        
        # Cálculo del tamaño de la posición
        try:
             #El valor absoluto es por si por ejemplo el precio de entrada es 1.1000 y el SL es 1.1050, o sea que la distancia es negativa para una venta, pero lo que nos interesa es la distancia en ticks, no el signo de la distancia.
             # Se divide por el tamaño del tick para obtener la distancia en ticks, y se convierte a entero porque no podemos tener fracciones de ticks.
            price_distance_in_integer_ticksizes = int(abs(entry_price - signal_event.sl) / tick_size) # por ejemplo con entry_price=1.10, sl=1.00, tick_size=0.01 tendremos como resultado 10.0 q con el int() se convierte en 10, que es la distancia en ticks entre el precio de entrada y el stop loss. Esto es importante porque el tamaño de la posición se calcula en función del riesgo monetario que estamos dispuestos a asumir, y ese riesgo se determina por la distancia entre el precio de entrada y el stop loss en ticks.
            monetary_risk = equity * self.risk_pct #o sea el equity por el porcentaje de riesgo que nosotros hemos definido.
            volume = monetary_risk / (price_distance_in_integer_ticksizes * tick_value_account_ccy) # aqui monetary_risk està en el currency de mi cuenta. Esto representa lo que estoy dispuesto a arriesgar en cada tick para esa operacion
            volume = round(volume / volume_step) * volume_step #Resulta q hay q respetar el volume step. La funcion round redondea a dos decimales, por ejemplo 5.76543 a 5.77
        
        except Exception as e:
            print(f"- ERROR: Problema al calcular el tamaño de la posición en función del riesgo. Excepción: {e}")
            return 0.0

        else:
            return volume