# detector_movimientos.py - DETECTOR DE MOVIMIENTOS PORCENTUALES SIGNIFICATIVOS
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DetectorMovimientos:
    """
    Detecta movimientos porcentuales significativos en pares
    y genera alertas cuando superan umbrales predefinidos
    """
    
    def __init__(self):
        # UMBRALES POR TIPO DE ACTIVO (en porcentaje)
        self.umbrales = {
            'forex': 0.003,      # 0.3%
            'commodities': 0.005, # 0.5%  
            'indices': 0.008,     # 0.8%
            'crypto': 0.020       # 2.0%
        }
        
        # HISTORIAL DE PRECIOS POR PAR
        self.historico = {}
        
        # MOVIMIENTOS YA NOTIFICADOS (evitar duplicados)
        self.movimientos_notificados = set()
        
        logger.info("✅ Detector de Movimientos inicializado")

    def clasificar_tipo_activo(self, par):
        """Clasificar el tipo de activo para aplicar umbral correcto"""
        if any(metal in par for metal in ['XAU', 'XAG', 'XPT', 'XPD']):
            return 'commodities'
        elif any(energia in par for energia in ['OIL', 'NGAS']):
            return 'commodities'
        elif any(indice in par for indice in ['SPX', 'NAS', 'DJI', 'GER', 'UK', 'JPN']):
            return 'indices'
        elif any(metal in par for metal in ['COPPER']):
            return 'commodities'
        else:
            return 'forex'

    def obtener_umbral_activo(self, par):
        """Obtener umbral específico para el par"""
        tipo = self.clasificar_tipo_activo(par)
        return self.umbrales.get(tipo, 0.005)

    def actualizar_precio(self, par, precio_actual, timestamp=None):
        """
        Actualizar precio y detectar movimientos significativos
        
        Args:
            par (str): Símbolo del par (ej: EURUSD, XAUUSD)
            precio_actual (float): Precio actual
            timestamp (datetime): Timestamp del precio
            
        Returns:
            dict or None: Alerta de movimiento si es significativo
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Inicializar historial si no existe
        if par not in self.historico:
            self.historico[par] = []
            logger.info(f"📊 Iniciando seguimiento para {par}")

        # Agregar nuevo precio al historial
        nuevo_dato = {
            'precio': float(precio_actual),
            'timestamp': timestamp,
            'par': par
        }
        
        self.historico[par].append(nuevo_dato)
        
        # Limpiar datos antiguos (mantener solo 48 horas)
        self._limpiar_historial_antiguo(par)
        
        # Detectar movimientos significativos
        alertas = self._detectar_movimientos_significativos(par)
        
        return alertas

    def _limpiar_historial_antiguo(self, par, horas_maximas=48):
        """Limpiar datos más antiguos que horas_maximas"""
        if par not in self.historico:
            return
            
        cutoff = datetime.now() - timedelta(hours=horas_maximas)
        historial_limpio = [
            dato for dato in self.historico[par] 
            if dato['timestamp'] > cutoff
        ]
        
        eliminados = len(self.historico[par]) - len(historial_limpio)
        if eliminados > 0:
            logger.debug(f"🧹 Limpiados {eliminados} datos antiguos de {par}")
        
        self.historico[par] = historial_limpio

    def _detectar_movimientos_significativos(self, par):
        """
        Detectar movimientos significativos en diferentes timeframes
        """
        if par not in self.historico or len(self.historico[par]) < 5:
            return None

        precios = [d['precio'] for d in self.historico[par]]
        timestamps = [d['timestamp'] for d in self.historico[par]]
        
        alertas = []
        umbral = self.obtener_umbral_activo(par)

        # MOVIMIENTO 1 HORA (últimos 12 registros si hay datos de 5min)
        if len(precios) >= 12:
            movimiento_1h = self._calcular_movimiento_periodo(precios, -12, -1)
            if movimiento_1h and abs(movimiento_1h['porcentaje']) >= umbral:
                alerta = self._crear_alerta_movimiento(par, movimiento_1h, '1HORA')
                if alerta and self._es_movimiento_nuevo(alerta):
                    alertas.append(alerta)

        # MOVIMIENTO 4 HORAS (últimos 48 registros)
        if len(precios) >= 48:
            movimiento_4h = self._calcular_movimiento_periodo(precios, -48, -1)
            if movimiento_4h and abs(movimiento_4h['porcentaje']) >= umbral:
                alerta = self._crear_alerta_movimiento(par, movimiento_4h, '4HORAS')
                if alerta and self._es_movimiento_nuevo(alerta):
                    alertas.append(alerta)

        # MOVIMIENTO 24 HORAS (todo el historial disponible)
        if len(precios) >= 10:  # Mínimo para cálculo diario
            movimiento_24h = self._calcular_movimiento_periodo(precios, 0, -1)
            if movimiento_24h and abs(movimiento_24h['porcentaje']) >= umbral:
                alerta = self._crear_alerta_movimiento(par, movimiento_24h, '24HORAS')
                if alerta and self._es_movimiento_nuevo(alerta):
                    alertas.append(alerta)

        return alertas if alertas else None

    def _calcular_movimiento_periodo(self, precios, inicio_idx, fin_idx):
        """
        Calcular movimiento porcentual en un período específico
        """
        try:
            precio_inicial = precios[inicio_idx]
            precio_final = precios[fin_idx]
            
            if precio_inicial == 0:
                return None
                
            movimiento_absoluto = precio_final - precio_inicial
            movimiento_porcentual = (movimiento_absoluto / precio_inicial) * 100
            
            return {
                'porcentaje': movimiento_porcentual,
                'absoluto': movimiento_absoluto,
                'precio_inicial': precio_inicial,
                'precio_final': precio_final,
                'inicio_idx': inicio_idx,
                'fin_idx': fin_idx
            }
        except (IndexError, ZeroDivisionError) as e:
            logger.warning(f"Error cálculo movimiento: {e}")
            return None

    def _crear_alerta_movimiento(self, par, movimiento, periodo):
        """
        Crear estructura de alerta de movimiento
        """
        # Determinar dirección y magnitud
        direccion = "ALCISTA" if movimiento['porcentaje'] > 0 else "BAJISTA"
        
        umbral = self.obtener_umbral_activo(par)
        magnitud_abs = abs(movimiento['porcentaje'])
        
        if magnitud_abs >= umbral * 3:
            magnitud = "MUY_FUERTE"
            emoji = "🚀🚀" if direccion == "ALCISTA" else "📉📉"
        elif magnitud_abs >= umbral * 2:
            magnitud = "FUERTE" 
            emoji = "🚀" if direccion == "ALCISTA" else "📉"
        else:
            magnitud = "MODERADO"
            emoji = "📈" if direccion == "ALCISTA" else "📊"

        # Crear ID único para esta alerta (evitar duplicados)
        alerta_id = f"{par}_{periodo}_{direccion}_{magnitud_abs:.2f}"
        
        alerta = {
            'id': alerta_id,
            'tipo': 'ALERTA_MOVIMIENTO',
            'par': par,
            'periodo': periodo,
            'movimiento_porcentual': round(movimiento['porcentaje'], 3),
            'movimiento_absoluto': round(movimiento['absoluto'], 5),
            'precio_inicial': round(movimiento['precio_inicial'], 5),
            'precio_actual': round(movimiento['precio_final'], 5),
            'direccion': direccion,
            'magnitud': magnitud,
            'umbral_superado': round(magnitud_abs, 3),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'emoji': emoji,
            'tipo_activo': self.clasificar_tipo_activo(par)
        }
        
        return alerta

    def _es_movimiento_nuevo(self, alerta):
        """
        Verificar si este movimiento ya fue notificado recientemente
        """
        alerta_id = alerta['id']
        
        # Si ya fue notificado, no notificar de nuevo
        if alerta_id in self.movimientos_notificados:
            return False
        
        # Agregar a notificados y limpiar antiguos periódicamente
        self.movimientos_notificados.add(alerta_id)
        
        # Limpiar notificaciones antiguas (mantener solo últimas 100)
        if len(self.movimientos_notificados) > 100:
            self.movimientos_notificados = set(list(self.movimientos_notificados)[-50:])
        
        return True

    def obtener_estadisticas_par(self, par):
        """
        Obtener estadísticas de movimientos para un par
        """
        if par not in self.historico or len(self.historico[par]) < 2:
            return None
            
        precios = [d['precio'] for d in self.historico[par]]
        
        # Calcular varios movimientos
        movimientos = {}
        
        # Movimiento total (desde primer precio)
        if len(precios) >= 2:
            movimiento_total = self._calcular_movimiento_periodo(precios, 0, -1)
            if movimiento_total:
                movimientos['total'] = movimiento_total
        
        # Movimiento últimas 4 horas
        if len(precios) >= 48:
            movimiento_4h = self._calcular_movimiento_periodo(precios, -48, -1)
            if movimiento_4h:
                movimientos['4h'] = movimiento_4h
        
        # Movimiento última hora
        if len(precios) >= 12:
            movimiento_1h = self._calcular_movimiento_periodo(precios, -12, -1)
            if movimiento_1h:
                movimientos['1h'] = movimiento_1h
        
        return {
            'par': par,
            'total_registros': len(self.historico[par]),
            'precio_actual': precios[-1] if precios else None,
            'movimientos': movimientos,
            'umbral_actual': self.obtener_umbral_activo(par)
        }

    def limpiar_historial_completo(self):
        """Limpiar todo el historial (para testing o reset)"""
        self.historico = {}
        self.movimientos_notificados = set()
        logger.info("🧹 Historial de movimientos limpiado completamente")

# Instancia global para uso fácil
detector_movimientos = DetectorMovimientos()
