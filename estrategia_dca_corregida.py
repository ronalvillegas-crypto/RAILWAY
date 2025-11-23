# estrategia_dca.py - ESTRATEGIA S/R REAL CON INDICADORES REALES - CORREGIDO
import random
from datetime import datetime

class EstrategiaDCA:
    def __init__(self):
        self.operaciones_activas = {}
        # IMPORTACIONES DIFERIDAS
        self.yahoo = None
        self.analisis_sr = None
        self.indicadores_reales = None
    
    def _get_yahoo(self):
        if self.yahoo is None:
            try:
                from yahoo_api import YahooFinanceAPI
                self.yahoo = YahooFinanceAPI()
            except ImportError as e:
                print(f"⚠️ Error importando YahooFinanceAPI: {e}")
                return None
        return self.yahoo
    
    def _get_analisis_sr(self):
        if self.analisis_sr is None:
            try:
                from analisis_tecnico import AnalisisTechnicoSR
                self.analisis_sr = AnalisisTechnicoSR()
            except ImportError as e:
                print(f"⚠️ Error importando AnalisisTechnicoSR: {e}")
                return None
        return self.analisis_sr
    
    def _get_indicadores_reales(self):
        if self.indicadores_reales is None:
            try:
                from indicadores_reales import IndicadoresReales
                self.indicadores_reales = IndicadoresReales()
            except ImportError as e:
                print(f"⚠️ Error importando IndicadoresReales: {e}")
                return None
        return self.indicadores_reales
    
    def generar_señal_real(self, par):
        """Generar señal REAL con indicadores REALES"""
        try:
            from config import PARAMETROS_POR_PAR
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['EURUSD'])
            
            # Obtener datos TÉCNICOS REALES
            datos_reales = self.obtener_datos_tecnicos_reales(par)
            
            if not datos_reales:
                print(f"❌ No se pudieron obtener datos técnicos reales para {par}")
                return None
            
            precio = datos_reales['precio_actual']
            rsi = datos_reales['rsi']
            tendencia = datos_reales['tendencia']
            fuente = datos_reales['fuente']
            
            print(f"🔍 Analizando {par} - Precio: {precio:.5f}, RSI: {rsi}, Tendencia: {tendencia}, Fuente: {fuente}")
            
            # 🎯 ANÁLISIS S/R REAL (ESTRATEGIA BACKTESTING)
            analisis_sr_obj = self._get_analisis_sr()
            if not analisis_sr_obj:
                print(f"❌ No se pudo inicializar análisis S/R para {par}")
                return None
                
            analisis_sr = analisis_sr_obj.analizar_estructura_mercado(
                par, precio, tendencia, rsi
            )
            
            # Solo generar señal si el análisis S/R es favorable
            if not analisis_sr['señal']:
                print(f"📊 {par}: {analisis_sr['motivo']}")
                return None
            
            # Verificar condiciones óptimas según backtesting
            if (analisis_sr['señal'] == "COMPRA" and 
                not analisis_sr_obj.es_zona_compra_optima(analisis_sr)):
                print(f"📊 {par}: Condiciones compra no óptimas - {analisis_sr['motivo']}")
                return None
                
            if (analisis_sr['señal'] == "VENTA" and 
                not analisis_sr_obj.es_zona_venta_optima(analisis_sr)):
                print(f"📊 {par}: Condiciones venta no óptimas - {analisis_sr['motivo']}") 
                return None
            
            direccion = analisis_sr['señal']
            confianza = analisis_sr['confianza']
            
            print(f"🎯 SEÑAL S/R CONFIRMADA: {par} {direccion} - {analisis_sr['motivo']}")
            
            # Calcular niveles con parámetros optimizados del backtesting
            if direccion == "COMPRA":
                tp1 = precio * (1 + params['tp_niveles'][0])
                tp2 = precio * (1 + params['tp_niveles'][1])
                sl = precio * (1 - params['sl'])
                dca_1 = precio * (1 - params['dca_niveles'][0])
                dca_2 = precio * (1 - params['dca_niveles'][1])
            else:
                tp1 = precio * (1 - params['tp_niveles'][0])
                tp2 = precio * (1 - params['tp_niveles'][1])
                sl = precio * (1 + params['sl'])
                dca_1 = precio * (1 + params['dca_niveles'][0])
                dca_2 = precio * (1 + params['dca_niveles'][1])
            
            return {
                'par': par,
                'direccion': direccion,
                'precio_actual': round(precio, 5),
                'tp1': round(tp1, 5),
                'tp2': round(tp2, 5),
                'sl': round(sl, 5),
                'dca_1': round(dca_1, 5),
                'dca_2': round(dca_2, 5),
                'rsi': rsi,
                'tendencia': tendencia,
                'winrate_esperado': params['winrate'],
                'rentabilidad_esperada': params['rentabilidad'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'fuente_datos': fuente,
                'leverage': params['leverage'],
                'confianza': confianza,
                # NUEVOS DATOS S/R
                'estrategia': 'S/R Etapa 1',
                'niveles_sr': analisis_sr['niveles_sr'],
                'zona_actual': analisis_sr['zona_actual'],
                'motivo_señal': analisis_sr['motivo'],
                'distancia_support': analisis_sr['distancia_support'],
                'distancia_resistance': analisis_sr['distancia_resistance']
            }
            
        except Exception as e:
            print(f"❌ Error en generar_señal_real: {e}")
            return None
    
    def obtener_datos_tecnicos_reales(self, par):
        """Obtener datos técnicos REALES usando IndicadoresReales"""
        try:
            # Usar el nuevo módulo de indicadores reales
            indicadores = self._get_indicadores_reales()
            if indicadores:
                datos = indicadores.obtener_indicadores_reales(par)
                if datos and datos['precio_actual']:
                    return datos
            
            # Fallback: usar Yahoo API
            yahoo = self._get_yahoo()
            if yahoo:
                return yahoo.obtener_datos_tecnicos(par)
            else:
                # Fallback final: simulación
                return self._datos_tecnicos_simulados(par)
                
        except Exception as e:
            print(f"❌ Error obteniendo datos técnicos reales: {e}")
            return self._datos_tecnicos_simulados(par)
    
    def _datos_tecnicos_simulados(self, par):
        """Datos técnicos simulados como último recurso"""
        precios_base = {
            "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550, "EURAUD": 1.6350,
            "XAUUSD": 2185.50, "XAGUSD": 24.85, "OILUSD": 78.30, "XPTUSD": 925.80
        }
        precio_base = precios_base.get(par, 1.0000)
        precio_actual = round(precio_base * (1 + random.uniform(-0.001, 0.001)), 5)
        rsi = random.randint(30, 70)
        
        return {
            'precio_actual': precio_actual,
            'rsi': rsi,
            'tendencia': "ALCISTA" if rsi < 40 else "BAJISTA" if rsi > 60 else "LATERAL",
            'fuente': 'Simulación'
        }
