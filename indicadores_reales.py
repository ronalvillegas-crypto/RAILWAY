# indicadores_reales.py - CÁLCULO REAL DE INDICADORES CON PRECIO CENTRALIZADO
import requests
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class IndicadoresReales:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.cache_datos = {}
        self.cache_ttl = 300  # 5 minutos de cache para datos históricos
        
        logger.info("✅ IndicadoresReales inicializado")

    def obtener_datos_historicos(self, simbolo, periodo="1mo", intervalo="1h"):
        """Obtener datos históricos REALES de Yahoo Finance con cache"""
        try:
            # Verificar cache primero
            cache_key = f"{simbolo}_{periodo}_{intervalo}"
            ahora = datetime.now()
            
            if cache_key in self.cache_datos:
                datos, timestamp = self.cache_datos[cache_key]
                if (ahora - timestamp).total_seconds() < self.cache_ttl:
                    logger.debug(f"📊 Datos desde cache: {simbolo}")
                    return datos

            symbol_mapping = {
                "EURUSD": "EURUSD=X", "USDCAD": "CAD=X", "EURCHF": "EURCHF=X", "EURAUD": "EURAUD=X",
                "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "NZDUSD": "NZDUSD=X",
                "USDCHF": "CHF=X", "GBPJPY": "GBPJPY=X", "XAUUSD": "GC=F", "XAGUSD": "SI=F", 
                "OILUSD": "CL=F", "XPTUSD": "PL=F", "XPDUSD": "PA=F", "NGASUSD": "NG=F", 
                "COPPER": "HG=F", "SPX500": "^GSPC", "NAS100": "^IXIC", "DJI30": "^DJI",
                "GER40": "^GDAXI", "UK100": "^FTSE", "JPN225": "^N225"
            }
            
            yahoo_symbol = symbol_mapping.get(simbolo)
            if not yahoo_symbol:
                logger.warning(f"⚠️ Símbolo no mapeado: {simbolo}")
                return None
            
            url = f"{self.base_url}/{yahoo_symbol}"
            params = {
                'range': periodo,
                'interval': intervalo
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    timestamps = result.get('timestamp', [])
                    prices = result.get('indicators', {}).get('quote', [{}])[0]
                    
                    # Extraer precios y limpiar None values
                    closes = [c for c in prices.get('close', []) if c is not None]
                    highs = [h for h in prices.get('high', []) if h is not None]
                    lows = [l for l in prices.get('low', []) if l is not None]
                    opens = [o for o in prices.get('open', []) if o is not None]
                    
                    datos = {
                        'timestamp': timestamps,
                        'close': closes,
                        'high': highs,
                        'low': lows,
                        'open': opens
                    }
                    
                    # Guardar en cache
                    self.cache_datos[cache_key] = (datos, ahora)
                    logger.info(f"✅ Datos históricos obtenidos: {simbolo} - {len(closes)} registros")
                    return datos
                else:
                    logger.warning(f"⚠️ Sin datos en respuesta Yahoo para {simbolo}")
            else:
                logger.warning(f"⚠️ Error HTTP {response.status_code} para {simbolo}")
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Error datos históricos {simbolo}: {e}")
            return None

    def obtener_indicadores_reales(self, simbolo):
        """Obtener todos los indicadores REALES (método tradicional)"""
        try:
            # Obtener datos históricos (último mes, 1h timeframe)
            datos = self.obtener_datos_historicos(simbolo, "1mo", "1h")
            
            if not datos or len(datos['close']) < 20:
                logger.warning(f"⚠️ Datos insuficientes para {simbolo}, usando cálculo básico")
                return self._indicadores_basicos(simbolo)
            
            precios_cierre = datos['close']
            
            if len(precios_cierre) < 20:
                return self._indicadores_basicos(simbolo)
            
            # Calcular indicadores REALES
            precio_actual = precios_cierre[-1]
            rsi_real = self.calcular_rsi_real(precios_cierre)
            tendencia_real = self.determinar_tendencia(precios_cierre)
            bandas_bollinger = self.calcular_bandas_bollinger(precios_cierre)
            
            logger.info(f"📊 {simbolo} - RSI: {rsi_real}, Tendencia: {tendencia_real}")
            
            return {
                'precio_actual': precio_actual,
                'rsi': rsi_real,
                'tendencia': tendencia_real,
                'bandas_bollinger': bandas_bollinger,
                'fuente': 'Cálculo Real'
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando indicadores reales {simbolo}: {e}")
            return self._indicadores_basicos(simbolo)

    def obtener_indicadores_con_precio(self, simbolo, precio_actual):
        """
        Obtener indicadores usando precio proporcionado (para central de precios)
        
        Args:
            simbolo (str): Símbolo del par
            precio_actual (float): Precio actual proporcionado
            
        Returns:
            dict: Indicadores técnicos
        """
        try:
            # Obtener datos históricos
            datos = self.obtener_datos_historicos(simbolo, "1mo", "1h")
            
            if datos and len(datos['close']) > 0:
                # Actualizar el último precio con el actual proporcionado
                datos['close'][-1] = precio_actual
                
                precios_cierre = datos['close']
                
                if len(precios_cierre) >= 14:  # Mínimo para RSI
                    rsi_real = self.calcular_rsi_real(precios_cierre)
                    tendencia_real = self.determinar_tendencia(precios_cierre)
                    bandas_bollinger = self.calcular_bandas_bollinger(precios_cierre)
                    
                    logger.debug(f"📊 Indicadores con precio proporcionado: {simbolo} - RSI: {rsi_real}")
                    
                    return {
                        'precio_actual': precio_actual,
                        'rsi': rsi_real,
                        'tendencia': tendencia_real,
                        'bandas_bollinger': bandas_bollinger,
                        'fuente': 'Cálculo Real con Precio Actual'
                    }
            
            # Fallback a cálculo básico con precio proporcionado
            return self._indicadores_basicos_con_precio(simbolo, precio_actual)
            
        except Exception as e:
            logger.error(f"❌ Error indicadores con precio {simbolo}: {e}")
            return self._indicadores_basicos_con_precio(simbolo, precio_actual)

    def calcular_rsi_real(self, precios, periodo=14):
        """Calcular RSI REAL con fórmula estándar"""
        try:
            if len(precios) < periodo + 1:
                return 50  # Valor neutral si no hay suficientes datos
            
            # Convertir a numpy array para mejor manejo
            precios_array = np.array(precios)
            
            # Calcular cambios de precio
            deltas = np.diff(precios_array)
            
            # Separar ganancias y pérdidas
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            # Calcular promedio de ganancias/pérdidas (primer promedio)
            avg_gains = []
            avg_losses = []
            
            # Primer promedio simple
            avg_gain = np.mean(gains[:periodo])
            avg_loss = np.mean(losses[:periodo])
            
            avg_gains.append(avg_gain)
            avg_losses.append(avg_loss)
            
            # Calcular promedios sucesivos con suavizado
            for i in range(periodo, len(gains)):
                avg_gain = (avg_gains[-1] * (periodo - 1) + gains[i]) / periodo
                avg_loss = (avg_losses[-1] * (periodo - 1) + losses[i]) / periodo
                avg_gains.append(avg_gain)
                avg_losses.append(avg_loss)
            
            if not avg_gains or not avg_losses:
                return 50
            
            # Calcular RSI para los últimos valores
            rs = avg_gains[-1] / avg_losses[-1] if avg_losses[-1] != 0 else float('inf')
            rsi = 100 - (100 / (1 + rs))
            
            # Limitar valores extremos
            rsi = max(0, min(100, rsi))
            
            return round(rsi, 2)
            
        except Exception as e:
            logger.error(f"❌ Error cálculo RSI: {e}")
            return 50

    def determinar_tendencia(self, precios, periodo_corto=10, periodo_largo=20):
        """Determinar tendencia REAL basada en medias móviles"""
        try:
            if len(precios) < periodo_largo:
                return "LATERAL"
            
            # Calcular medias móviles
            precios_array = np.array(precios)
            
            ma_rapida = np.mean(precios_array[-periodo_corto:])
            ma_lenta = np.mean(precios_array[-periodo_largo:])
            
            # Determinar tendencia con umbrales dinámicos
            diferencia_porcentual = (ma_rapida - ma_lenta) / ma_lenta * 100
            
            if diferencia_porcentual > 0.5:  # 0.5% de diferencia
                return "ALCISTA"
            elif diferencia_porcentual < -0.5:
                return "BAJISTA"
            else:
                return "LATERAL"
                
        except Exception as e:
            logger.error(f"❌ Error determinando tendencia: {e}")
            return "LATERAL"

    def calcular_bandas_bollinger(self, precios, periodo=20, desviaciones=2):
        """Calcular Bandas de Bollinger"""
        try:
            if len(precios) < periodo:
                return None
            
            precios_array = np.array(precios[-periodo:])
            
            # Calcular media móvil
            media = np.mean(precios_array)
            
            # Calcular desviación estándar
            desviacion = np.std(precios_array)
            
            # Calcular bandas
            banda_superior = media + (desviaciones * desviacion)
            banda_inferior = media - (desviaciones * desviacion)
            
            # Ancho de bandas (indicador de volatilidad)
            ancho_bandas = (banda_superior - banda_inferior) / media * 100
            
            # Posición actual relativa a las bandas
            precio_actual = precios_array[-1]
            posicion_bandas = (precio_actual - banda_inferior) / (banda_superior - banda_inferior) * 100
            
            return {
                'media': round(media, 5),
                'banda_superior': round(banda_superior, 5),
                'banda_inferior': round(banda_inferior, 5),
                'ancho_bandas': round(ancho_bandas, 2),
                'posicion_actual': round(posicion_bandas, 1),
                'desviacion': round(desviacion, 5)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando Bandas Bollinger: {e}")
            return None

    def calcular_media_movil(self, precios, periodo):
        """Calcular media móvil simple"""
        try:
            if len(precios) < periodo:
                return None
            return np.mean(precios[-periodo:])
        except Exception as e:
            logger.error(f"❌ Error calculando media móvil: {e}")
            return None

    def calcular_soporte_resistencia(self, datos_ohlc, window=20):
        """Calcular niveles de soporte y resistencia basados en máximos/mínimos recientes"""
        try:
            if not datos_ohlc or len(datos_ohlc['high']) < window:
                return None
            
            highs = datos_ohlc['high'][-window:]
            lows = datos_ohlc['low'][-window:]
            
            resistencia = max(highs)
            soporte = min(lows)
            
            return {
                'soporte': round(soporte, 5),
                'resistencia': round(resistencia, 5),
                'rango_trading': round(resistencia - soporte, 5)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando S/R: {e}")
            return None

    def _indicadores_basicos(self, simbolo):
        """Fallback a cálculo básico si falla el real"""
        try:
            from yahoo_api_mejorado import YahooFinanceAPI
            yahoo = YahooFinanceAPI()
            precio = yahoo.obtener_precio_redundante(simbolo)
            
            if not precio:
                return self._indicadores_simulados(simbolo)
            
            # Cálculo básico mejorado con precio real
            precios_base = {
                "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550, 
                "EURAUD": 1.6350, "XAUUSD": 2185.50, "XAGUSD": 24.85, 
                "OILUSD": 78.30, "XPTUSD": 925.80, "SPX500": 5200.0
            }
            
            precio_base = precios_base.get(simbolo, precio)
            
            # Calcular RSI basado en desviación del precio base
            desviacion = (precio - precio_base) / precio_base
            rsi = 50 + (desviacion * 25)  # Más conservador que antes
            rsi = max(15, min(85, rsi))  # Limitar valores extremos
            
            # Tendencia basada en RSI
            if rsi < 35:
                tendencia = "ALCISTA"
            elif rsi > 65:
                tendencia = "BAJISTA"
            else:
                tendencia = "LATERAL"
            
            logger.info(f"📊 {simbolo} - Indicadores básicos: RSI={rsi:.1f}")
            
            return {
                'precio_actual': precio,
                'rsi': round(rsi, 1),
                'tendencia': tendencia,
                'fuente': 'Cálculo Básico'
            }
            
        except Exception as e:
            logger.error(f"❌ Error en indicadores básicos {simbolo}: {e}")
            return self._indicadores_simulados(simbolo)

    def _indicadores_basicos_con_precio(self, simbolo, precio_actual):
        """Fallback con precio proporcionado"""
        try:
            # Cálculo básico usando el precio actual proporcionado
            precios_base = {
                "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550,
                "EURAUD": 1.6350, "XAUUSD": 2185.50, "XAGUSD": 24.85,
                "OILUSD": 78.30, "XPTUSD": 925.80, "SPX500": 5200.0,
                "NAS100": 18000.0, "DJI30": 39000.0, "GBPUSD": 1.2650
            }
            
            precio_base = precios_base.get(simbolo, precio_actual)
            
            # Calcular RSI basado en desviación del precio base
            if precio_base > 0:
                desviacion = (precio_actual - precio_base) / precio_base
                rsi = 50 + (desviacion * 20)  # Menos sensible para mayor estabilidad
                rsi = max(20, min(80, rsi))  # Rangos más conservadores
            else:
                rsi = 50
            
            # Tendencia basada en RSI con histeresis
            if rsi < 32:
                tendencia = "ALCISTA"
            elif rsi > 68:
                tendencia = "BAJISTA"
            else:
                tendencia = "LATERAL"
            
            logger.debug(f"📊 {simbolo} - Básico con precio: RSI={rsi:.1f}, Precio={precio_actual:.5f}")
            
            return {
                'precio_actual': precio_actual,
                'rsi': round(rsi, 1),
                'tendencia': tendencia,
                'fuente': 'Cálculo Básico con Precio Actual'
            }
            
        except Exception as e:
            logger.error(f"❌ Error en básico con precio {simbolo}: {e}")
            return self._indicadores_simulados_con_precio(simbolo, precio_actual)

    def _indicadores_simulados(self, simbolo):
        """Indicadores simulados como último recurso"""
        import random
        
        precios_base = {
            "EURUSD": 1.0850, "USDCAD": 1.3450, "EURCHF": 0.9550,
            "EURAUD": 1.6350, "XAUUSD": 2185.50, "XAGUSD": 24.85,
            "OILUSD": 78.30, "XPTUSD": 925.80, "SPX500": 5200.0
        }
        
        precio_base = precios_base.get(simbolo, 1.0000)
        precio_actual = round(precio_base * (1 + random.uniform(-0.002, 0.002)), 5)
        rsi = random.randint(30, 70)
        
        return {
            'precio_actual': precio_actual,
            'rsi': rsi,
            'tendencia': "ALCISTA" if rsi < 40 else "BAJISTA" if rsi > 60 else "LATERAL",
            'fuente': 'Simulación'
        }

    def _indicadores_simulados_con_precio(self, simbolo, precio_actual):
        """Indicadores simulados con precio proporcionado"""
        import random
        
        rsi = random.randint(30, 70)
        
        return {
            'precio_actual': precio_actual,
            'rsi': rsi,
            'tendencia': "ALCISTA" if rsi < 40 else "BAJISTA" if rsi > 60 else "LATERAL",
            'fuente': 'Simulación con Precio Actual'
        }

    def limpiar_cache(self):
        """Limpiar cache de datos históricos"""
        self.cache_datos = {}
        logger.info("🧹 Cache de indicadores limpiado")

    def obtener_estadisticas_cache(self):
        """Obtener estadísticas del cache"""
        return {
            'items_en_cache': len(self.cache_datos),
            'cache_ttl_segundos': self.cache_ttl
        }

# Instancia global para uso fácil
indicadores_reales = IndicadoresReales()
