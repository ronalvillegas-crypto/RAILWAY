# gestor_volatilidad.py - GESTIÓN DE VOLATILIDAD EN TIEMPO REAL
import numpy as np
from datetime import datetime

class GestorVolatilidad:
    """
    Calcula y gestiona volatilidad para ajustar stops y posición sizing
    """
    
    def __init__(self):
        self.historico_volatilidad = {}
    
    def calcular_atr(self, datos_ohlc, periodo=14):
        """
        Calcular Average True Range (ATR) - indicador de volatilidad
        """
        if len(datos_ohlc['high']) < periodo + 1:
            return None
        
        high = datos_ohlc['high'][-periodo:]
        low = datos_ohlc['low'][-periodo:]
        close = datos_ohlc['close'][-periodo-1:-1]  # Cierres anteriores
        
        true_ranges = []
        for i in range(len(high)):
            if i < len(close):
                tr1 = high[i] - low[i]
                tr2 = abs(high[i] - close[i])
                tr3 = abs(low[i] - close[i])
                true_ranges.append(max(tr1, tr2, tr3))
            else:
                true_ranges.append(high[i] - low[i])
        
        if true_ranges:
            return sum(true_ranges) / len(true_ranges)
        return None
    
    def calcular_volatilidad_historica(self, datos_ohlc, periodo=20):
        """
        Calcular volatilidad histórica (desviación estándar de retornos)
        """
        if len(datos_ohlc['close']) < periodo + 1:
            return None
        
        closes = [c for c in datos_ohlc['close'] if c is not None]
        if len(closes) < periodo + 1:
            return None
        
        # Calcular retornos porcentuales
        retornos = []
        for i in range(1, len(closes)):
            if closes[i-1] and closes[i] and closes[i-1] != 0:
                retorno = (closes[i] - closes[i-1]) / closes[i-1]
                retornos.append(retorno)
        
        if len(retornos) >= periodo:
            retornos_recientes = retornos[-periodo:]
            volatilidad = np.std(retornos_recientes)
            return volatilidad * 100  # Como porcentaje
        
        return None
    
    def obtener_nivel_volatilidad(self, par, datos_ohlc):
        """
        Clasificar volatilidad en niveles: BAJA, MEDIA, ALTA
        """
        atr = self.calcular_atr(datos_ohlc)
        vol_historica = self.calcular_volatilidad_historica(datos_ohlc)
        
        if not atr or not vol_historica:
            return "MEDIA"  # Valor por defecto
        
        # Umbrales basados en tipo de activo
        if par in ["EURUSD", "USDJPY", "GBPUSD"]:  # Forex mayor
            if vol_historica < 0.4: return "BAJA"
            elif vol_historica < 0.8: return "MEDIA"
            else: return "ALTA"
        
        elif par in ["XAUUSD", "XAGUSD"]:  # Metales
            if vol_historica < 0.8: return "BAJA"
            elif vol_historica < 1.5: return "MEDIA"
            else: return "ALTA"
        
        elif par in ["OILUSD", "NGASUSD"]:  # Energía
            if vol_historica < 1.0: return "BAJA"
            elif vol_historica < 2.0: return "MEDIA"
            else: return "ALTA"
        
        else:  # Por defecto
            if vol_historica < 0.5: return "BAJA"
            elif vol_historica < 1.0: return "MEDIA"
            else: return "ALTA"
    
    def ajustar_stop_loss_por_volatilidad(self, par, sl_base, datos_ohlc):
        """
        Ajustar stop loss según volatilidad actual
        """
        nivel_volatilidad = self.obtener_nivel_volatilidad(par, datos_ohlc)
        
        multiplicadores = {
            "BAJA": 1.2,    # SL más amplio en baja volatilidad
            "MEDIA": 1.0,   # SL normal
            "ALTA": 0.8     # SL más ajustado en alta volatilidad
        }
        
        multiplicador = multiplicadores.get(nivel_volatilidad, 1.0)
        return sl_base * multiplicador
    
    def ajustar_take_profit_por_volatilidad(self, par, tp_base, datos_ohlc):
        """
        Ajustar take profit según volatilidad actual
        """
        nivel_volatilidad = self.obtener_nivel_volatilidad(par, datos_ohlc)
        
        multiplicadores = {
            "BAJA": 0.8,    # TP más conservador en baja volatilidad
            "MEDIA": 1.0,   # TP normal
            "ALTA": 1.3     # TP más ambicioso en alta volatilidad
        }
        
        multiplicador = multiplicadores.get(nivel_volatilidad, 1.0)
        return tp_base * multiplicador
    
    def calcular_tamaño_posicion_volatilidad(self, capital, riesgo_por_operacion, par, datos_ohlc):
        """
        Calcular tamaño de posición ajustado por volatilidad
        """
        nivel_volatilidad = self.obtener_nivel_volatilidad(par, datos_ohlc)
        
        # Reducir tamaño en alta volatilidad
        ajustes_tamaño = {
            "BAJA": 1.2,    # Tamaño normal
            "MEDIA": 1.0,   # Tamaño normal
            "ALTA": 0.7     # Reducir 30% en alta volatilidad
        }
        
        ajuste = ajustes_tamaño.get(nivel_volatilidad, 1.0)
        tamaño_base = capital * riesgo_por_operacion
        return tamaño_base * ajuste
    
    def generar_alerta_volatilidad(self, par, datos_ohlc):
        """
        Generar alertas de cambios significativos en volatilidad
        """
        vol_actual = self.calcular_volatilidad_historica(datos_ohlc, 10)  # Corto plazo
        vol_historica = self.calcular_volatilidad_historica(datos_ohlc, 50)  # Largo plazo
        
        if vol_actual and vol_historica:
            cambio = (vol_actual - vol_historica) / vol_historica * 100
            
            if abs(cambio) > 50:  # Cambio del 50% o más
                return f"📈 VOLATILIDAD {par}: {cambio:+.1f}% vs histórico"
        
        return None
