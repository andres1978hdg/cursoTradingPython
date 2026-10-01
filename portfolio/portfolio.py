import MetaTrader5 as mt5
from typing import Dict

class Portfolio(): #un portafolio es la coleccion total de activos financieros (acciones forex, cripto,oro), posiciones abiertas (por ejemplo estoy comprando/vendiendo acciones de fender, ethereum y orex) y estrategias que tiene un trader (o sea yo) en un momento determinado

    def __init__(self, magic_number: int):
        """
        Initializes a new instance of the Portfolio class.

        Args:
            magic_number (int): The magic number associated with the portfolio.
        """
        self.magic = magic_number

    def get_open_positions(self) -> tuple: # devuelve una tupla de objetos de posiciones abiertas
        """
        Retrieves the open positions from the MetaTrader 5 platform.

        Returns:
            tuple: A tuple containing the open positions.
        """
        return mt5.positions_get()

    # el magic number es un numero que yo mismo le asigno al bot de peppersone para q mt5 sepa que operaciones tienen el mismo algoritmo especìfico. 
    # por ejemplo si ethereum, acciones de fender y acciones de gibson tienen un magic number=1001 significa que se rigen por la misma estrategia de trading. Si el dia de mañana
    # asigno magic number =1002 a ethereum, entonces tendrè dos operaciones con dos estrategias de trading distintas al mismo tiempo, lo que es vàlido. 
    def get_strategy_open_positions(self) -> tuple:
        """
        Retrieves the open positions for the strategy.

        Returns:
            tuple: A tuple containing the open positions for the strategy.
        """
        positions = []
        for position in mt5.positions_get():
            if position.magic == self.magic:
                positions.append(position)
        
        return tuple(positions)

    def get_number_of_open_positions_by_symbol(self, symbol: str) -> Dict[str, int]:
        """
        Get the number of open positions for a given symbol.

        Args:
            symbol (str): The symbol for which to retrieve the open positions.

        Returns:
            Dict[str, int]: A dictionary containing the count of long positions, short positions, and total positions.

        """
        longs = 0
        shorts = 0
        for position in mt5.positions_get(symbol=symbol):
            if position.type == mt5.ORDER_TYPE_BUY: #para cada open position, por cada operacion de compra para ese simbolo en particular sumamos uno al contador
                longs += 1
            else: #para cada open position, por cada operacion de venta para ese simbolo en particular sumamos uno al contador
                shorts += 1
        
        return {"LONG": longs, "SHORT": shorts, "TOTAL": longs + shorts}

    def get_number_of_strategy_open_positions_by_symbol(self, symbol: str) -> Dict[str, int]:
        """
        Get the number of open positions for a given symbol in the strategy's portfolio.

        Args:
            symbol (str): The symbol for which to count the open positions.

        Returns:
            Dict[str, int]: A dictionary containing the count of long positions, short positions, and the total count.

        """
        longs = 0
        shorts = 0

        for position in mt5.positions_get(symbol=symbol):
            if position.magic == self.magic:
                if position.type == mt5.ORDER_TYPE_BUY:
                    longs += 1
                else:
                    shorts += 1
        
        return {"LONG": longs, "SHORT": shorts, "TOTAL": longs + shorts}