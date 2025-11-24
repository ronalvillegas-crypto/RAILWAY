# central_precios.py - FUENTE ÚNICA Y CENTRALIZADA DE PRECIOS
import time
import logging
from datetime import datetime, timedelta
from threading import Lock

logger = logging.getLogger(__name__)

class CentralPrecios:
    """
    Fuente centralizada de precios para evitar inconsistencias
    Todos los módulos obtienen precios desde aquí
    """
    
    def __init__(self):
        self.precios_actuales = {}
        self.ultima_actualizacion = {}
        self.cache_ttl = 30  # 30 segundos de cache
        self.lock = Lock()
        
        # Módulo de obtención de precios
        self.yahoo_api = None
        
        logger.info("✅ Central de Precios inicializada")

    def _get_yahoo_api(self):
        """Obtener API de Yahoo (lazy loading)"""
        if self.yahoo_api is None:
            try:
                from yahoo_api_mejorado import YahooFinanceAPI
                self.yahoo_api = YahooFinanceAPI()
            except ImportError as e:
                logger.error(f"❌ No se pudo cargar Yahoo API: {e}")
                return None
        return self.yahoo_api

    def obtener_precio_actual(self, simbolo, forzar_actualizacion=False):
        """
        Obtener precio actual desde fuente centralizada
        
        Args:
            simbolo (str): Símbolo del par (EURUSD, XAUUSD, etc.)
            forzar_actualizacion (bool): Ignorar cache y obtener precio fresco
            
        Returns:
            float or None: Precio actual o None si error
        """
        with self.lock:
            # Verificar si tenemos precio cacheado y válido
            ahora = datetime.now()
            precio_cacheado = self.precios_actuales.get(simbolo)
            ultima_actualizacion = self.ultima_actualizacion.get(simbolo)
            
            if (not forzar_actualizacion and 
                precio_cacheado and 
                ultima_actualizacion and 
                (ahora - ultima_actualizacion).total_seconds() < self.cache_ttl):
                logger.debug(f"📊 Precio desde cache: {simbolo} = {precio_cacheado}")
                return precio_cacheado

            # Obtener precio fresco
            try:
                yahoo = self._get_yahoo_api()
                if yahoo:
                    precio = yahoo.obtener_precio_redundante(simbolo)
                    
                    if precio and precio > 0:
                        self.precios_actuales[simbolo] = precio
                        self.ultima_actualizacion[simbolo] = ahora
                        
                        logger.info(f"✅ Precio actualizado: {simbolo} = {precio}")
                        return precio
                    else:
                        logger.warning(f"⚠️ Precio inválido para {simbolo}: {precio}")
                
                # Fallback a precio cacheado si disponible
                if precio_cacheado:
                    logger.warning(f"🔄 Usando precio cacheado por fallo: {simbolo}")
                    return precio_cacheado
                    
                return None
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo precio {simbolo}: {e}")
                
                # Fallback a precio cacheado
                if precio_cacheado:
                    logger.warning(f"🔄 Usando precio cacheado por error: {simbolo}")
                    return precio_cacheado
                    
                return None

    def obtener_precios_lote(self, simbolos):
        """
        Obtener múltiples precios en lote para eficiencia
        
        Args:
            simbolos (list): Lista de símbolos
            
        Returns:
            dict: Diccionario con precios {simbolo: precio}
        """
        precios = {}
        
        for simbolo in simbolos:
            precio = self.obtener_precio_actual(simbolo)
            if precio:
                precios[simbolo] = precio
            else:
                logger.warning(f"⚠️ No se pudo obtener precio para {simbolo}")
        
        return precios

    def verificar_consistencia_precios(self, simbolo, precio_proporcionado, tolerancia=0.001):
        """
        Verificar si un precio proporcionado es consistente con nuestra fuente
        
        Args:
            simbolo (str): Símbolo del par
            precio_proporcionado (float): Precio a verificar
            tolerancia (float): Tolerancia porcentual (0.1%)
            
        Returns:
            bool: True si es consistente
        """
        precio_central = self.obtener_precio_actual(simbolo)
        
        if not precio_central or not precio_proporcionado:
            return False
        
        diferencia_porcentual = abs((precio_proporcionado - precio_central) / precio_central) * 100
        
        if diferencia_porcentual > tolerancia:
            logger.warning(f"⚠️ Inconsistencia precio {simbolo}: Central={precio_central}, Proporcionado={precio_proporcionado}, Diff={diferencia_porcentual:.3f}%")
            return False
        
        logger.debug(f"✅ Precio consistente: {simbolo} = {precio_central}")
        return True

    def obtener_estadisticas(self):
        """Obtener estadísticas de la central de precios"""
        total_pares = len(self.precios_actuales)
        precios_validos = sum(1 for p in self.precios_actuales.values() if p and p > 0)
        
        return {
            'total_pares_registrados': total_pares,
            'precios_validos_actualmente': precios_validos,
            'cache_ttl_segundos': self.cache_ttl,
            'ultima_actualizacion': self.ultima_actualizacion
        }

    def limpiar_cache_antiguo(self, horas_maximas=24):
        """Limpiar precios muy antiguos del cache"""
        cutoff = datetime.now() - timedelta(hours=horas_maximas)
        eliminados = 0
        
        for simbolo, timestamp in list(self.ultima_actualizacion.items()):
            if timestamp < cutoff:
                del self.precios_actuales[simbolo]
                del self.ultima_actualizacion[simbolo]
                eliminados += 1
        
        if eliminados > 0:
            logger.info(f"🧹 Limpiados {eliminados} precios antiguos del cache")

# Instancia global para uso en todos los módulos
central_precios = CentralPrecios()
