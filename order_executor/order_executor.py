# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from portfolio.portfolio import Portfolio
from events.events import OrderEvent, ExecutionEvent, PlacedPendingOrderEvent, SignalType
from utils.utils import Utils
import pandas as pd
from queue import Queue 
import MetaTrader5 as mt5
import time
from datetime import datetime

class OrderExecutor():

    def __init__(self, events_queue: Queue, portfolio: Portfolio) -> None:
        """
        Initialize the OrderExecutor object.

        Args:
            events_queue (Queue): The queue to receive events from.
            portfolio (Portfolio): The portfolio object to execute orders on.
        """
        self.events_queue = events_queue
        self.PORTFOLIO = portfolio

    def execute_order(self, order_event: OrderEvent) -> None:
        """
        Executes the given order event.

        Args:
            order_event (OrderEvent): The order event to be executed.

        Returns:
            None
        """

        # Evaluamos el tipo de orden que se quiere ejecutar, y llamamos al método adecuado
        if order_event.target_order == "MARKET": # esto esta en class OrderType en events.py
            # Llamamos al método que ejecuta órdenes a mercado
            self._execute_market_order(order_event) 
        else:
            # Llamamos al método que coloque órdenes pendientes.  Esto es "LIMIT" o "STOP" de class OrderType en events.py
            self._send_pending_order(order_event)

    def _execute_market_order(self, order_event: OrderEvent) -> None: # este metodo recibe un OrderEvent para saber si es de compra o de venta, y el simbolo, y el volumen, y el sl y tp, y el magic number. Y luego ejecuta la orden a mercado usando mt5.order_send()
        """
        Executes a market order based on the given order event.

        Args:
            order_event (OrderEvent): The order event containing the details of the market order.

        Raises:
            Exception: If the order event signal is not valid.

        Returns:
            None
        """
        # Comprobamos si la orden es de compra o de venta
        if order_event.signal == "BUY":
            # Orden de compra
            order_type = mt5.ORDER_TYPE_BUY
        elif order_event.signal == "SELL":
            # Orden de venta
            order_type = mt5.ORDER_TYPE_SELL
        else:
            raise Exception(f"ORD EXEC: La señal {order_event.signal} no es válida")

        # Creación del market order request
        market_order_request = { 
            "action": mt5.TRADE_ACTION_DEAL, # Esto es para colocar una orden de mercado.
            "symbol": order_event.symbol, # Esto es el símbolo del instrumento financiero (por ejemplo, EURUSD) para el que se está ejecutando la orden.
            "volume": order_event.volume,  # Esto es el volumen de la orden, es decir, la cantidad de lotes que se van a comprar o vender.
            'price': mt5.symbol_info(order_event.symbol).bid,  # Esto es
            "sl": order_event.sl, # Esto es el nivel de stop loss para la orden, es decir, el precio al que se cerrará automáticamente la posición si el mercado se mueve en contra de la operación.
            "tp": order_event.tp, # Esto es el nivel de take profit para la orden, es decir, el precio al que se cerrará automáticamente la posición si el mercado se mueve a favor de la operación.        
            "type": order_type, # Esto es el tipo de orden, que puede ser de compra (BUY) o de venta (SELL) y q viene de mt5 en de las lineas de mas arriba
            "deviation": 0, # Esto es la desviación máxima permitida en puntos para la ejecución de la orden. Si el precio de mercado se mueve más allá de esta desviación, la orden no se ejecutará. Esmconstante en nuestro caso.
            "magic": order_event.magic_number, # Identificador único para la orden, que se utiliza para diferenciar entre distintas estrategias o sistemas de trading que puedan estar operando simultáneamente en la misma cuenta.
            "comment": "FWK Market Order", # Esto es un comentario que se puede asociar a la orden para proporcionar información adicional o contexto sobre la operación.
            "type_filling": mt5.ORDER_FILLING_FOK, # Esto es el tipo de llenado de la orden, que indica cómo se debe ejecutar la orden en términos de cantidad y precio. En este caso, FOK (Fill or Kill) significa que la orden debe ejecutarse completamente al precio especificado o no ejecutarse en absoluto.
        }

        # Mandamos el trade request para ser ejecutado
        result = mt5.order_send(market_order_request)

        # Verificar el resultado de la ejecución de la orden
        if self._check_execution_status(result):
            print(f"Market Order {order_event.signal} para {order_event.symbol} de {order_event.volume} lotes ejecutada correctamente")
            # Generar el execution event y añadirlo a la cola
            self._create_and_put_execution_event(result)
        else:
            #Mandaremos un mensaje de error
            print(f"Ha habido un error al ejecutar la Market Order {order_event.signal} para {order_event.symbol}: {result.comment}")

    def _send_pending_order(self, order_event: OrderEvent) -> None: # este metodo recibe un OrderEvent para saber si es de compra o de venta, y el simbolo, y el volumen, y el sl y tp, y el magic number. Y luego ejecuta la orden pendiente usando mt5.order_send()
        """
        Sends a pending order based on the given order event.

        Args:
            order_event (OrderEvent): The order event containing the details of the pending order.

        Raises:
            Exception: If the target order of the order event is not valid.

        Returns:
            None
        """
        # Comprobar si es de tipo STOP o de tipo LIMITE
        if order_event.target_order == "STOP":
            order_type = mt5.ORDER_TYPE_BUY_STOP if order_event.signal == "BUY" else mt5.ORDER_TYPE_SELL_STOP #el else es para order_event.signal == "SELL" obviamente
        elif order_event.target_order == "LIMIT":
            order_type = mt5.ORDER_TYPE_BUY_LIMIT if order_event.signal == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT #el else es para order_event.signal == "SELL" obviamente
        else:
            raise Exception(f"ORD EXEC: La orden pendiente objetivo {order_event.target_order} no es válida")
        
        # Creación de la pending order request
        pending_order_request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": order_event.symbol,
            "volume": order_event.volume,
            "sl": order_event.sl,
            "tp": order_event.tp,
            "type": order_type, # Esto es el tipo de orden pendiente, que puede ser de compra (BUY) o de venta (SELL) y que depende del tipo de orden objetivo (STOP o LIMIT) y de la señal (BUY o SELL).
            "price": order_event.target_price, # Notar q a diferencia de Market Order aca sì hay price. Esto es el precio al que se colocará la orden pendiente. Para órdenes LIMIT, este será el precio límite al que se ejecutará la orden, mientras que para órdenes STOP, este será el precio de activación de la orden.
            "deviation": 0,
            "magic": order_event.magic_number,
            "comment": "FWK Pnding Order",
            "type_filling": mt5.ORDER_FILLING_FOK, # Esto es el tipo de llenado de la orden pendiente, que indica cómo se debe ejecutar la orden en términos de cantidad y precio. En este caso, FOK (Fill or Kill) significa que la orden debe ejecutarse completamente al precio especificado o no ejecutarse en absoluto.
            "type_time": mt5.ORDER_TIME_GTC
        }

        # Mandamos el trade request para colocar la orden pendiente
        result = mt5.order_send(pending_order_request)

        # Verificar el resultado de la ejecución de la orden
        if self._check_execution_status(result):
            print(f" Pending Order {order_event.signal} {order_event.target_order} para {order_event.symbol} de {order_event.volume} lotes colocada en {order_event.target_price} correctamente")
            # Generamos y colocamos el evento específico de colocación de órdenes pendientes a la cola
            self._create_and_put_placed_pending_order_event(order_event)
        else:
            #Mandaremos un mensaje de error
            print(f" Ha habido un error al colocar la orden pendiente {order_event.signal} {order_event.target_order} para {order_event.symbol}: {result.comment}")

    # Como obtuvo el ticket cuando probò? -> lo mismo del  comentario del metodo close_position_by_ticket
    def cancel_pending_order_by_ticket(self, ticket: int) -> None:
        """
        Cancels a pending order by its ticket number.

        Args:
            ticket (int): The ticket number of the pending order to be cancelled.

        Returns:
            None
        """
        # Accedemos a la orden pendiente de interés
        order = mt5.orders_get(ticket=ticket)[0]

        # Verificamos que la orden exista
        if order is None:
            print(f" ORD EXEC: No existe ninguna orden pendiente con el ticket {ticket}")
            return
        
        # Creamos el trade request para cancelar la orden pendiente
        cancel_request = {
            'action': mt5.TRADE_ACTION_REMOVE,
            'order': order.ticket,
            'symbol': order.symbol
        }

        # mandamos el cancel request
        result = mt5.order_send(cancel_request)

        # Verificar el resultado de la cancelación de la orden
        if self._check_execution_status(result):
            print(f"{Utils.dateprint()} - Orden pendiente con ticket {ticket} en {order.symbol} y volumen {order.volume_initial} se ha cancelado correctamente")
        else:
            # Mandaremos un mensaje de error
            print(f"{Utils.dateprint()} - Ha habido un error al cancelar la orden {ticket} en {order.symbol} con volumen {order.volume_initial}: {result.comment}")

    # Como obtuvo el ticket cuando probò? -> en un archivo .ipynb manda un dict close_request (esta aqui abajo) y uno de los campos que obtiene de esa llamada es el ticket .
    # Intuyo q cuando ya pruebe desde la plataforma misma la obtencion del ticket sera automatica
    def close_position_by_ticket(self, ticket: int) -> None:
        """
        Closes a position by ticket number.

        Args:
            ticket (int): The ticket number of the position to be closed.

        Returns:
            None
        """
        # Accedemos a la posición (abierta) de interés
        position = mt5.positions_get(ticket=ticket)[0]

        # Verificamos que la posición exista
        if position is None:
            print(f"ORD EXEC: No existe ninguna posición con el ticket {ticket}")
            return
        
        # Creamos el trade request para cerrar dicha posición.
        close_request = { # close_request es un objeto de tipo dict.
            'action': mt5.TRADE_ACTION_DEAL, # Esto es para cerrar la posición, ya que estamos haciendo un trade de tipo DEAL (ejecución de mercado). El  mt5.TRADE_ACTION_DEAL es una constante tipo 1 o 2 o 3, etc q define el tipo de acción. En este caso es 1. Otras acciones posibles son TRADE_ACTION_PENDING (para colocar una orden pendiente) y TRADE_ACTION_REMOVE (para cancelar una orden pendiente).
            'position': position.ticket,
            'symbol': position.symbol,
            'volume': position.volume,
            'price': mt5.symbol_info(position.symbol).bid,
            'type': mt5.ORDER_TYPE_BUY if position.type == mt5.ORDER_TYPE_SELL else mt5.ORDER_TYPE_SELL,
            'type_filling': mt5.ORDER_FILLING_FOK # Esto es el tipo de llenado de la orden, que indica cómo se debe ejecutar la orden en términos de cantidad y precio. En este caso, FOK (Fill or Kill) significa que la orden debe ejecutarse completamente al precio especificado o no ejecutarse en absoluto.
        }

        # Mandamos el close_request
        result = mt5.order_send(close_request)

        # Verificar el resultado de la ejecución de la orden
        if self._check_execution_status(result):
            print(f" Posición con ticket {ticket} en {position.symbol} y volumen {position.volume} se ha cerrado correctamente")
            # Generar el execution event y añadirlo a la cola
            self._create_and_put_execution_event(result)
        else:
            # Mandaremos un mensaje de error
            print(f" Ha habido un error al cerrar la posición {ticket} en {position.symbol} con volumen {position.volume}: {result.comment}")
    
    def close_strategy_long_positions_by_symbol(self, symbol: str) -> None:
        """
        Closes all long positions for a specific symbol in the strategy's portfolio.

        Parameters:
        symbol (str): The symbol of the positions to be closed.

        Returns:
        None
        """
        # Accedemos a todas las posiciones abiertas por nuestra estrategia
        positions = self.PORTFOLIO.get_strategy_open_positions()

        # Filtrar posiciones por símbolo y por dirección
        for position in positions:
            if position.symbol == symbol and position.type == mt5.ORDER_TYPE_BUY:
                self.close_position_by_ticket(position.ticket)

    def close_strategy_short_positions_by_symbol(self, symbol: str) -> None:
        """
        Closes all short positions for a specific symbol in the strategy's portfolio.

        Parameters:
        symbol (str): The symbol of the positions to be closed.

        Returns:
        None
        """
        # Accedemos a todas las posiciones abiertas por nuestra estrategia
        positions = self.PORTFOLIO.get_strategy_open_positions()

        # Filtrar posiciones por símbolo y por dirección
        for position in positions:
            if position.symbol == symbol and position.type == mt5.ORDER_TYPE_SELL:
                self.close_position_by_ticket(position.ticket)

    # Este metodo es para ordenes tipo PENDING
    def _create_and_put_placed_pending_order_event(self, order_event: OrderEvent) -> None: # este metodo recibe OrderEvent y genera un PlacedPendingOrderEvent y lo coloca en la cola de eventos
        """
        Creates a PlacedPendingOrderEvent object based on the given OrderEvent and puts it in the events queue.

        Args:
            order_event (OrderEvent): The OrderEvent object containing the necessary information.

        Returns:
            None
        """
        # Creamos el placed pending order event. En events.py creo PlacedPendingOrderEvent para diferenciarlo de OrderEvent, ya que este último es el que se genera desde la estrategia y el primero es el que se genera desde el OrderExecutor cuando la orden pendiente ha sido colocada correctamente en la plataforma.
        placed_pending_order_event = PlacedPendingOrderEvent(
                                                        symbol=order_event.symbol,
                                                        signal=order_event.signal,
                                                        target_order=order_event.target_order,
                                                        target_price=order_event.target_price,
                                                        magic_number=order_event.magic_number,
                                                        sl=order_event.sl,
                                                        tp=order_event.tp,
                                                        volume=order_event.volume)
        
        # Lo colocamos en la events queue
        self.events_queue.put(placed_pending_order_event)


     # Este metodo es para ordenes tipo
    def _create_and_put_execution_event(self, order_result) -> None:
        """
        Creates an execution event based on the order result and puts it into the events queue.

        Args:
            order_result (OrderResult): The result of the order execution.

        Returns:
            None
        """
        # Obtenemos la información del deal resultado de la ejecución de la orden usando la POSICIÓN a la que el deal pertenece (en lugar del ticket del propio deal),
        # ya que en LIVE el resultado del deal suele ser 0 si lo consultamos inmediatamente.
        #deal = mt5.history_deals_get(ticket=order_result.deal)[0]. Esto esta mas abajo aunque con position en lugar de ticket; por ahora lo inicializa con None. Notar q el deal [0] pq result.order es una tupla q contiene en la primera posicion el deal
        deal = None

        # Simulamos un fill_time usando el momento actual
        fill_time = datetime.now()
        
        # Creamos un pequeño bucle para dar tiempo al servidor a que genere el deal, y definimos un máximo de 5 intentos
        for _ in range(5):
            # Esperamos 0.5 segundos
            time.sleep(0.5)
            try:
                deal = mt5.history_deals_get(position=order_result.order)[0]  # Usamos position en lugar de ticket. 
            except IndexError:
                deal = None
                
            if not deal:
                # Si no obtenemos el deal, vamos a guardar el fill time como "ahora" para tener una aproximación -> puedes modificarlo si lo consideras necesario
                fill_time = datetime.now()
                continue
            else:
                break
        
        # Si pasado el bucle no hemos obtenido el deal, mostramos un mensaje de error
        if not deal:
            print(f" ORD EXEC: No se ha podido obtener el deal de la ejecución de la orden {order_result.order}, aunque probablemente haya sido ejecutada.")

        # Creamos el execution event
        execution_event = ExecutionEvent(symbol=order_result.request.symbol,
                                        signal=SignalType.BUY if order_result.request.type == mt5.DEAL_TYPE_BUY else SignalType.SELL,
                                        fill_price=order_result.price,
                                        fill_time=fill_time if not deal else pd.to_datetime(deal.time_msc, unit='ms'), # aca lo pasa a timestamp
                                        volume=order_result.request.volume)


        
        # Colocar el execution event a la cola de eventos
        self.events_queue.put(execution_event)

    def _check_execution_status(self, order_result) -> bool: # order_result es el result que le pasamos mas arriba al llamar a este metodo, pero ojo q instructor mencionò q lo correcto arquitectonicamente es
        # crear entidades para poder recepcionar la respuesta del request (creo q se refiere mas a dto q a entidades segun yo).
        """
        Checks the execution status of an order.

        Args:
            order_result (mt5.TradeResult): The result of the order execution.

        Returns:
            bool: True if the execution status is successful, False otherwise.
        """
        if order_result.retcode == mt5.TRADE_RETCODE_DONE:
            # todo ha ido bien
            return True
        elif order_result.retcode == mt5.TRADE_RETCODE_DONE_PARTIAL: # pq a veces el broker no puede ejecutar toda la orden, y ejecuta solo una parte de la orden, y devuelve este código de error. En ese caso, podemos decidir si queremos aceptar la ejecución parcial o no.
            return True
        else:
            return False

