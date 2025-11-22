# noticias_alerta.py - SISTEMA DE ALERTAS DE NOTICIAS ECONÓMICAS
import requests
import json
from datetime import datetime, timedelta

class AlertaNoticias:
    def __init__(self):
        self.eventos_alto_impacto = {
            # 📊 DATOS ECONÓMICOS CLAVE
            'IPC_MENSUAL': {
                'nombre': 'IPC Mensual (Inflación)',
                'pais': 'EE.UU.',
                'impacto': 'ALTO',
                'efecto_usd': 'FUERTE_POSITIVO',
                'efecto_oro': 'NEGATIVO', 
                'efecto_acciones': 'NEGATIVO',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500', 'NAS100']
            },
            'TASA_DESEMPLEO': {
                'nombre': 'Tasa de Desempleo',
                'pais': 'EE.UU.',
                'impacto': 'ALTO',
                'efecto_usd': 'FUERTE_NEGATIVO',
                'efecto_oro': 'POSITIVO',
                'efecto_acciones': 'POSITIVO',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500']
            },
            'DECISION_TASAS_FED': {
                'nombre': 'Decisión de Tasas FED',
                'pais': 'EE.UU.', 
                'impacto': 'MUY_ALTO',
                'efecto_usd': 'VOLATIL',
                'efecto_oro': 'VOLATIL',
                'efecto_acciones': 'VOLATIL',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500', 'DJI30']
            },
            'NFP': {
                'nombre': 'Nóminas No Agrícolas',
                'pais': 'EE.UU.',
                'impacto': 'MUY_ALTO', 
                'efecto_usd': 'FUERTE_POSITIVO',
                'efecto_oro': 'NEGATIVO',
                'efecto_acciones': 'POSITIVO',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500', 'USDJPY']
            },
            'PMI': {
                'nombre': 'PMI Manufacturero',
                'pais': 'EE.UU.',
                'impacto': 'MEDIO',
                'efecto_usd': 'POSITIVO',
                'efecto_oro': 'NEUTRO',
                'efecto_acciones': 'POSITIVO',
                'simbolos_afectados': ['EURUSD', 'SPX500']
            }
        }
        
        self.ultimas_alertas = []
    
    def verificar_noticias_impacto(self):
        """Verificar si hay noticias de alto impacto recientes"""
        try:
            # Simular obtención de datos económicos (en producción usar API real)
            noticias_simuladas = self._simular_datos_economicos()
            
            alertas_activas = []
            
            for evento, datos in noticias_simuladas.items():
                if self._es_noticia_reciente(datos['timestamp']):
                    alerta = self._crear_alerta(evento, datos)
                    alertas_activas.append(alerta)
            
            return alertas_activas
            
        except Exception as e:
            print(f"❌ Error verificando noticias: {e}")
            return []
    
    def _simular_datos_economicos(self):
        """Simular datos económicos recientes (en producción usar API real)"""
        ahora = datetime.now()
        
        # Simular que el IPC salió más alto de lo esperado
        return {
            'IPC_MENSUAL': {
                'valor_actual': 0.4,
                'valor_esperado': 0.2,
                'resultado': 'MAYOR_ESPERADO',
                'timestamp': ahora - timedelta(minutes=5),  # Hace 5 minutos
                'impacto_mercado': 'FUERTE'
            },
            'NFP': {
                'valor_actual': 250,
                'valor_esperado': 180, 
                'resultado': 'MAYOR_ESPERADO',
                'timestamp': ahora - timedelta(hours=2),  # Hace 2 horas
                'impacto_mercado': 'MODERADO'
            }
        }
    
    def _es_noticia_reciente(self, timestamp):
        """Verificar si la noticia es de los últimos 30 minutos"""
        return (datetime.now() - timestamp).total_seconds() <= 1800  # 30 minutos
    
    def _crear_alerta(self, evento, datos):
        """Crear alerta de noticia"""
        info_evento = self.eventos_alto_impacto[evento]
        
        # Determinar dirección del mercado
        direccion_forex = self._determinar_direccion_forex(info_evento, datos)
        direccion_oro = self._determinar_direccion_oro(info_evento, datos)
        direccion_acciones = self._determinar_direccion_acciones(info_evento, datos)
        
        return {
            'tipo': 'ALERTA_NOTICIA',
            'evento': evento,
            'nombre': info_evento['nombre'],
            'pais': info_evento['pais'],
            'impacto': info_evento['impacto'],
            'timestamp': datos['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            'datos': {
                'valor_actual': datos['valor_actual'],
                'valor_esperado': datos['valor_esperado'],
                'resultado': datos['resultado']
            },
            'efectos_mercado': {
                'forex': direccion_forex,
                'oro': direccion_oro,
                'acciones': direccion_acciones
            },
            'simbolos_afectados': info_evento['simbolos_afectados'],
            'recomendaciones': self._generar_recomendaciones(info_evento, datos)
        }
    
    def _determinar_direccion_forex(self, info_evento, datos):
        """Determinar dirección para Forex basado en noticia"""
        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_usd'] == 'FUERTE_POSITIVO':
                return {'USD': 'FUERTE_ALCISTA', 'EUR': 'BAJISTA', 'GBP': 'BAJISTA'}
            elif info_evento['efecto_usd'] == 'FUERTE_NEGATIVO':
                return {'USD': 'FUERTE_BAJISTA', 'EUR': 'ALCISTA', 'GBP': 'ALCISTA'}
        else:
            return {'USD': 'NEUTRO', 'EUR': 'NEUTRO', 'GBP': 'NEUTRO'}
    
    def _determinar_direccion_oro(self, info_evento, datos):
        """Determinar dirección para Oro basado en noticia"""
        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_oro'] == 'NEGATIVO':
                return 'BAJISTA'
            elif info_evento['efecto_oro'] == 'POSITIVO':
                return 'ALCISTA'
        return 'NEUTRO'
    
    def _determinar_direccion_acciones(self, info_evento, datos):
        """Determinar dirección para Acciones basado en noticia"""
        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_acciones'] == 'NEGATIVO':
                return 'BAJISTA'
            elif info_evento['efecto_acciones'] == 'POSITIVO':
                return 'ALCISTA'
        return 'NEUTRO'
    
    def _generar_recomendaciones(self, info_evento, datos):
        """Generar recomendaciones de trading basadas en la noticia"""
        recomendaciones = []
        
        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_usd'] == 'FUERTE_POSITIVO':
                recomendaciones.extend([
                    "🎯 EURUSD - POSIBLE OPERACIÓN VENTA",
                    "🎯 GBPUSD - POSIBLE OPERACIÓN VENTA", 
                    "💰 USD/JPY - POSIBLE OPERACIÓN COMPRA"
                ])
            
            if info_evento['efecto_oro'] == 'NEGATIVO':
                recomendaciones.append("🪙 XAUUSD - POSIBLE OPERACIÓN VENTA")
                
            if info_evento['efecto_acciones'] == 'NEGATIVO':
                recomendaciones.extend([
                    "📉 SPX500 - POSIBLE OPERACIÓN VENTA",
                    "📉 NAS100 - POSIBLE OPERACIÓN VENTA"
                ])
                
        elif datos['resultado'] == 'MENOR_ESPERADO':
            if info_evento['efecto_usd'] == 'FUERTE_NEGATIVO':
                recomendaciones.extend([
                    "🎯 EURUSD - POSIBLE OPERACIÓN COMPRA",
                    "🎯 GBPUSD - POSIBLE OPERACIÓN COMPRA"
                ])
        
        return recomendaciones
    
    def obtener_alertas_activas(self):
        """Obtener alertas activas de noticias"""
        return self.verificar_noticias_impacto()
