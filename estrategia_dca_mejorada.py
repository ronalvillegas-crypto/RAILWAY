# estrategia_dca_mejorada.py - ESTRATEGIA MEJORADA CON NUEVAS FUNCIONALIDADES
import random
from datetime import datetime

class EstrategiaDCAMejorada:
    def __init__(self):
        self.operaciones_activas = {}
        self.gestor_sesiones = GestorSesionesMercado()
        self.analizador_correlaciones = AnalizadorCorrelaciones()
        self.gestor_volatilidad = GestorVolatilidad()
        
        # IMPORTACIONES DIFERIDAS
        self.yahoo = None
        self.analisis_sr = None
        self.indicadores_reales = None
    
    def _get_yahoo(self):
        if self.yahoo is None:
            try:
                from yahoo_api_mejorado import YahooFinanceAPI
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
    
    def generar_señal_mejorada(self, par, operaciones_activas=[]):
        """Generar señal con todas las mejoras implementadas"""
        try:
            from config import PARAMETROS_POR_PAR
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['EURUSD'])
            
            # 1. VERIFICAR HORARIO DE MERCADO
            if not self.gestor_sesiones.es_horario_optimo_trading():
                print(f"⏰ {par} - Fuera de horario óptimo de trading")
                return None
            
            # 2. VERIFICAR CORRELACIONES
            if operaciones_activas:
                evitar, motivo = self.analizador_correlaciones.deberia_evitar_señal(
                    {'par': par, 'direccion': 'COMPRA'},  # Placeholder
                    operaciones_activas
                )
                if evitar:
                    print(f"📊 {par} - Evitado por correlación: {motivo}")
                    return None
            
            # 3. OBTENER DATOS TÉCNICOS
            datos_reales = self.obtener_datos_tecnicos_reales(par)
            if not datos_reales:
                return None
            
            precio = datos_reales['precio_actual']
            rsi = datos_reales['rsi']
            tendencia = datos_reales['tendencia']
            fuente = datos_reales['fuente']
            
            # 4. ANÁLISIS S/R
            analisis_sr_obj = self._get_analisis_sr()
            if not analisis_sr_obj:
                return None
                
            analisis_sr = analisis_sr_obj.analizar_estructura_mercado(par, precio, tendencia, rsi)
            
            if not analisis_sr['señal']:
                print(f"📊 {par}: {analisis_sr['motivo']}")
                return None
            
            # 5. VERIFICAR CONDICIONES ÓPTIMAS
            direccion = analisis_sr['señal']
            if (direccion == "COMPRA" and 
                not analisis_sr_obj.es_zona_compra_optima(analisis_sr)):
                return None
                
            if (direccion == "VENTA" and 
                not analisis_sr_obj.es_zona_venta_optima(analisis_sr)):
                return None
            
            # 6. AJUSTAR POR SESIÓN
            ajuste_sesion = self.gestor_sesiones.ajustar_estrategia_por_sesion(par)
            
            # 7. CALCULAR NIVELES CON VOLATILIDAD
            datos_ohlc = self.obtener_datos_ohlc_recientes(par)
            if datos_ohlc:
                # Ajustar SL/TP por volatilidad
                if direccion == "COMPRA":
                    sl_base = precio * (1 - params['sl'])
                    tp_base = precio * (1 + params['tp_niveles'][0])
                    
                    sl_ajustado = self.gestor_volatilidad.ajustar_stop_loss_por_volatilidad(
                        par, sl_base, datos_ohlc
                    )
                    tp_ajustado = self.gestor_volatilidad.ajustar_take_profit_por_volatilidad(
                        par, tp_base, datos_ohlc
                    )
                    
                    dca_1 = precio * (1 - params['dca_niveles'][0])
                    dca_2 = precio * (1 - params['dca_niveles'][1])
                else:
                    sl_base = precio * (1 + params['sl'])
                    tp_base = precio * (1 - params['tp_niveles'][0])
                    
                    sl_ajustado = self.gestor_volatilidad.ajustar_stop_loss_por_volatilidad(
                        par, sl_base, datos_ohlc
                    )
                    tp_ajustado = self.gestor_volatilidad.ajustar_take_profit_por_volatilidad(
                        par, tp_base, datos_ohlc
                    )
                    
                    dca_1 = precio * (1 + params['dca_niveles'][0])
                    dca_2 = precio * (1 + params['dca_niveles'][1])
            else:
                # Fallback sin datos OHLC
                if direccion == "COMPRA":
                    sl_ajustado = precio * (1 - params['sl'])
                    tp_ajustado = precio * (1 + params['tp_niveles'][0])
                    dca_1 = precio * (1 - params['dca_niveles'][0])
                    dca_2 = precio * (1 - params['dca_niveles'][1])
                else:
                    sl_ajustado = precio * (1 + params['sl'])
                    tp_ajustado = precio * (1 - params['tp_niveles'][0])
                    dca_1 = precio * (1 + params['dca_niveles'][0])
                    dca_2 = precio * (1 + params['dca_niveles'][1])
            
            # 8. CONFIRMAR SEÑAL
            confianza = analisis_sr['confianza']
            sesion_actual, _ = self.gestor_sesiones.obtener_sesion_actual()
            
            print(f"🎯 SEÑAL MEJORADA: {par} {direccion} - Sesión: {sesion_actual} - Confianza: {confianza}")
            
            return {
                'par': par,
                'direccion': direccion,
                'precio_actual': round(precio, 5),
                'tp1': round(tp_ajustado, 5),
                'tp2': round(tp_ajustado * 1.1, 5),  # TP2 un 10% más
                'sl': round(sl_ajustado, 5),
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
                'estrategia': 'S/R Mejorada',
                'niveles_sr': analisis_sr['niveles_sr'],
                'zona_actual': analisis_sr['zona_actual'],
                'motivo_señal': analisis_sr['motivo'],
                'sesion_mercado': sesion_actual,
                'ajuste_sesion': ajuste_sesion
            }
            
        except Exception as e:
            print(f"❌ Error en generar_señal_mejorada: {e}")
            return None
    
    def obtener_datos_tecnicos_reales(self, par):
        """Obtener datos técnicos REALES"""
        try:
            indicadores = self._get_indicadores_reales()
            if indicadores:
                datos = indicadores.obtener_indicadores_reales(par)
                if datos and datos['precio_actual']:
                    return datos
            
            yahoo = self._get_yahoo()
            if yahoo:
                return yahoo.obtener_datos_tecnicos(par)
            else:
                return self._datos_tecnicos_simulados(par)
                
        except Exception as e:
            print(f"❌ Error obteniendo datos técnicos reales: {e}")
            return self._datos_tecnicos_simulados(par)
    
    def obtener_datos_ohlc_recientes(self, par):
        """Obtener datos OHLC recientes para análisis de volatilidad"""
        try:
            yahoo = self._get_yahoo()
            if yahoo:
                return yahoo.obtener_datos_historicos_ohlc(par, "5d", "1h")
            return None
        except:
            return None
    
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
