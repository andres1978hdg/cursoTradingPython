from data_provider.data_provider import DataProvider
import queue
import time
from typing import Dict, Callable

from events.events import DataEvent


class TradingDirector():
    
    def __init__(self, events_queue: queue.Queue, data_provider: DataProvider):
        """
        Initializes the TradingDirector object.

        Args:
            events_queue (queue.Queue): The queue to receive events.
            data_provider (DataProvider): The data provider object.
            signal_generator (ISignalGenerator): The signal generator object.
            position_sizer (PositionSizer): The position sizer object.
            risk_manager (RiskManager): The risk manager object.
            order_executor (OrderExecutor): The order executor object.
            notification_service (NotificationService): The notification service object.
        """
        self.events_queue = events_queue
        
        # Referencia de los distintos módulos
        self.DATA_PROVIDER = data_provider

         # Controlador de trading
        self.continue_trading: bool = True

     # Creación del event handler
        self.event_handler: Dict[str, Callable] = {
            "DATA": self._handle_data_event
            #, "SIGNAL": self._handle_signal_event,
        }

    def _handle_data_event(self, event: DataEvent):
        """
        Handle the data event.

        Args:
            event (DataEvent): The data event object.

        Returns:
            None
        """
        # Aquí dentro gestionamos los eventos de tipo DataEvent
   # Aquí dentro gestionamos los eventos de tipo DataEvent
        print(f"{event.data.name} - Recibido evento de tipo DATA para el símbolo {event.symbol} - Ultimo precio de cierre: {event.data.close}")
       
        


    def execute(self) -> None:
        """
        Executes the main trading loop.

        This method continuously checks for events in the events queue and handles them accordingly.
        If no events are available, it checks for new data from the data provider.
        The loop continues until the `continue_trading` flag is set to False.

        Note:
        - The events are processed by the corresponding event handlers.
        - If an unknown event is encountered, it is handled by the `_handle_unknown_event` method.
        - If a None event is encountered, it is handled by the `_handle_none_event` method.

        Returns:
        None
        """
        # Definición del bucle principal
        while self.continue_trading:
            try:
                event = self.events_queue.get(block=False)    # Recordar que es una cola FIFO
            
            except queue.Empty: #  Si la cola esta vacia, es un indicio de q podrìa no haber datos nuevos, asi q hay q buscar si hay datos nuevos
                self.DATA_PROVIDER.check_for_new_data()

            else:
                if event is not None:
                  handler = self.event_handler.get(event.event_type) #esto euivale al  "DATA": self._handle_data_event de mas arriba
                  handler(event)
                else:
                    self.continue_trading = False
                    print("Error: Se ha recibido un evento None, lo que indica que se ha decidido detener el programa.")

                time.sleep(0.1) #para no saturar la CPU, hacemos una pausa de 0.1 segundos antes de volver a comprobar la cola de eventos