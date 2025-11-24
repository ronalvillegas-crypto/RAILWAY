# analisis_tecnico_corregido.py - CON DETECCIÓN REAL DE S/R MEJORADA
import numpy as np
import random
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AnalisisTechnicoSR:
    def __init__(self):
        self.niveles_sr_historicos = {}
        self.indicadores = IndicadoresReales()
        
    def detectar_niveles_sr(self, par, datos_precios):
        """Detectar niveles de Support/Resistance REALES"""
        return self.detectar_niveles_sr_reales(par)
        
    def detectar_niveles_sr_reales(self, par):
        """Detectar niveles S/R REALES basados en datos históricos - VERSIÓN MEJORADA"""
        try:
            # Obtener más datos históricos para mejor detección
            datos = self.indicadores.obtener_datos_historicos(par, "6mo", "4h")
            
            if not datos or len(datos['close']) < 50:
                logger.warning(f"⚠️ Datos insuficientes para S/R real de {par}")
                return self._niveles_sr_base(par)
            
            highs = np.array([h for h in datos['high'] if h is not None])
            lows = np.array([l for l in datos['low'] if l is not None])
            closes = np.array([c for c in datos['close'] if c is not None])
            
            if len(highs) < 50 or len(lows) < 50:
                return self._niveles_sr_base(par)
            
            # PRECIO ACTUAL para contexto
            precio_actual = closes[-1] if len(closes) > 0 else self._get_precio_actual(par)
            
            # 🎯 DETECCIÓN MEJORADA DE S/R CON MÚLTIPLOS MÉTODOS
            
            # 1. PIVOTS HIGH/LOW (Método principal)
            resistances_pivots = self._detectar_pivots_mejorado(highs, window=7, is_high=True)
            supports_pivots = self._detectar_pivots_mejorado(lows, window=7, is_high=False)
            
            # 2. MÁXIMOS/MÍNIMOS RECIENTES (últimas 50 velas)
            resistances_recent = self._detectar_maximos_recientes(highs, window=50)
            supports_recent = self._detectar_minimos_recientes(lows, window=50)
            
            # 3. NIVELES PSICOLÓGICOS
            niveles_psicologicos = self._detectar_niveles_psicologicos(precio_actual, par)
            
            # COMBINAR TODOS LOS MÉTODOS
            todas_resistances = list(set(resistances_pivots + resistances_recent + niveles_psicologicos['resistance']))
            todas_supports = list(set(supports_pivots + supports_recent + niveles_psicologicos['support']))
            
            # FILTRAR Y ORDENAR NIVELES RELEVANTES
            resistances_relevantes = self._filtrar_niveles_relevantes(todas_resistances, precio_actual, "RESISTANCE")
            supports_relevantes = self._filtrar_niveles_relevantes(todas_supports, precio_actual, "SUPPORT")
            
            niveles = {
                'support': supports_relevantes[:3],  # Top 3 supports
                'resistance': resistances_relevantes[:3]  # Top 3 resistances
            }
            
            logger.info(f"🏔️ {par} - S/R DETECTADOS: Support {[round(s, 4) for s in niveles['support']]}, Resistance {[round(r, 4) for r in niveles['resistance']]}")
            
            # Guardar en histórico
            self.niveles_sr_historicos[par] = {
                'niveles': niveles,
                'timestamp': datetime.now(),
                'precio_actual': precio_actual
            }
            
            return niveles
            
        except Exception as e:
            logger.error(f"❌ Error detectando S/R reales {par}: {e}")
            return self._niveles_sr_base(par)
    
    def _detectar_pivots_mejorado(self, prices, window=7, is_high=True):
        """Detección MEJORADA de puntos pivote"""
        try:
            if len(prices) < window * 2 + 1:
                return []
            
            pivots = []
            
            for i in range(window, len(prices) - window):
                if prices[i] is None:
                    continue
                    
                # Ventana izquierda y derecha
                left_window = prices[i-window:i]
                right_window = prices[i+1:i+window+1]
                
                # Filtrar valores None
                left_window = [p for p in left_window if p is not None]
                right_window = [p for p in right_window if p is not None]
                
                if not left_window or not right_window:
                    continue
                
                if is_high:
                    # Pivot high: mayor que izquierda Y derecha
                    if (prices[i] > max(left_window) and 
                        prices[i] > max(right_window)):
                        pivots.append(prices[i])
                else:
                    # Pivot low: menor que izquierda Y derecha  
                    if (prices[i] < min(left_window) and 
                        prices[i] < min(right_window)):
                        pivots.append(prices[i])
            
            # Eliminar duplicados cercanos con tolerancia dinámica
            if pivots:
                avg_price = np.mean(prices)
                tolerance = avg_price * 0.003  # 0.3% de tolerancia
                
                pivots_unicos = []
                for pivot in sorted(pivots):
                    if not pivots_unicos or abs(pivot - pivots_unicos[-1]) > tolerance:
                        pivots_unicos.append(pivot)
                
                return pivots_unicos
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error en detección pivotes: {e}")
            return []
    
    def _detectar_maximos_recientes(self, highs, window=50):
        """Detectar máximos recientes significativos"""
        try:
            if len(highs) < window:
                return []
            
            recent_highs = highs[-window:]
            # Tomar los 3 máximos más altos
            max_highs = sorted(recent_highs, reverse=True)[:3]
            return max_highs
            
        except Exception as e:
            logger.error(f"❌ Error detectando máximos: {e}")
            return []
    
    def _detectar_minimos_recientes(self, lows, window=50):
        """Detectar mínimos recientes significativos"""
        try:
            if len(lows) < window:
                return []
            
            recent_lows = lows[-window:]
            # Tomar los 3 mínimos más bajos
            min_lows = sorted(recent_lows)[:3]
            return min_lows
            
        except Exception as e:
            logger.error(f"❌ Error detectando mínimos: {e}")
            return []
    
    def _detectar_niveles_psicologicos(self, precio_actual, par):
        """Detectar niveles psicológicos basados en el precio actual"""
        try:
            # Determinar el paso según el tipo de par
            if par in ["XAUUSD", "XAGUSD", "XPTUSD"]:
                # Metales: múltiplos de 10, 50, 100
                step = 10.0 if precio_actual > 1000 else 5.0
            elif par in ["OILUSD", "NGASUSD"]:
                # Energía: múltiplos de 1, 5
                step = 5.0 if precio_actual > 50 else 1.0
            elif any(indice in par for indice in ["SPX", "NAS", "DJI"]):
                # Índices: múltiplos de 100, 500
                step = 500.0 if precio_actual > 10000 else 100.0
            else:
                # Forex: múltiplos de 0.0100, 0.0050
                step = 0.0100 if precio_actual > 1.0 else 0.0050
            
            # Calcular niveles psicológicos cercanos
            base_level = round(precio_actual / step) * step
            supports_psych = [base_level - step, base_level - (2 * step)]
            resistances_psych = [base_level + step, base_level + (2 * step)]
            
            return {
                'support': [s for s in supports_psych if s > 0],
                'resistance': resistances_psych
            }
            
        except Exception as e:
            logger.error(f"❌ Error niveles psicológicos: {e}")
            return {'support': [], 'resistance': []}
    
    def _filtrar_niveles_relevantes(self, niveles, precio_actual, tipo):
        """Filtrar niveles relevantes basados en proximidad al precio actual"""
        try:
            if not niveles:
                return []
            
            # Calcular distancias
            niveles_con_distancia = []
            for nivel in niveles:
                if nivel and nivel > 0:
                    distancia = abs((nivel - precio_actual) / precio_actual) * 100
                    niveles_con_distancia.append((nivel, distancia))
            
            # Filtrar por distancia máxima según tipo
            if tipo == "SUPPORT":
                # Supports: solo niveles por debajo del precio actual
                niveles_filtrados = [n for n, d in niveles_con_distancia 
                                   if n < precio_actual and d < 5.0]  # Máximo 5% de distancia
            else:  # RESISTANCE
                # Resistances: solo niveles por encima del precio actual  
                niveles_filtrados = [n for n, d in niveles_con_distancia 
                                   if n > precio_actual and d < 5.0]
            
            # Ordenar por proximidad al precio actual
            if tipo == "SUPPORT":
                niveles_filtrados.sort(reverse=True)  # Supports más altos primero
            else:
                niveles_filtrados.sort()  # Resistances más bajos primero
            
            return niveles_filtrados[:3]  # Top 3 más relevantes
            
        except Exception as e:
            logger.error(f"❌ Error filtrando niveles: {e}")
            return []
    
    def _get_precio_actual(self, par):
        """Obtener precio actual como fallback"""
        try:
            from yahoo_api_mejorado import YahooFinanceAPI
            yahoo = YahooFinanceAPI()
            return yahoo.obtener_precio_redundante(par) or 1.0
        except:
            return 1.0
    
    def _niveles_sr_base(self, par):
        """Niveles base como fallback - ACTUALIZADOS"""
        niveles_base = {
            'EURUSD': {'support': [1.0780, 1.0820, 1.0750], 'resistance': [1.0920, 1.0950, 1.0980]},
            'USDCAD': {'support': [1.3380, 1.3420, 1.3350], 'resistance': [1.3520, 1.3560, 1.3590]},
            'EURCHF': {'support': [0.9480, 0.9520, 0.9450], 'resistance': [0.9620, 0.9660, 0.9690]},
            'EURAUD': {'support': [1.6280, 1.6320, 1.6250], 'resistance': [1.6450, 1.6480, 1.6520]},
            'GBPUSD': {'support': [1.2600, 1.2550, 1.2500], 'resistance': [1.2750, 1.2800, 1.2850]},
            'USDJPY': {'support': [147.50, 148.00, 146.80], 'resistance': [149.50, 150.00, 150.50]},
            'XAUUSD': {'support': [2170, 2180, 2160], 'resistance': [2200, 2210, 2220]},
            'XAGUSD': {'support': [24.50, 24.70, 24.30], 'resistance': [25.00, 25.20, 25.50]},
            'OILUSD': {'support': [77.0, 77.5, 76.5], 'resistance': [79.0, 79.5, 80.0]},
            'SPX500': {'support': [5150, 5170, 5120], 'resistance': [5220, 5250, 5280]},
        }
        return niveles_base.get(par, {'support': [1.0000, 0.9950], 'resistance': [1.0100, 1.0150]})
    
    def analizar_estructura_mercado(self, par, precio_actual, tendencia, rsi):
        """Análisis completo de estructura de mercado S/R - VERSIÓN MEJORADA"""
        try:
            # Obtener niveles S/R REALES
            niveles_sr = self.detectar_niveles_sr_reales(par)
            
            if not niveles_sr:
                logger.warning(f"⚠️ No se pudieron obtener niveles S/R para {par}")
                return self._analisis_fallback(par, precio_actual, rsi)
            
            # Determinar proximidad a niveles clave
            distancias_support = [abs(precio_actual - s) for s in niveles_sr['support'] if s and s > 0]
            distancias_resistance = [abs(precio_actual - r) for r in niveles_sr['resistance'] if r and r > 0]
            
            if not distancias_support or not distancias_resistance:
                return self._analisis_fallback(par, precio_actual, rsi)
            
            distancia_support = min(distancias_support)
            distancia_resistance = min(distancias_resistance)
            
            # Determinar umbral según tipo de activo
            if par in ['XAUUSD', 'XAGUSD', 'XPTUSD']:  # Metales
                umbral_proximidad = precio_actual * 0.008  # 0.8%
            elif par in ['OILUSD', 'NGASUSD']:  # Energía
                umbral_proximidad = precio_actual * 0.012  # 1.2%
            elif any(indice in par for indice in ['SPX', 'NAS', 'DJI']):  # Índices
                umbral_proximidad = precio_actual * 0.015  # 1.5%
            else:  # Forex
                umbral_proximidad = precio_actual * 0.004  # 0.4%
            
            # 🎯 ESTRATEGIA S/R MEJORADA - CONDICIONES MÁS ESTRICTAS
            
            # Zona actual
            if distancia_support < distancia_resistance:
                zona_actual = "SUPPORT"
                nivel_cercano = min(niveles_sr['support'], key=lambda x: abs(x - precio_actual))
            else:
                zona_actual = "RESISTANCE" 
                nivel_cercano = min(niveles_sr['resistance'], key=lambda x: abs(x - precio_actual))
            
            # CONDICIONES COMPRA (en support)
            condiciones_compra_alta = (
                zona_actual == "SUPPORT" and
                distancia_support < umbral_proximidad and  # Cerca de support
                rsi < 35 and                              # RSI oversold
                tendencia in ["ALCISTA", "LATERAL"] and   # Tendencia favorable
                precio_actual > nivel_cercano * 0.998     # No demasiado por debajo del support
            )
            
            condiciones_compra_media = (
                zona_actual == "SUPPORT" and
                distancia_support < umbral_proximidad * 1.5 and  # Cerca de support
                rsi < 40 and                                    # RSI cercano a oversold
                tendencia != "BAJISTA"                         # No en tendencia bajista fuerte
            )
            
            # CONDICIONES VENTA (en resistance)  
            condiciones_venta_alta = (
                zona_actual == "RESISTANCE" and
                distancia_resistance < umbral_proximidad and  # Cerca de resistance
                rsi > 65 and                                 # RSI overbought
                tendencia in ["BAJISTA", "LATERAL"] and      # Tendencia favorable
                precio_actual < nivel_cercano * 1.002        # No demasiado por encima de resistance
            )
            
            condiciones_venta_media = (
                zona_actual == "RESISTANCE" and
                distancia_resistance < umbral_proximidad * 1.5 and  # Cerca de resistance
                rsi > 60 and                                       # RSI cercano a overbought
                tendencia != "ALCISTA"                            # No en tendencia alcista fuerte
            )
            
            # DETERMINAR SEÑAL Y CONFIANZA
            señal = None
            confianza = "BAJA"
            motivo = f"⚡ {par} - Fuera de zonas S/R clave"
            
            if condiciones_compra_alta:
                señal = "COMPRA"
                confianza = "ALTA"
                motivo = f"🎯 REBOTE S/R: {par} en Support + RSI Oversold + Tendencia Favorable"
            elif condiciones_venta_alta:
                señal = "VENTA" 
                confianza = "ALTA"
                motivo = f"🎯 RECHAZO S/R: {par} en Resistance + RSI Overbought + Tendencia Favorable"
            elif condiciones_compra_media:
                señal = "COMPRA"
                confianza = "MEDIA"
                motivo = f"📊 {par} cerca de Support + RSI Cercano a Oversold"
            elif condiciones_venta_media:
                señal = "VENTA"
                confianza = "MEDIA" 
                motivo = f"📊 {par} cerca de Resistance + RSI Cercano a Overbought"
            
            logger.info(f"🔍 Análisis S/R {par}: Señal={señal}, Confianza={confianza}, Zona={zona_actual}")
            
            return {
                'señal': señal,
                'confianza': confianza,
                'motivo': motivo,
                'niveles_sr': niveles_sr,
                'distancia_support': round(distancia_support, 5),
                'distancia_resistance': round(distancia_resistance, 5),
                'zona_actual': zona_actual,
                'nivel_cercano': round(nivel_cercano, 5),
                'umbral_proximidad': round(umbral_proximidad, 5)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en análisis estructura mercado {par}: {e}")
            return self._analisis_fallback(par, precio_actual, rsi)
    
    def _analisis_fallback(self, par, precio_actual, rsi):
        """Análisis fallback cuando falla la detección S/R"""
        # Fallback basado solo en RSI (como antes)
        if rsi < 35:
            señal = "COMPRA"
            confianza = "MEDIA"
            motivo = f"📊 {par} - RSI Oversold (fallback)"
        elif rsi > 65:
            señal = "VENTA"
            confianza = "MEDIA" 
            motivo = f"📊 {par} - RSI Overbought (fallback)"
        else:
            señal = None
            confianza = "BAJA"
            motivo = f"⚡ {par} - Condiciones no óptimas (fallback)"
        
        return {
            'señal': señal,
            'confianza': confianza,
            'motivo': motivo,
            'niveles_sr': self._niveles_sr_base(par),
            'distancia_support': 0.0,
            'distancia_resistance': 0.0,
            'zona_actual': "NEUTRAL"
        }
    
    def es_zona_compra_optima(self, analisis):
        """Verificar si es zona de compra óptima según S/R"""
        return (analisis['señal'] == "COMPRA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "SUPPORT")
    
    def es_zona_venta_optima(self, analisis):
        """Verificar si es zona de venta óptima según S/R"""
        return (analisis['señal'] == "VENTA" and 
                analisis['confianza'] in ["ALTA", "MEDIA"] and
                analisis['zona_actual'] == "RESISTANCE")
