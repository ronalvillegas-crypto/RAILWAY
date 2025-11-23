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
    
    def ajustar_estrategia_por_sesion(self, par):
        """Ajustar parámetros de estrategia según sesión"""
        sesion_actual, _ = self.obtener_sesion_actual()
        
        ajustes = {
            "ASIA": {
                "volatilidad": "MEDIA", 
                "tp_multiplier": 2.5, 
                "sl_multiplier": 1.2,
                "descripcion": "Mercado asiático - volatilidad media"
            },
            "LONDRES": {
                "volatilidad": "ALTA", 
                "tp_multiplier": 3.0, 
                "sl_multiplier": 1.0,
                "descripcion": "Mercado europeo - alta volatilidad"
            },
            "NUEVA_YORK": {
                "volatilidad": "ALTA", 
                "tp_multiplier": 3.5, 
                "sl_multiplier": 0.8,
                "descripcion": "Mercado americano - máxima volatilidad"
            },
            "FUERA_HORARIO": {
                "volatilidad": "BAJA", 
                "tp_multiplier": 2.0, 
                "sl_multiplier": 1.5,
                "descripcion": "Fuera de horario - baja volatilidad"
            }
        }
        
        # Ajustes específicos para overlaps
        if "OVERLAP" in sesion_actual:
            return {
                "volatilidad": "MUY_ALTA",
                "tp_multiplier": 4.0,
                "sl_multiplier": 0.7,
                "descripcion": "Overlap de sesiones - máxima volatilidad"
            }
        
        return ajustes.get(sesion_actual, ajustes["FUERA_HORARIO"])
    
    def es_horario_optimo_trading(self):
        """Verificar si es buen momento para trading"""
        sesion_actual, _ = self.obtener_sesion_actual()
        return sesion_actual != "FUERA_HORARIO"
    
    def obtener_proxima_sesion(self):
        """Obtener información de la próxima sesión"""
        hora_utc = datetime.utcnow().hour
        
        for nombre, sesion in self.sesiones.items():
            if hora_utc < sesion["inicio"]:
                horas_faltantes = sesion["inicio"] - hora_utc
                return nombre, horas_faltantes
        
        # Si es después de la última sesión, retornar primera sesión del siguiente día
        primera_sesion = list(self.sesiones.values())[0]
        horas_faltantes = (24 - hora_utc) + primera_sesion["inicio"]
        return list(self.sesiones.keys())[0], horas_faltantes
    
    def obtener_estado_sesiones(self):
        """Obtener estado completo de todas las sesiones"""
        estado = {
            'actual': self.obtener_sesion_actual()[0],
            'proxima': self.obtener_proxima_sesion()[0],
            'horas_faltantes_proxima': self.obtener_proxima_sesion()[1],
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
