# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from platform_connector.platform_connector import PlatformConnector



if __name__ == "__main__":
        # Definición de variables necesarias para la estrategia
    symbols = ['EURUSD', 'USDJPY', 'GBPUSD', 'USDCLP'] #un simbolo en mt5 es un par de divisas, por ejemplo EURUSD, USDJPY, GBPUSD, USDCLP del MarketWatch (la ventana q se ve en la plataforma de mt5 donde estan todos los simbolos que podemos tradear y q se activa con ctrl +M)
    CONNECT = PlatformConnector(symbol_list=symbols)
   