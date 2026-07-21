import MetaTrader5 as mt5
import os
from dotenv import load_dotenv, find_dotenv

class PlatformConnector(): # PlatformConnector() se ejecutara en cada coneccion, o sea cuando instanciemos esta clase

    def __init__(self):
        #buscamos el archivo .env y cargamos sus valores
        load_dotenv(find_dotenv())

        #inicializacion de la plataforma
        self._initialize_platform()


    def _initialize_platform(self)->None:
     if mt5.initialize( #initialize es un metodo de la api de mt5 para coneccion
            path=os.getenv("MT5_PATH"),
            login=int(os.getenv("MT5_LOGIN")),
            password=os.getenv("MT5_PASSWORD"),
            server=os.getenv("MT5_SERVER"),
            timeout=int(os.getenv("MT5_TIMEOUT")),
            portable=eval(os.getenv("MT5_PORTABLE"))):
         print("La plataforma MT5 se ha lanzado con exito")
     else:
        raise Exception(f"Ha ocurrido un error al inicializar la plataforma MT5: {mt5.last_error()}")   
        