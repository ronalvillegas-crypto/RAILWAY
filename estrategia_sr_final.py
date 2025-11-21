# estrategia_sr_final.py - ESTRATEGIA DEL BACKTESTING INTEGRADA
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EstrategiaSRFinal:
    def __init__(self):
        self.parametros = {
            'window_sr': 15,
            'umbral_proximidad': 0.0020,
            'ema_rapida': 20,
            'ema_lenta': 15, 
            'stop_loss': 0.0025,
            'take_profit_multiplier': 3.5,
            'risk_por_operacion': 0.025,
            'trailing_stop_activation': 0.0020
        }
        
    def detectar_señal_backtesting(self, datos_historicos):
        """Aplicar la estrategia del backtesting a datos históricos"""
        if len(datos_historicos) < self.parametros['window_sr'] + 10:
            return None
            
        df = pd.DataFrame(datos_historicos)
        
        # Calcular indicadores
        precio_actual = df['close'].iloc[-1]
        
        # Detectar S/R
        soporte = df['low'].iloc[-self.parametros['window_sr']:].min()
        resistencia = df['high'].iloc[-self.parametros['window_sr']:].max()
        
        # Calcular EMA
        ema_rapida = df['close'].ewm(span=self.parametros['ema_rapida']).mean().iloc[-1]
        ema_lenta = df['close'].ewm(span=self.parametros['ema_lenta']).mean().iloc[-1]
        
        # Calcular distancias
        dist_soporte = abs(precio_actual - soporte) / precio_actual
        dist_resistencia = abs(precio_actual - resistencia) / precio_actual
        
        # 🎯 CONDICIONES BACKTESTING OPTIMIZADAS
        if (dist_soporte <= self.parametros['umbral_proximidad'] and 
            ema_rapida > ema_lenta and
            df['close'].iloc[-1] > df['open'].iloc[-1]):
            return {
                'direccion': "COMPRA",
                'precio_actual': precio_actual,
                'soporte': soporte,
                'resistencia': resistencia,
                'confianza': 'ALTA',
                'estrategia': 'S/R Final Perfecta'
            }
            
        elif (dist_resistencia <= self.parametros['umbral_proximidad'] and 
              ema_rapida < ema_lenta and
              df['close'].iloc[-1] < df['open'].iloc[-1]):
            return {
                'direccion': "VENTA", 
                'precio_actual': precio_actual,
                'soporte': soporte,
                'resistencia': resistencia,
                'confianza': 'ALTA',
                'estrategia': 'S/R Final Perfecta'
            }
        
        return None
    
    def calcular_niveles_operacion(self, señal, params_par):
        """Calcular niveles TP/SL según parámetros del backtesting"""
        precio = señal['precio_actual']
        direccion = señal['direccion']
        
        # Calcular SL base
        sl_pips = self.parametros['stop_loss'] * precio
        
        if direccion == "COMPRA":
            sl_precio = precio - sl_pips
            tp_precio = precio + (sl_pips * self.parametros['take_profit_multiplier'])
        else:
            sl_precio = precio + sl_pips
            tp_precio = precio - (sl_pips * self.parametros['take_profit_multiplier'])
        
        # Niveles DCA (usando parámetros del par)
        if direccion == "COMPRA":
            dca_1 = precio * (1 - params_par['dca_niveles'][0])
            dca_2 = precio * (1 - params_par['dca_niveles'][1])
        else:
            dca_1 = precio * (1 + params_par['dca_niveles'][0])
            dca_2 = precio * (1 + params_par['dca_niveles'][1])
        
        return {
            'sl': round(sl_precio, 5),
            'tp1': round(tp_precio, 5),
            'tp2': round(tp_precio * 1.1, 5),  # TP2 un 10% más lejano
            'dca_1': round(dca_1, 5),
            'dca_2': round(dca_2, 5)
        }
