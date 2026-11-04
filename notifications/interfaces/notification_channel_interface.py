# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from typing import Protocol

# Esta interfaz define el contrato que deben cumplir todos los canales de notificación. Cualquier clase que implemente esta interfaz debe proporcionar una implementación del método send_message.
# INotificationChannel es inyectada por dependencia en la clase SignalMACrossover, lo que permite que la clase SignalMACrossover pueda enviar notificaciones a través de cualquier canal de notificación que implemente esta interfaz, sin necesidad de conocer los detalles de implementación del canal de notificación específico. Esto promueve la flexibilidad y la extensibilidad del sistema, permitiendo agregar nuevos canales de notificación en el futuro sin modificar la clase SignalMACrossover.

class INotificationChannel(Protocol): 
    
    def send_message(self, title: str, message: str):
        ...