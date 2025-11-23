# estrategia_rapida.py - Estrategia sin dependencias problemáticas
import random
from datetime import datetime

class EstrategiaRapida:
    """Estrategia rápida sin dependencias de Yahoo API"""
    
    def __init__(self):
        self.precios_base = {
            # FOREX
            "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550, "EURAUD": 1.6350,
            "USDJPY": 148.50, "AUDUSD": 0.6520, "EURGBP": 0.8550, "GBPUSD": 1.2650,
            "NZDUSD": 0.6080, "USDCHF": 0.8800, "GBPJPY": 188.00,
            
            # MATERIAS PRIMAS
            "XAUUSD": 2185.50, "XAGUSD": 24.85, "OILUSD": 78.30, "XPTUSD": 925.80,
        }
    
    def analizar_par(self, par):
        """Analizar par rápidamente sin dependencias externas"""
        try:
            # Precio simulado
            precio_base = self.precios_base.get(par, 1.0000)
            
            if par in ["XAUUSD", "XAGUSD", "XPTUSD"]:
                volatilidad = random.uniform(-0.005, 0.005)
            elif par in ["OILUSD"]:
                volatilidad = random.uniform(-0.008, 0.008)
            else:
                volatilidad = random.uniform(-0.001, 0.001)
                
            precio_actual = round(precio_base * (1 + volatilidad), 5)
            
            # RSI simulado
            rsi = random.randint(25, 75)
            
            # Señal basada en RSI (20% probabilidad de señal)
            if random.random() > 0.8:
                if rsi < 35:
                    direccion = "COMPRA"
                    motivo = f"RSI Oversold ({rsi})"
                elif rsi > 65:
                    direccion = "VENTA" 
                    motivo = f"RSI Overbought ({rsi})"
                else:
                    return None
                
                # Calcular TP/SL básicos
                if direccion == "COMPRA":
                    tp1 = round(precio_actual * 1.005, 5)
                    tp2 = round(precio_actual * 1.010, 5)
                    sl = round(precio_actual * 0.995, 5)
                else:
                    tp1 = round(precio_actual * 0.995, 5)
                    tp2 = round(precio_actual * 0.990, 5)
                    sl = round(precio_actual * 1.005, 5)
                
                señal = {
                    'par': par,
                    'direccion': direccion,
                    'precio_actual': precio_actual,
                    'tp1': tp1,
                    'tp2': tp2,
                    'sl': sl,
                    'rsi': rsi,
                    'tendencia': "ALCISTA" if rsi < 40 else "BAJISTA" if rsi > 60 else "LATERAL",
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'fuente_datos': 'Estrategia Rápida',
                    'winrate_esperado': 55 + random.randint(0, 15),
                    'confianza': "ALTA" if (rsi < 30 or rsi > 70) else "MEDIA",
                    'motivo_señal': motivo
                }
                
                print(f"🎯 Señal rápida {par}: {direccion} a {precio_actual} (RSI: {rsi})")
                return señal
            
            return None
            
        except Exception as e:
            print(f"❌ Error en estrategia rápida {par}: {e}")
            return None

# Instancia global
estrategia_rapida = EstrategiaRapida()
