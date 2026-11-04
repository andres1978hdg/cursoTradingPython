# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from .interfaces.notification_channel_interface import INotificationChannel
from .properties.properties import TelegramNotificationProperties, NotificationChannelBaseProperties
from .channels.telegram_notification_channel import TelegramNotificationChannel

class NotificationService:



    """
    def __init__(self, channel: INotificationChannel) -> None: #ESTE CONSTRUCTOR LO HABIA PUESTO PRIMERO EL INSTRUCTOR. ACA SE APRECIA CLARAMENTE LA  INYECCION DE DEPENDENCIA. LA CLASE NotificationService NO SABE NADA DE LA IMPLEMENTACION DEL CANAL DE NOTIFICACION, SOLO SABE QUE TIENE UN METODO send_message. EL CANAL DE NOTIFICACION ES INYECTADO POR DEPENDENCIA EN EL CONSTRUCTOR DE LA CLASE NotificationService, LO QUE PERMITE QUE LA CLASE NotificationService PUEDA ENVIAR NOTIFICACIONES A TRAVES DE CUALQUIER CANAL DE NOTIFICACION QUE IMPLEMENTE LA INTERFAZ INotificationChannel, SIN NECESIDAD DE CONOCER LOS DETALLES DE IMPLEMENTACION DEL CANAL DE NOTIFICACION ESPECIFICO. ESTO PROMUEVE LA FLEXIBILIDAD Y LA EXTENSIBILIDAD DEL SISTEMA, PERMITIENDO AGREGAR NUEVOS CANALES DE NOTIFICACION EN EL FUTURO SIN MODIFICAR LA CLASE NotificationService.
        self._channel = channel
    """



    def __init__(self, properties: NotificationChannelBaseProperties) -> None:
        """
        Initializes a new instance of the Notification class.

        Args:
            properties (NotificationChannelBaseProperties): The properties of the notification channel.

        Returns:
            None
        """
        self._channel = self._get_channel(properties)
        
    def _get_channel(self, properties: NotificationChannelBaseProperties) -> INotificationChannel:
        """
        Returns an instance of the appropriate notification channel based on the provided properties.

        Args:
            properties (NotificationChannelBaseProperties): The properties of the notification channel.

        Returns:
            INotificationChannel: An instance of the notification channel.

        Raises:
            Exception: If the selected communication channel does not exist.
        """
        if isinstance(properties, TelegramNotificationProperties):
            return TelegramNotificationChannel(properties)
        else:
            raise Exception("ERROR: El canal de comunicación seleccionado no existe")
    
    def send_notification(self, title: str, message: str):
        """
        Sends a notification with the specified title and message.

        Args:
            title (str): The title of the notification.
            message (str): The message of the notification.
        """
        self._channel.send_message(title, message)
