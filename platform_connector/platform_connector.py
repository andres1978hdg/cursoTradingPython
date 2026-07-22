import MetaTrader5 as mt5
#from utils.utils import Utils
import os
from dotenv import load_dotenv, find_dotenv

class PlatformConnector(): # PlatformConnector() se ejecutara en cada coneccion, o sea cuando instanciemos esta clase

     def __init__(self, symbol_list: list): #recibimos una lista de simbolos que queremos añadir al MarketWatch desde trading_app.p
        #buscamos el archivo .env y cargamos sus valores
        load_dotenv(find_dotenv())

        #inicializacion de la plataforma
        self._initialize_platform()

        # Comprobación del tipo de cuenta
        self._live_account_warning()

        # Comprobación del trading algorítmico
        self._check_algo_trading_enabled()

          # Añadimos los símbolos al MarketWatch
        self._add_symbols_to_marketwatch(symbol_list)


     def _initialize_platform(self) -> None:
         if mt5.initialize(  # initialize es un metodo de la api de mt5 para coneccion
                 path=os.getenv("MT5_PATH"),
                 login=int(os.getenv("MT5_LOGIN")),
                 password=os.getenv("MT5_PASSWORD"),
                 server=os.getenv("MT5_SERVER"),
                 timeout=int(os.getenv("MT5_TIMEOUT")),
                 portable=eval(os.getenv("MT5_PORTABLE"))):
             print("La plataforma MT5 se ha lanzado con exito")
         else:
             raise Exception(f"Ha ocurrido un error al inicializar la plataforma MT5: {mt5.last_error()}")

     def _live_account_warning(self) -> None:
        """
        Displays a warning message if a real trading account is detected.
        Prompts the user to confirm if they want to continue.
        If the user chooses not to continue, the program is shut down.
        """
        # Recuperamos el objeto de tipo AccountInfo
        account_info = mt5.account_info()
        
        # Comprobar el tipo de cuenta que se ha lanzado
        if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
            print("Cuenta de tipo DEMO detectada.")
        
        elif account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_REAL:
            if not input("ALERTA! Cuenta de tipo REAL detectada. Capital en riesgo. ¿Deseas continuar? (y/n): ").lower() == "y":
                mt5.shutdown()
                raise Exception("Usuario ha decidido DETENER el programa.")
        else:
            print("Cuenta de tipo CONCURSO detectada.")

     def _check_algo_trading_enabled(self) -> None:
        """
        Checks if algorithmic trading is enabled.

        Raises:
            Exception: If algorithmic trading is disabled.
        """
        # Vamos a comprobar que el trading algorítmico está activado
        if not mt5.terminal_info().trade_allowed:
            raise Exception("El trading algorítmico está desactivado. Por favor, actívalo MANUALMENTE desde la configuración del terminal MT5.") #Esto se hace desde herramientas-->opciones-->asesores expertos-->chequear "permitir e comercio algoritmico"

     def _add_symbols_to_marketwatch(self, symbols: list) -> None:
            """
            Adds symbols to the MarketWatch if they are not already visible.
    
            Args:
                symbols (list): List of symbols to be added.
    
            Returns:
                None
            """
            # 1) Comprobamos si el símbolo ya está visible en el MW
            # 2) Si no lo está, lo añadiremos

            for symbol in symbols:
                        if mt5.symbol_info(symbol) is None:
                            print(f"No se ha podido añadir el símbolo {symbol} al MarketWatch: {mt5.last_error()}")
                            continue
                        
                        if not mt5.symbol_info(symbol).visible:
                            if not mt5.symbol_select(symbol, True):
                                print(f"No se ha podido añadir el símbolo {symbol} al MarketWatch: {mt5.last_error()}")
                            else:
                                print(f"Símbolo {symbol} se ha añadido con éxito al MarketWatch!")
                        else:
                            print(f"El símbolo {symbol} ya estaba en el MarketWatch.")
    