from data_provider.data_provider import DataProvider
import queue
import time


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
                    pass