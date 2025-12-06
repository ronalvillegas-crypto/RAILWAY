# gestor_sesiones.py - GESTIÓN INTELIGENTE DE SESIONES DE MERCADO
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GestorSesionesMercado:
    """
    Gestiona sesiones de mercado globales y ajusta estrategias
    Versión mejorada para el bot completo
    """
    
    def __init__(self):
        self.sesiones = {
            "ASIA": {
                "inicio": 0, 
                "fin": 8, 
                "activos": ["USDJPY", "AUDUSD", "NZDUSD", "XAUUSD", "XAGUSD"],
                "descripcion": "Sesión Asiática - Pares JPY y Commodities"
            },
            "LONDRES": {
                "inicio": 8, 
                "fin": 16, 
                "activos": ["EURUSD", "GBPUSD", "EURCHF", "EURGBP", "XAUUSD", "XAGUSD"],
                "descripcion": "Sesión Europea - Pares EUR y GBP"
            },
            "NUEVA_YORK": {
                "inicio": 13, 
                "fin": 21, 
                "activos": ["USDCAD", "USDCHF", "SPX500", "NAS100", "DJI30", "OILUSD"],
                "descripcion": "Sesión Americana - Pares USD e Índices"
            }
        }
        
        # OVERLAPS (superposiciones) importantes
        self.overlaps = [
            {"nombre": "LONDRES-NUEVA_YORK", "inicio": 13, "fin": 16, "activos": ["EURUSD", "GBPUSD", "XAUUSD"]},
            {"nombre": "ASIA-LONDRES", "inicio": 8, "fin": 9, "activos": ["USDJPY", "EURUSD"]}
        ]
        
        logger.info("✅ Gestor de Sesiones inicializado")
    
    def obtener_sesion_actual(self):
        """Obtener sesión de mercado actual basada en hora UTC"""
        hora_utc = datetime.utcnow().hour
        minuto_utc = datetime.utcnow().minute
        
        # Primero verificar overlaps (son más importantes)
        for overlap in self.overlaps:
            if overlap["inicio"] <= hora_utc < overlap["fin"]:
                return f"OVERLAP_{overlap['nombre']}", overlap
        
        # Luego verificar sesiones normales
        for nombre, sesion in self.sesiones.items():
            if sesion["inicio"] <= hora_utc < sesion["fin"]:
                return nombre, sesion
        
        return "FUERA_HORARIO", None
    
    def obtener_activos_recomendados(self):
        """Obtener activos recomendados para la sesión actual"""
        sesion_actual, datos_sesion = self.obtener_sesion_actual()
        
        if datos_sesion:
            logger.info(f"🏪 Sesión activa: {sesion_actual}")
            return datos_sesion["activos"]
        
        # Fuera de horario - todos los activos pero con prioridad baja
        logger.info("🌙 Fuera de horario principal - todos los activos")
        todos_activos = list(set(
            [activo for sesion in self.sesiones.values() for activo in sesion["activos"]]
        ))
        return todos_activos
    
    def es_horario_optimo_trading(self):
        """Verificar si es buen momento para trading"""
        sesion_actual, _ = self.obtener_sesion_actual()
        return sesion_actual != "FUERA_HORARIO"
    
    def obtener_estado_sesiones(self):
        """Obtener estado completo de todas las sesiones"""
        estado = {
            'actual': self.obtener_sesion_actual()[0],
            'es_horario_optimo': self.es_horario_optimo_trading(),
            'sesiones': {}
        }
        
        hora_utc = datetime.utcnow().hour
        
        for nombre, sesion in self.sesiones.items():
            estado['sesiones'][nombre] = {
                'activa': sesion["inicio"] <= hora_utc < sesion["fin"],
                'inicio': sesion["inicio"],
                'fin': sesion["fin"],
                'activos': sesion["activos"]
            }
        
        return estado
