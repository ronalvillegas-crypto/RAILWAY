# yahoo_fallback.py - Fallback seguro para Yahoo API
import random
from datetime import datetime

class YahooFallback:
    """Fallback seguro cuando YahooFinanceAPI no está disponible"""
    
    def __init__(self):
        self.precios_base = {
            # FOREX
            "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550, "EURAUD": 1.6350,
            "USDJPY": 148.50, "AUDUSD": 0.6520, "EURGBP": 0.8550, "GBPUSD": 1.2650,
            "NZDUSD": 0.6080, "USDCHF": 0.8800, "GBPJPY": 188.00,
            
            # MATERIAS PRIMAS
            "XAUUSD": 2185.50, "XAGUSD": 24.85, "OILUSD": 78.30, "XPTUSD": 925.80,
        }
    
    def obtener_precio(self, simbolo):
        """Obtener precio simulado"""
        precio_base = self.precios_base.get(simbolo, 1.0000)
        
        if simbolo in ["XAUUSD", "XAGUSD", "XPTUSD"]:
            volatilidad = random.uniform(-0.005, 0.005)
        elif simbolo in ["OILUSD"]:
            volatilidad = random.uniform(-0.008, 0.008)
        else:
            volatilidad = random.uniform(-0.001, 0.001)
            
        return round(precio_base * (1 + volatilidad), 5)
    
    def obtener_datos_tecnicos(self, simbolo):
        """Obtener datos técnicos simulados"""
        precio_actual = self.obtener_precio(simbolo)
        rsi = random.randint(30, 70)
        
        if rsi < 40:
            tendencia = "ALCISTA"
        elif rsi > 60:
            tendencia = "BAJISTA"
        else:
            tendencia = "LATERAL"
        
        return {
            "precio_actual": precio_actual,
            "rsi": rsi,
            "tendencia": tendencia,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fuente": "Simulación Fallback"
        }

# Instancia global para uso rápido
yahoo_fallback = YahooFallback()
