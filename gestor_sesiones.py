# gestor_sesiones.py - GESTIÓN INTELIGENTE DE SESIONES DE MERCADO
from datetime import datetime, timedelta

class GestorSesionesMercado:
    """
    Gestiona sesiones de mercado globales y ajusta estrategias
    """
    
    def __init__(self):
        self.sesiones = {
            "ASIA": {"inicio": 0, "fin": 8, "activos": ["USDJPY", "AUDUSD", "NZDUSD", "XAUUSD"]},
            "LONDRES": {"inicio": 8, "fin": 16, "activos": ["EURUSD", "GBPUSD", "EURCHF", "XAGUSD"]},
            "NUEVA_YORK": {"inicio": 13, "fin": 21, "activos": ["USDCAD", "USDCHF", "SPX500", "NAS100"]}
        }
    
    def obtener_sesion_actual(self):
        """Obtener sesión de mercado actual basada en hora UTC"""
        hora_utc = datetime.utcnow().hour
        
        for nombre, sesion in self.sesiones.items():
            if sesion["inicio"] <= hora_utc < sesion["fin"]:
                return nombre, sesion
        
        return "FUERA_HORARIO", None
    
    def obtener_activos_recomendados(self):
        """Obtener activos recomendados para la sesión actual"""
        sesion_actual, datos_sesion = self.obtener_sesion_actual()
        
        if datos_sesion:
            return datos_sesion["activos"]
        
        # Fuera de horario - todos los activos
        return list(set([activo for sesion in self.sesiones.values() for activo in sesion["activos"]]))
    
    def ajustar_estrategia_por_sesion(self, par):
        """Ajustar parámetros de estrategia según sesión"""
        sesion_actual, _ = self.obtener_sesion_actual()
        
        ajustes = {
            "ASIA": {"volatilidad": "MEDIA", "tp_multiplier": 2.5, "sl_multiplier": 1.2},
            "LONDRES": {"volatilidad": "ALTA", "tp_multiplier": 3.0, "sl_multiplier": 1.0},
            "NUEVA_YORK": {"volatilidad": "ALTA", "tp_multiplier": 3.5, "sl_multiplier": 0.8},
            "FUERA_HORARIO": {"volatilidad": "BAJA", "tp_multiplier": 2.0, "sl_multiplier": 1.5}
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
