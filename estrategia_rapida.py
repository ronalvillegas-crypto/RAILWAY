# estrategia_rapida.py - ESTRATEGIA RÁPIDA + DETECCIÓN MOVIMIENTOS (IMPORT CORREGIDO)
import random
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EstrategiaRapida:
    def __init__(self):
        self.historial_precios = {}
        self.ultimas_señales = {}
        
        # 📊 UMBRALES DE MOVIMIENTO SIGNIFICATIVO POR TIPO
        self.umbrales_movimiento = {
            # FOREX - Movimientos ≥ 0.4%
            'forex': 0.0040,
            # MATERIAS PRIMAS - Movimientos ≥ 1.0%  
            'commodity': 0.0100,
            # ACCIONES - Movimientos ≥ 0.6%
            'indice': 0.0060
        }
    
    def generar_señal_eficiente(self, par):
        """Estrategia principal que combina momentum + movimientos significativos"""
        try:
            # ✅ IMPORT CORREGIDO - SIN "from yahoo_api import YahooFinanceAPI"
            from yahoo_api import YahooFinanceAPI
            from config import PARAMETROS_POR_PAR
            
            yahoo = YahooFinanceAPI()
            
            # 1. OBTENER PRECIO ACTUAL
            precio_actual = yahoo.obtener_precio_real(par)
            if not precio_actual:
                logger.warning(f"⚠️ No se pudo obtener precio para {par}")
                return None
            
            # 2. INICIALIZAR HISTORIAL
            if par not in self.historial_precios:
                self.historial_precios[par] = {
                    'precios': [],
                    'timestamp': [],
                    'volatilidad': 0.0
                }
            
            historial = self.historial_precios[par]
            historial['precios'].append(precio_actual)
            historial['timestamp'].append(datetime.now())
            
            # Mantener máximo 100 precios
            if len(historial['precios']) > 100:
                historial['precios'].pop(0)
                historial['timestamp'].pop(0)
            
            # 3. ESTRATEGIA 1: MOMENTUM CON MEDIAS MÓVILES
            señal_momentum = self._analizar_momentum(par, precio_actual, historial)
            
            # 4. ESTRATEGIA 2: DETECCIÓN MOVIMIENTOS SIGNIFICATIVOS
            señal_movimiento = self._detectar_movimiento_significativo(par, precio_actual, historial)
            
            # 5. PRIORIZAR SEÑALES
            if señal_movimiento:
                logger.info(f"🎯 MOVIMIENTO DETECTADO: {par} {señal_movimiento['direccion']} - {señal_movimiento['movimiento_porcentual']:.2f}%")
                return señal_movimiento
            elif señal_momentum:
                logger.info(f"📊 SEÑAL MOMENTUM: {par} {señal_momentum['direccion']}")
                return señal_momentum
            
            return None
            
        except ImportError as e:
            logger.error(f"❌ Error de importación en estrategia rápida: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error estrategia rápida {par}: {e}")
            return None
    
    def _analizar_momentum(self, par, precio_actual, historial):
        """Estrategia de momentum con medias móviles"""
        precios = historial['precios']
        
        if len(precios) < 15:
            return None  # Necesitamos al menos 15 precios
        
        # Calcular medias móviles
        media_rapida = sum(precios[-5:]) / 5    # 5 periodos
        media_lenta = sum(precios[-15:]) / 15   # 15 periodos
        
        # Calcular RSI
        rsi = self._calcular_rsi_avanzado(precios)
        
        # 🎯 CONDICIONES COMPRA MOMENTUM
        if (media_rapida > media_lenta and     # Tendencia alcista
            rsi < 35 and                       # No sobrecomprado
            precio_actual > media_rapida and   # Precio sobre media rápida
            len(precios) >= 20):               # Suficiente historia
            
            return self._crear_señal_momentum(par, precio_actual, 'COMPRA', rsi)
        
        # 🎯 CONDICIONES VENTA MOMENTUM  
        elif (media_rapida < media_lenta and   # Tendencia bajista
              rsi > 65 and                     # No sobrevendido
              precio_actual < media_rapida and # Precio bajo media rápida
              len(precios) >= 20):
            
            return self._crear_señal_momentum(par, precio_actual, 'VENTA', rsi)
        
        return None
    
    def _detectar_movimiento_significativo(self, par, precio_actual, historial):
        """Detectar movimientos porcentuales significativos"""
        precios = historial['precios']
        timestamps = historial['timestamp']
        
        if len(precios) < 10:
            return None
        
        # Obtener tipo de activo para umbral
        tipo_activo = self._obtener_tipo_activo(par)
        umbral = self.umbrales_movimiento.get(tipo_activo, 0.0050)
        
        # Analizar últimos 30 minutos (6 velas de 5 minutos)
        precio_30min_atras = self._obtener_precio_periodo_atras(precios, timestamps, minutos=30)
        precio_1h_atras = self._obtener_precio_periodo_atras(precios, timestamps, minutos=60)
        
        if not precio_30min_atras or not precio_1h_atras:
            return None
        
        # Calcular movimientos porcentuales
        movimiento_30min = ((precio_actual - precio_30min_atras) / precio_30min_atras) * 100
        movimiento_1h = ((precio_actual - precio_1h_atras) / precio_1h_atras) * 100
        
        # 🎯 DETECTAR MOVIMIENTOS SIGNIFICATIVOS
        movimiento_absoluto_30min = abs(movimiento_30min)
        movimiento_absoluto_1h = abs(movimiento_1h)
        
        # Umbral dinámico basado en tipo de activo
        umbral_porcentual = umbral * 100  # Convertir a porcentaje
        
        # Señal por movimiento fuerte en 30 minutos
        if movimiento_absoluto_30min >= umbral_porcentual:
            direccion = 'COMPRA' if movimiento_30min > 0 else 'VENTA'
            return self._crear_señal_movimiento(
                par, precio_actual, direccion, 
                movimiento_30min, '30MIN', tipo_activo
            )
        
        # Señal por movimiento fuerte en 1 hora
        elif movimiento_absoluto_1h >= umbral_porcentual:
            direccion = 'COMPRA' if movimiento_1h > 0 else 'VENTA'
            return self._crear_señal_movimiento(
                par, precio_actual, direccion,
                movimiento_1h, '1HORA', tipo_activo
            )
        
        return None
    
    def _obtener_precio_periodo_atras(self, precios, timestamps, minutos=30):
        """Obtener precio de hace X minutos"""
        if not precios or not timestamps:
            return None
        
        tiempo_limite = datetime.now() - timedelta(minutes=minutos)
        
        # Buscar el precio más cercano al tiempo límite
        for i in range(len(timestamps)-1, -1, -1):
            if timestamps[i] <= tiempo_limite:
                return precios[i]
        
        # Si no encontramos, usar el precio más antiguo
        return precios[0] if precios else None
    
    def _obtener_tipo_activo(self, par):
        """Determinar tipo de activo para umbrales específicos"""
        try:
            from config import PARAMETROS_POR_PAR
            params = PARAMETROS_POR_PAR.get(par, {})
            return params.get('tipo', 'forex')
        except Exception:
            return 'forex'
    
    def _calcular_rsi_avanzado(self, precios, periodo=14):
        """Calcular RSI más preciso"""
        if len(precios) < periodo + 1:
            return 50
        
        cambios = [precios[i] - precios[i-1] for i in range(1, len(precios))]
        
        ganancias = [c for c in cambios[-periodo:] if c > 0]
        perdidas = [abs(c) for c in cambios[-periodo:] if c < 0]
        
        if not ganancias and not perdidas:
            return 50
        
        avg_ganancia = sum(ganancias) / len(ganancias) if ganancias else 0
        avg_perdida = sum(perdidas) / len(perdidas) if perdidas else 0.001  # Evitar división por 0
        
        rs = avg_ganancia / avg_perdida
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def _crear_señal_momentum(self, par, precio, direccion, rsi):
        """Crear señal de momentum"""
        try:
            from config import PARAMETROS_POR_PAR
            params = PARAMETROS_POR_PAR.get(par, {})
            
            if not params:
                # Parámetros por defecto si no se encuentran
                params = {'tp_niveles': [0.015, 0.025], 'sl': 0.012, 'dca_niveles': [0.005, 0.010], 'winrate': 55}
            
            if direccion == 'COMPRA':
                tp1 = precio * (1 + params['tp_niveles'][0])
                tp2 = precio * (1 + params['tp_niveles'][1])
                sl = precio * (1 - params['sl'])
                dca1 = precio * (1 - params['dca_niveles'][0])
                dca2 = precio * (1 - params['dca_niveles'][1])
            else:
                tp1 = precio * (1 - params['tp_niveles'][0])
                tp2 = precio * (1 - params['tp_niveles'][1])
                sl = precio * (1 + params['sl'])
                dca1 = precio * (1 + params['dca_niveles'][0])
                dca2 = precio * (1 + params['dca_niveles'][1])
            
            return {
                'par': par,
                'direccion': direccion,
                'precio_actual': precio,
                'tp1': round(tp1, 5),
                'tp2': round(tp2, 5),
                'sl': round(sl, 5),
                'dca_1': round(dca1, 5),
                'dca_2': round(dca2, 5),
                'rsi': rsi,
                'tendencia': 'ALCISTA' if direccion == 'COMPRA' else 'BAJISTA',
                'winrate_esperado': params.get('winrate', 55),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'estrategia': 'Momentum Rápido',
                'confianza': 'ALTA',
                'tipo_señal': 'MOMENTUM'
            }
        except Exception as e:
            logger.error(f"❌ Error creando señal momentum para {par}: {e}")
            return None
    
    def _crear_señal_movimiento(self, par, precio, direccion, movimiento_porcentual, periodo, tipo_activo):
        """Crear señal por movimiento significativo"""
        try:
            from config import PARAMETROS_POR_PAR
            params = PARAMETROS_POR_PAR.get(par, {})
            
            if not params:
                # Parámetros por defecto si no se encuentran
                params = {'tp_niveles': [0.015, 0.025], 'sl': 0.012, 'dca_niveles': [0.005, 0.010], 'winrate': 55}
            
            # Ajustar parámetros para señales de movimiento (más agresivos)
            multiplier_movimiento = 1.3  # 30% más agresivo en movimientos fuertes
            
            if direccion == 'COMPRA':
                tp1 = precio * (1 + params['tp_niveles'][0] * multiplier_movimiento)
                tp2 = precio * (1 + params['tp_niveles'][1] * multiplier_movimiento)
                sl = precio * (1 - params['sl'] * 0.8)  # SL más ajustado
                dca1 = precio * (1 - params['dca_niveles'][0])
                dca2 = precio * (1 - params['dca_niveles'][1])
            else:
                tp1 = precio * (1 - params['tp_niveles'][0] * multiplier_movimiento)
                tp2 = precio * (1 - params['tp_niveles'][1] * multiplier_movimiento)
                sl = precio * (1 + params['sl'] * 0.8)  # SL más ajustado
                dca1 = precio * (1 + params['dca_niveles'][0])
                dca2 = precio * (1 + params['dca_niveles'][1])
            
            return {
                'par': par,
                'direccion': direccion,
                'precio_actual': precio,
                'tp1': round(tp1, 5),
                'tp2': round(tp2, 5),
                'sl': round(sl, 5),
                'dca_1': round(dca1, 5),
                'dca_2': round(dca2, 5),
                'rsi': 50,  # No aplica para señales de movimiento
                'tendencia': 'FUERTE_ALCISTA' if direccion == 'COMPRA' else 'FUERTE_BAJISTA',
                'winrate_esperado': params.get('winrate', 55),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'estrategia': f'Movimiento {periodo}',
                'confianza': 'MUY_ALTA',
                'tipo_señal': 'MOVIMIENTO',
                'movimiento_porcentual': movimiento_porcentual,
                'periodo_movimiento': periodo,
                'tipo_activo': tipo_activo
            }
        except Exception as e:
            logger.error(f"❌ Error creando señal movimiento para {par}: {e}")
            return None
