import MetaTrader5 as mt5
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Crear un método estático para poder convertir una divisa a otra
class Utils():

    def __init__(self):
        """
        Initializes the object.
        """
        pass

    #En este metodo usemos como ejemplo el par EURJPY, donde EUR es la divisa cotizada y JPY es la divisa base. Los precios de FX estabecen q de momento 1 EUR (base) equivalen a 160 JPY (cotizada). En caso chileno para USDCLP seria 1 USD (base) equivalen a 950 CLP (cotizada).
    # Creamos nuestro método estático con el decorador @staticmethod
    @staticmethod
    def convert_currency_amount_to_another_currency(amount: float, from_ccy: str, to_ccy: str) -> float:
        # Comprobamos si ambas divisas para la conversión son las mismas
        if from_ccy == to_ccy:
            return amount

        # all_fx_symbol es un tuple
        all_fx_symbol = ("AUDCAD", "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD", "CADCHF", "CADJPY", "CHFJPY", "EURAUD", "EURCAD", #ojo, que hay q cerciorarse q el broker provea estos pares (en nuestro caso pepperstone)
                        "EURCHF", "EURGBP", "EURJPY", "EURNZD", "EURUSD", "GBPAUD", "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD",
                        "GBPUSD", "NZDCAD", "NZDCHF", "NZDJPY", "NZDUSD", "USDCAD", "USDCHF", "USDJPY", "USDSEK", "USDNOK")
        
        # Convertir las divisas a mayúsculas
        from_ccy = from_ccy.upper()
        to_ccy = to_ccy.upper()

        # Buscamos el símbolo que relaciona nuestra divisa origen con nuestra divisa destino (list comprehension)
        fx_symbol = [symbol for symbol in all_fx_symbol if from_ccy in symbol and to_ccy in symbol][0] #aca buscamos las 6 letras de la lista de arriba
        fx_symbol_base = fx_symbol[:3] #las 3 primeras letras del par es la divisa base

        # Recuperamos los últimos datos disponibles del fx_symbol
        try:
            tick = mt5.symbol_info_tick(fx_symbol)
            if tick is None:
                raise Exception(f"El símbolo {fx_symbol} no está disponible en la plataforma MT5. Por favor, revísa los símbolos disponibles de tu broker.")

        except Exception as e:
            print(f"ERROR: No se pudo recuperar el último tick del símbolo {fx_symbol}. MT5 error: {mt5.last_error()}, Exception: {e}")
            return 0.0 #esto es simplemente para cumplir con devolver un float
        
        else:
            # Recuperamos el último precio disponible del símbolo
            last_price = tick.bid #160 en el ejempo de linea 14

            # Convertimos la cantidad de la divisa origen a la divisa destino
            converted_amount = amount / last_price if fx_symbol_base == to_ccy else amount * last_price # usando el ejemplo de EURJPY, el primer caso (o sea fx_symbol_base == to_ccy) es para convertir de la divisa cotizada (o sea JPY) a la divisa base (o sea EUR). El segundo caso (o sea el else) es para pasar de la divisa base  (o sea EUR) a la  divisa cotizada (o sea JPY). 
            # 1 EUR --> 160 JPY ; 10 amount EUR -->X converted_amount JPY, o sea este serìa el caso del else de la linea anterior.
            return converted_amount

    @staticmethod
    def dateprint() -> str:
        """
        Returns the current date and time in the format "dd/mm/yyyy HH:MM:SS.sss".
        The timezone used is "Asia/Nicosia".
        """
        return datetime.now(ZoneInfo("Asia/Nicosia")).strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]



