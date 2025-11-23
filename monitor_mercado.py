# monitor_mercado.py - VERSIÓN SIMPLIFICADA Y CORREGIDA
import time
import random
from datetime import datetime

class MonitorMercado:
    def __init__(self):
        self.monitoreando = False
        self.capital_actual = 1000
        
    def obtener_estadisticas_riesgo(self):
        return {
            'capital_actual': self.capital_actual,
            'total_operaciones': 0,
            'operaciones_ganadoras': 0,
            'win_rate': 0,
            'perdidas_consecutivas': 0
        }
    
    def analizar_par(self, par):
        """Analizar par de forma simplificada sin dependencias problemáticas"""
        try:
            print(f"🔍 Analizando {par}...")
            
            # Simulación básica sin Yahoo API problemático
            precio_simulado = self._simular_precio(par)
            rsi_simulado = random.randint(30, 70)
            
            # Señal aleatoria para testing (20% probabilidad)
            if random.random() > 0.8:
                direccion = "COMPRA" if rsi_simulado < 40 else "VENTA"
                señal = {
                    'par': par,
                    'direccion': direccion,
                    'precio_actual': precio_simulado,
                    'rsi': rsi_simulado,
                    'tendencia': "ALCISTA" if rsi_simulado < 40 else "BAJISTA" if rsi_simulado > 60 else "LATERAL",
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'fuente_datos': 'Simulación'
                }
                print(f"🎯 Señal detectada: {par} {direccion} - RSI: {rsi_simulado}")
                return señal
            
            print(f"📊 {par} - Sin señal clara (RSI: {rsi_simulado})")
            return None
            
        except Exception as e:
            print(f"❌ Error analizando {par}: {e}")
            return None
    
    def _simular_precio(self, par):
        """Simular precio sin dependencias externas"""
        precios_base = {
            "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550, "EURAUD": 1.6350,
            "XAUUSD": 2185.50, "XAGUSD": 24.85, "OILUSD": 78.30, "XPTUSD": 925.80
        }
        precio_base = precios_base.get(par, 1.0000)
        
        # Diferente volatilidad según tipo de activo
        if par in ["XAUUSD", "XAGUSD", "XPTUSD"]:
            volatilidad = random.uniform(-0.005, 0.005)
        elif par in ["OILUSD"]:
            volatilidad = random.uniform(-0.008, 0.008)
        else:
            volatilidad = random.uniform(-0.001, 0.001)
            
        return round(precio_base * (1 + volatilidad), 5)
    
    def ejecutar_señal(self, señal):
        """Ejecutar señal simplificada"""
        print(f"🎯 Ejecutando señal: {señal['par']} {señal['direccion']} a {señal['precio_actual']}")
        return True
    
    def iniciar_monitoreo(self):
        """Iniciar monitoreo continuo"""
        print("🤖 INICIANDO MONITOREO AUTOMÁTICO...")
        self.monitoreando = True
        
        ciclo = 0
        while self.monitoreando:
            ciclo += 1
            print(f"🔄 Ciclo #{ciclo} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Pares a monitorear
            pares = ["EURUSD", "USDCAD", "XAUUSD", "XAGUSD", "OILUSD"]
            
            for par in pares:
                if not self.monitoreando:
                    break
                    
                señal = self.analizar_par(par)
                if señal:
                    self.ejecutar_señal(señal)
                
                time.sleep(2)
            
            print("⏳ Esperando 2 minutos para próximo ciclo...")
            for i in range(120):
                if not self.monitoreando:
                    break
                time.sleep(1)
    
    def detener_monitoreo(self):
        """Detener monitoreo"""
        print("🛑 Deteniendo monitoreo...")
        self.monitoreando = False
