# estrategia_dca_corregida.py - ESTRATEGIA CORREGIDA CON PRECIOS CENTRALIZADOS
import random
from datetime import datetime

class EstrategiaDCACorregida:
    def __init__(self, central_precios):
        self.central_precios = central_precios
        self.operaciones_activas = {}
        
        # Módulos auxiliares
        self.gestor_sesiones = GestorSesionesMercado()
        self.analizador_correlaciones = AnalizadorCorrelaciones()
        self.gestor_volatilidad = GestorVolatilidad()
        
        # Módulos de análisis (lazy loading)
        self.analisis_sr = None
        self.indicadores_reales = None
    
    def generar_señal_con_precio(self, par, precio_actual, operaciones_activas=[]):
        """
        Generar señal usando precio proporcionado (de la central)
        """
        try:
            from config import PARAMETROS_POR_PAR
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['EURUSD'])
            
            # 1. VERIFICAR HORARIO
            if not self.gestor_sesiones.es_horario_optimo_trading():
                return None
            
            # 2. VERIFICAR CORRELACIONES
            if operaciones_activas:
                evitar, motivo = self.analizador_correlaciones.deberia_evitar_señal(
                    {'par': par, 'direccion': 'COMPRA'}, operaciones_activas
                )
                if evitar:
                    return None
            
            # 3. OBTENER DATOS TÉCNICOS (USANDO PRECIO ACTUAL)
            datos_reales = self.obtener_datos_tecnicos_con_precio(par, precio_actual)
            if not datos_reales:
                return None
            
            rsi = datos_reales['rsi']
            tendencia = datos_reales['tendencia']
            
            # 4. ANÁLISIS S/R
            analisis_sr_obj = self._get_analisis_sr()
            if not analisis_sr_obj:
                return None
                
            analisis_sr = analisis_sr_obj.analizar_estructura_mercado(par, precio_actual, tendencia, rsi)
            
            if not analisis_sr['señal']:
                return None
            
            # 5. VERIFICAR CONDICIONES ÓPTIMAS
            direccion = analisis_sr['señal']
            if (direccion == "COMPRA" and 
                not analisis_sr_obj.es_zona_compra_optima(analisis_sr)):
                return None
                
            if (direccion == "VENTA" and 
                not analisis_sr_obj.es_zona_venta_optima(analisis_sr)):
                return None
            
            # 6. CALCULAR NIVELES OPERACIÓN
            niveles = self.calcular_niveles_operacion(direccion, precio_actual, params)
            
            return {
                'par': par,
                'direccion': direccion,
                'precio_actual': precio_actual,  # USANDO PRECIO PROPORCIONADO
                'tp1': niveles['tp1'],
                'tp2': niveles['tp2'],
                'sl': niveles['sl'],
                'dca_1': niveles['dca_1'],
                'dca_2': niveles['dca_2'],
                'rsi': rsi,
                'tendencia': tendencia,
                'winrate_esperado': params['winrate'],
                'rentabilidad_esperada': params['rentabilidad'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'fuente_datos': 'Central Precios',
                'leverage': params['leverage'],
                'confianza': analisis_sr['confianza'],
                'estrategia': 'S/R Corregida',
                'niveles_sr': analisis_sr['niveles_sr'],
                'zona_actual': analisis_sr['zona_actual'],
                'motivo_señal': analisis_sr['motivo'],
                'sesion_mercado': self.gestor_sesiones.obtener_sesion_actual()[0]
            }
            
        except Exception as e:
            print(f"❌ Error en generar_señal_con_precio: {e}")
            return None
    
    def calcular_niveles_operacion(self, direccion, precio_actual, params):
        """Calcular niveles de operación usando precio proporcionado"""
        if direccion == "COMPRA":
            tp1 = precio_actual * (1 + params['tp_niveles'][0])
            tp2 = precio_actual * (1 + params['tp_niveles'][1])
            sl = precio_actual * (1 - params['sl'])
            dca_1 = precio_actual * (1 - params['dca_niveles'][0])
            dca_2 = precio_actual * (1 - params['dca_niveles'][1])
        else:
            tp1 = precio_actual * (1 - params['tp_niveles'][0])
            tp2 = precio_actual * (1 - params['tp_niveles'][1])
            sl = precio_actual * (1 + params['sl'])
            dca_1 = precio_actual * (1 + params['dca_niveles'][0])
            dca_2 = precio_actual * (1 + params['dca_niveles'][1])
        
        return {
            'tp1': round(tp1, 5),
            'tp2': round(tp2, 5),
            'sl': round(sl, 5),
            'dca_1': round(dca_1, 5),
            'dca_2': round(dca_2, 5)
        }
    
    def obtener_datos_tecnicos_con_precio(self, par, precio_actual):
        """Obtener datos técnicos usando precio proporcionado"""
        try:
            indicadores = self._get_indicadores_reales()
            if indicadores:
                # Pasar el precio actual para evitar que lo obtengan de nuevo
                datos = indicadores.obtener_indicadores_con_precio(par, precio_actual)
                if datos:
                    return datos
            
            # Fallback básico
            return self._datos_tecnicos_basicos(precio_actual)
                
        except Exception as e:
            print(f"❌ Error obteniendo datos técnicos: {e}")
            return self._datos_tecnicos_basicos(precio_actual)
    
    def _datos_tecnicos_basicos(self, precio_actual):
        """Datos técnicos básicos usando precio proporcionado"""
        # Simulación básica - en producción usarías indicadores reales
        rsi = random.randint(30, 70)
        
        return {
            'precio_actual': precio_actual,
            'rsi': rsi,
            'tendencia': "ALCISTA" if rsi < 40 else "BAJISTA" if rsi > 60 else "LATERAL",
            'fuente': 'Cálculo Básico'
        }
    
    def _get_analisis_sr(self):
        if self.analisis_sr is None:
            try:
                from analisis_tecnico import AnalisisTechnicoSR
                self.analisis_sr = AnalisisTechnicoSR()
            except ImportError:
                return None
        return self.analisis_sr
    
    def _get_indicadores_reales(self):
        if self.indicadores_reales is None:
            try:
                from indicadores_reales import IndicadoresReales
                self.indicadores_reales = IndicadoresReales()
            except ImportError:
                return None
        return self.indicadores_reales

# También necesitas actualizar indicadores_reales.py para aceptar precio
