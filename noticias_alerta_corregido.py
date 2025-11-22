# noticias_alerta.py - SISTEMA DE ALERTAS DE NOTICIAS ECONÓMICAS
import requests
import json
import os
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
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500']
            },
            'NFP': {
                'nombre': 'Nóminas No Agrícolas (NFP)',
                'pais': 'EE.UU.',
                'impacto': 'ALTO',
                'efecto_usd': 'FUERTE_POSITIVO',
                'efecto_oro': 'NEGATIVO',
                'efecto_acciones': 'NEGATIVO',
                'simbolos_afectados': ['EURUSD', 'USDJPY', 'XAUUSD', 'SPX500']
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
                'efecto_usd': 'FUERTE_POSITIVO',
                'efecto_oro': 'NEGATIVO',
                'efecto_acciones': 'NEGATIVO',
                'simbolos_afectados': ['EURUSD', 'XAUUSD', 'SPX500', 'NAS100']
            }
        }

        self.umbrales_recomendacion = {
            'MAYOR_ESPERADO': {
                'descripcion': 'Dato mejor a lo esperado (positivo para la economía)',
                'sesgo_usd': 'ALCISTA',
                'sesgo_oro': 'BAJISTA',
                'sesgo_acciones': 'BAJISTA'
            },
            'MENOR_ESPERADO': {
                'descripcion': 'Dato peor a lo esperado (negativo para la economía)',
                'sesgo_usd': 'BAJISTA',
                'sesgo_oro': 'ALCISTA',
                'sesgo_acciones': 'ALCISTA'
            },
            'EN_LINEA': {
                'descripcion': 'Dato en línea con lo esperado',
                'sesgo_usd': 'NEUTRAL',
                'sesgo_oro': 'NEUTRAL',
                'sesgo_acciones': 'NEUTRAL'
            }
        }

        # Configuración opcional de API externa
        self.api_url = os.environ.get('ECONOMIC_NEWS_API_URL')
        self.api_key = os.environ.get('ECONOMIC_NEWS_API_KEY')
        self.ultimas_alertas = []

    def _normalizar_evento(self, nombre_bruto):
        """Intentar mapear un nombre de evento a nuestras claves internas"""
        nombre = nombre_bruto.lower()
        if 'cpi' in nombre or 'ipc' in nombre:
            return 'IPC_MENSUAL'
        if 'non-farm' in nombre or 'nfp' in nombre:
            return 'NFP'
        if 'unemployment' in nombre or 'desempleo' in nombre:
            return 'TASA_DESEMPLEO'
        if 'rate decision' in nombre or 'fed' in nombre:
            return 'DECISION_TASAS_FED'
        return None

    def _crear_mensaje_resumen(self, alerta):
        """Crear un resumen corto para enviar por Telegram"""
        return (
            f"📰 NOTICIA ECONÓMICA IMPORTANTE\n"
            f"📍 País: {alerta['pais']}\n"
            f"📊 Evento: {alerta['nombre']}\n"
            f"📈 Resultado: {alerta['resultado_descripcion']}\n"
            f"💥 Impacto estimado: {alerta['impacto_mercado']}\n"
            f"🎯 Sesgo USD: {alerta['sesgo_usd']}\n"
            f"🥇 Oro: {alerta['sesgo_oro']} | Acciones: {alerta['sesgo_acciones']}\n"
        )

    def _formatear_timestamp(self, ts):
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                ts = datetime.now()
        return ts.strftime("%Y-%m-%d %H:%M:%S")

    def _determinar_direccion_forex(self, info_evento, datos):
        """Determinar dirección probable del USD"""
        resultado = datos['resultado']
        if resultado == 'MAYOR_ESPERADO':
            return info_evento['efecto_usd']
        elif resultado == 'MENOR_ESPERADO':
            return 'FUERTE_NEGATIVO' if info_evento['efecto_usd'] == 'FUERTE_POSITIVO' else 'FUERTE_POSITIVO'
        return 'NEUTRAL'

    def _determinar_direccion_oro(self, info_evento, datos):
        if datos['resultado'] == 'MAYOR_ESPERADO':
            return info_evento['efecto_oro']
        elif datos['resultado'] == 'MENOR_ESPERADO':
            return 'POSITIVO' if info_evento['efecto_oro'] == 'NEGATIVO' else 'NEGATIVO'
        return 'NEUTRAL'

    def _determinar_direccion_acciones(self, info_evento, datos):
        if datos['resultado'] == 'MAYOR_ESPERADO':
            return info_evento['efecto_acciones']
        elif datos['resultado'] == 'MENOR_ESPERADO':
            return 'POSITIVO' if info_evento['efecto_acciones'] == 'NEGATIVO' else 'NEGATIVO'
        return 'NEUTRAL'

    def obtener_datos_economicos(self):
        """Obtener datos económicos desde una API real si está configurada, o simular en caso contrario."""
        # Intentar usar una API sólo si se configuró ECONOMIC_NEWS_API_URL
        if getattr(self, "api_url", None):
            try:
                params = {}
                if getattr(self, "api_key", None):
                    params["apikey"] = self.api_key
                resp = requests.get(self.api_url, params=params, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    eventos = self._parsear_respuesta_api(data)
                    if eventos:
                        return eventos
            except Exception as e:
                print(f"⚠️ Error usando API de noticias económicas, usando modo simulado: {e}")
        # Si no hay API o falla el parseo, usar datos simulados seguros
        return self._simular_datos_economicos()

    def _parsear_respuesta_api(self, data):
        """Convertir la respuesta de la API al formato estándar interno.

        Esta implementación es genérica: si el formato no coincide, devuelve None
        y el sistema usará datos simulados. El usuario puede adaptar este método
        a la API específica que utilice.
        """
        try:
            # EJEMPLO de estructura esperada:
            # data = [
            #   {"code": "IPC_MENSUAL", "actual": 0.4, "forecast": 0.2, "time": "2025-11-22T13:30:00Z"},
            #   {"code": "NFP", "actual": 250, "forecast": 180, "time": "2025-11-22T13:30:00Z"},
            # ]
            eventos = {}
            for item in data:
                code = (item.get("code") or item.get("evento") or "").upper()
                if code in self.eventos_alto_impacto:
                    try:
                        actual = float(item.get("actual"))
                        forecast = float(item.get("forecast"))
                    except (TypeError, ValueError):
                        continue
                    ts_str = item.get("time") or item.get("timestamp")
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        except Exception:
                            ts = datetime.now()
                    else:
                        ts = datetime.now()
                    if actual > forecast:
                        resultado = "MAYOR_ESPERADO"
                    elif actual < forecast:
                        resultado = "MENOR_ESPERADO"
                    else:
                        resultado = "EN_LINEA"
                    eventos[code] = {
                        "valor_actual": actual,
                        "valor_esperado": forecast,
                        "resultado": resultado,
                        "timestamp": ts,
                        "impacto_mercado": "DESCONOCIDO"
                    }
            return eventos or None
        except Exception:
            return None

    def verificar_noticias_impacto(self):
        """Verificar si hay noticias de alto impacto recientes"""
        try:
            # Obtener datos económicos (API real si está configurada, si no modo simulado)
            noticias_simuladas = self.obtener_datos_economicos()

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

        resultado_info = self.umbrales_recomendacion.get(datos['resultado'], self.umbrales_recomendacion['EN_LINEA'])

        alerta = {
            'tipo': 'ALERTA_NOTICIA',
            'evento': evento,
            'nombre': info_evento['nombre'],
            'pais': info_evento['pais'],
            'impacto': info_evento['impacto'],
            'timestamp': self._formatear_timestamp(datos['timestamp']),
            'impacto_mercado': datos.get('impacto_mercado', 'MODERADO'),
            'direccion_usd': direccion_forex,
            'direccion_oro': direccion_oro,
            'direccion_acciones': direccion_acciones,
            'resultado': datos['resultado'],
            'resultado_descripcion': resultado_info['descripcion'],
            'sesgo_usd': resultado_info['sesgo_usd'],
            'sesgo_oro': resultado_info['sesgo_oro'],
            'sesgo_acciones': resultado_info['sesgo_acciones'],
            'simbolos_afectados': info_evento['simbolos_afectados'],
            'mensaje_resumen': self._crear_mensaje_resumen({
                'pais': info_evento['pais'],
                'nombre': info_evento['nombre'],
                'resultado_descripcion': resultado_info['descripcion'],
                'impacto_mercado': datos.get('impacto_mercado', 'MODERADO'),
                'sesgo_usd': resultado_info['sesgo_usd'],
                'sesgo_oro': resultado_info['sesgo_oro'],
                'sesgo_acciones': resultado_info['sesgo_acciones']
            })
        }

        self.ultimas_alertas.append(alerta)
        return alerta

    def obtener_alertas_activas(self):
        """Obtener alertas activas de noticias"""
        return self.verificar_noticias_impacto()
