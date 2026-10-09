# QUANTDEMY - https://quantdemy.com - Trading con Python y MetaTrader 5: Crea tu Propio Framework

from utils.utils import Utils
from events.events import SizingEvent
from ..interfaces.risk_manager_interface import IRiskManager
from ..properties.risk_manager_properties import MaxLeverageFactorRiskProps
import MetaTrader5 as mt5
import sys

#Recordar q el factor de apalancamiento permite definir nuestro margen de operacion.
"""
Supongamos que tengo en dinero mil dolares en mi cuenta de Pepperstone y quiero abrir una posicion donde yo aporto un margen de cien dolares para Comprar USDCLP.
Perfecto, vamos a desglosar tu ejemplo con números claros:

📊 Escenario: Cuenta en Pepperstone con $1,000 USD
Balance inicial: $1,000 USD
Margen aportado: $100 USD (10% de tu cuenta)
Apalancamiento: Supongamos que tu cuenta está configurada en 1:100 (muy común en Forex/CFDs).

⚖️ Cálculo de la posición
Con $100 de margen y apalancamiento 1:100, puedes controlar una posición de:

100 ⋅ 100 = 10,000 USD
En el par USDCLP, si el precio está en 973 CLP, tu posición equivale a:
10,000 ⋅ 973 = 9,730,000 CLP
📈 Impacto de movimientos
Si el USDCLP sube +1 peso (de 973 a 974), tu ganancia sería:

10,000⋅1=10,000 CLP≈10.28 USD

Si el USDCLP baja -1 peso, tu pérdida sería la misma: ≈ 10 USD.

"""
class MaxLeverageFactorRiskManager(IRiskManager):

    def __init__(self, properties: MaxLeverageFactorRiskProps):
        """
        Initializes a MaxLeverageFactorRiskManager object.

        Args:
            properties (MaxLeverageFactorRiskProps): The properties object containing the maximum leverage factor.
        """
        self.max_leverage_factor = properties.max_leverage_factor # Este es el maximo factor de apalancamiento, definido por el broker (Pepperstone en mi caso)

    #account_value_acc_ccy es el saldo estatico de la cuenta, sin considerar ganancias o perdidas flotantes de posiciones abiertas
    def _compute_leverage_factor(self, account_value_acc_ccy: float) -> float: # Aca calculamos el factor de apalancamiento calculado real, que debe ser menor al maximo factor de apalancamiento
        """
        Computes the leverage factor based on the account value and equity.

        Args:
            account_value_acc_ccy (float): The account value in the account currency.

        Returns:
            float: The computed leverage factor.
        """

        account_equity = mt5.account_info().equity # el equity es el valor total de la cuenta, es decir es la suma del saldo estatico de la cuenta mas las ganancias/pérdidas flotantes de posiciones abiertas. Es decir, es el valor real de la cuenta en un momento dado, considerando todas las operaciones abiertas y su impacto en el balance de la cuenta.

        if account_equity <= 0:
            return sys.float_info.max
        else:
            return account_value_acc_ccy / account_equity

    # Esto es cuando deseamos invertir un nuevo monto es una posicion que ya teniamos abierta de antes
    def _check_expected_new_position_is_compliant_with_max_leverage_factor(self, sizing_event: SizingEvent, 
                                                                            current_positions_value_acc_ccy: float, # el monto que ya teniamos de antes para esa posicion
                                                                            new_position_value_acc_ccy: float) -> bool: # el nuevo monto que queremos invertir para esa posicion
        """
        Checks if the expected new position is compliant with the maximum leverage factor.

        Args:
            sizing_event (SizingEvent): The sizing event for the new position.
            current_positions_value_acc_ccy (float): The current value of all positions in the account currency.
            new_position_value_acc_ccy (float): The value of the new position in the account currency.

        Returns:
            bool: True if the new position is compliant with the maximum leverage factor, False otherwise.
        """
        # Calculamos el nuevo expected account value que tendría la cuenta si ejecutáramos la nueva posición
        new_account_value = current_positions_value_acc_ccy + new_position_value_acc_ccy

        # Calculamos el nuevo factor de apalancamiento que tendríamos SI EJECUTÁRAMOS esa posición
        new_leverage_factor = self._compute_leverage_factor(new_account_value)

        # Comprobamos si el nuevo leverage factor sería mayor a nuestro máximo leverage factor
        if abs(new_leverage_factor) <= self.max_leverage_factor:
            return True
        else:
            print(f"RISK MGMT: La posición objetivo {sizing_event.signal} {sizing_event.volume} implica un Leverage Factor de {abs(new_leverage_factor):.2f}, que supera el máx. de {self.max_leverage_factor}")
            return False

    # Este metodo funciona como portero de discoteca, si el nuevo leverage factor es mayor al máximo permitido, no deja pasar la orden y devuelve 0.0, si es menor o igual, deja pasar la orden y devuelve el volumen de la orden.
    def assess_order(self, sizing_event: SizingEvent, current_positions_value_acc_ccy: float, new_position_value_acc_ccy: float) -> float: 
        """
        Assess the order and determine whether it should be allowed or not based on the maximum leverage factor.

        Args:
            sizing_event (SizingEvent): The sizing event for the order.
            current_positions_value_acc_ccy (float): The current value of all positions in the account currency.
            new_position_value_acc_ccy (float): The value of the new position in the account currency.

        Returns:
            float: The volume of the order if it is compliant with the maximum leverage factor, otherwise 0.0.
        """
        if self._check_expected_new_position_is_compliant_with_max_leverage_factor(sizing_event, current_positions_value_acc_ccy, new_position_value_acc_ccy):
            return sizing_event.volume #
        else:
            return 0.0 # con esto evitamos abrir una posicion nueva