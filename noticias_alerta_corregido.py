# noticias_alerta.py - NOTICIAS ALTO IMPACTO (Apify + Investing.com)
"""
Fuente REAL: Dataset de Apify basado en calendario económico de Investing.com

Usa DIRECTAMENTE el dataset que me pasaste:
    https://api.apify.com/v2/datasets/5tUiuIeUVExG0maAK/items?token=...

Puedes sobreescribir la URL con una variable de entorno:
    APIFY_DATASET_URL

Si la llamada falla o no hay eventos mapeables, simplemente no se envían alertas
(retorna lista vacía).
"""

from datetime import datetime, timedelta
import os
import requests


class AlertaNoticias:
    def __init__(self):
        # =========================
        # EVENTOS QUE NOS IMPORTAN
        # =========================
        self.eventos_alto_impacto = {
            'IPC_MENSUAL': {
                'nombre': 'Índice de Precios al Consumidor (IPC) Mensual',
                'pais': 'Estados Unidos',
                'impacto': 'MUY_ALTO',
                'efecto_usd': 'FUERTE_POSITIVO',
                'efecto_oro': 'NEGATIVO',
                'efecto_acciones': 'NEGATIVO',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500', 'NAS100', 'USDJPY']
            },
            'TASA_DESEMPLEO': {
                'nombre': 'Tasa de Desempleo',
                'pais': 'Estados Unidos',
                'impacto': 'ALTO',
                'efecto_usd': 'FUERTE_NEGATIVO',
                'efecto_oro': 'POSITIVO',
                'efecto_acciones': 'POSITIVO',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500']
            },
            'NFP': {
                'nombre': 'Nóminas No Agrícolas (NFP)',
                'pais': 'Estados Unidos',
                'impacto': 'MUY_ALTO',
                'efecto_usd': 'FUERTE_POSITIVO',
                'efecto_oro': 'NEGATIVO',
                'efecto_acciones': 'POSITIVO',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'SPX500', 'NAS100', 'USDJPY']
            },
            'PMI': {
                'nombre': 'PMI Manufacturero',
                'pais': 'Estados Unidos',
                'impacto': 'MEDIO',
                'efecto_usd': 'POSITIVO',
                'efecto_oro': 'NEUTRO',
                'efecto_acciones': 'POSITIVO',
                'simbolos_afectados': ['EURUSD', 'SPX500']
            },
            'DECISION_TASAS_FED': {
                'nombre': 'Decisión de Tasas de la FED',
                'pais': 'Estados Unidos',
                'impacto': 'MUY_ALTO',
                'efecto_usd': 'VOLATIL',
                'efecto_oro': 'VOLATIL',
                'efecto_acciones': 'VOLATIL',
                'simbolos_afectados': ['EURUSD', 'GBPUSD', 'XAUUSD', 'SPX500', 'NAS100']
            },
        }

        self.ultimas_alertas = []

        # URL de Apify: se puede sobreescribir por variable de entorno
        self.apify_dataset_url = os.environ.get(
            "APIFY_DATASET_URL",
            "https://api.apify.com/v2/datasets/5tUiuIeUVExG0maAK/items?token=apify_api_W0jlyv72abo93idd27ZibhWBxfkrJk3R0FtA"
        ).strip()

    # =========================
    # MÉTODO PÚBLICO PRINCIPAL
    # =========================
    def obtener_alertas_activas(self):
        """Método público que usa el bot para obtener alertas recientes."""
        return self.verificar_noticias_impacto()

    def verificar_noticias_impacto(self):
        """
        Obtiene datos desde Apify.
        Si la API falla o no hay eventos mapeables, devuelve [].
        """
        try:
            if not self.apify_dataset_url:
                print("⚠️ APIFY_DATASET_URL no configurado. Sin noticias.")
                return []

            eventos = self._obtener_eventos_apify()
            if not eventos:
                return []

            alertas_activas = []

            for evento, datos in eventos.items():
                if evento not in self.eventos_alto_impacto:
                    continue

                # Solo noticias recientes (últimos 45 minutos)
                if self._es_noticia_reciente(datos['timestamp'], ventana_minutos=45):
                    alerta = self._crear_alerta(evento, datos)
                    if alerta:
                        alertas_activas.append(alerta)

            return alertas_activas

        except Exception as e:
            print(f"❌ Error general verificando noticias: {e}")
            return []

    # =========================
    # FUENTE: APIFY DATASET
    # =========================
    def _obtener_eventos_apify(self):
        """
        Obtiene el calendario económico desde el dataset de Apify.
        Se espera una lista de eventos en JSON.
        """
        try:
            resp = requests.get(self.apify_dataset_url, timeout=20)
            if resp.status_code != 200:
                print(f"⚠️ Apify respondió {resp.status_code}: {resp.text[:200]}")
                return None

            data = resp.json()
            if not isinstance(data, list):
                print("⚠️ El dataset de Apify no es una lista.")
                return None

            eventos = {}

            for item in data:
                mapeo = self._mapear_evento_apify(item)
                if not mapeo:
                    continue
                clave_evento, datos = mapeo

                # Guardamos el más reciente por tipo de evento
                if (
                    clave_evento not in eventos or
                    datos["timestamp"] > eventos[clave_evento]["timestamp"]
                ):
                    eventos[clave_evento] = datos

            return eventos or None

        except Exception as e:
            print(f"⚠️ Error en _obtener_eventos_apify: {e}")
            return None

    def _mapear_evento_apify(self, item):
        """
        Mapea un evento del dataset Apify a uno de nuestros eventos_clave internos.

        Formato visto en el test:
            id: 536050
            date: 22/11/2025
            time: 11:00  o "All Day"
            zone: euro zone / united states / etc.
            currency: EUR / USD / ...
            importance: low / medium / high / None
            event: ECB President Lagarde Speaks / Fed Collins Speaks / ...
            actual / forecast / previous: a veces None
            retrieved_at: 2025-11-22T23:35:44.161206
        """
        try:
            # Nombre del evento
            nombre = str(item.get("event") or "").lower()

            # Valores numéricos
            actual = item.get("actual")
            forecast = item.get("forecast")

            # Fecha / hora tipo "22/11/2025" y "16:55" o "All Day"
            date_str = item.get("date") or ""
            time_str = item.get("time") or ""
            retrieved_at = item.get("retrieved_at") or ""

            ts = datetime.utcnow()

            # 1) Intentar parsear date + time Apify (DD/MM/YYYY HH:MM)
            if date_str:
                try:
                    if time_str and time_str.lower() != "all day":
                        # ejemplo: "22/11/2025 16:55"
                        dt_str = f"{date_str} {time_str}"
                        ts = datetime.strptime(dt_str, "%d/%m/%Y %H:%M")
                    else:
                        # Solo fecha, asumimos 00:00
                        ts = datetime.strptime(date_str, "%d/%m/%Y")
                except Exception:
                    # 2) Si falla, usar retrieved_at (ISO)
                    if isinstance(retrieved_at, str) and retrieved_at:
                        try:
                            ts = datetime.fromisoformat(retrieved_at.replace("Z", ""))
                        except Exception:
                            ts = datetime.utcnow()
                    else:
                        ts = datetime.utcnow()
            else:
                # Sin date_str
                if isinstance(retrieved_at, str) and retrieved_at:
                    try:
                        ts = datetime.fromisoformat(retrieved_at.replace("Z", ""))
                    except Exception:
                        ts = datetime.utcnow()
                else:
                    ts = datetime.utcnow()

            # Impacto / importancia del evento (low/medium/high)
            importancia = (item.get("importance") or "").lower() or "desconocido"

            # Si la importancia es 'low' y no es un evento clave, no nos interesa
            # (de todos modos, sólo mapeamos eventos macro fuertes)
            # Determinar resultado comparando actual vs forecast (si se puede)
            resultado = "EN_LINEA"

            def _to_float(v):
                if v is None:
                    return None
                s = str(v).replace("%", "").replace(",", "").replace("K", "").replace("M", "").strip()
                try:
                    return float(s)
                except Exception:
                    return None

            a = _to_float(actual)
            f = _to_float(forecast)

            if a is not None and f is not None:
                if a > f * 1.01:
                    resultado = "MAYOR_ESPERADO"
                elif a < f * 0.99:
                    resultado = "MENOR_ESPERADO"

            datos = {
                "valor_actual": actual,
                "valor_esperado": forecast,
                "resultado": resultado,
                "timestamp": ts,
                "impacto_mercado": importancia
            }

            # 🔎 Detección del tipo de evento por el texto
            # CPI / IPC / inflación
            if "cpi" in nombre or "consumer price" in nombre or "inflation" in nombre or "ipc" in nombre:
                return "IPC_MENSUAL", datos

            # Unemployment
            if "unemployment" in nombre or "jobless" in nombre:
                return "TASA_DESEMPLEO", datos

            # NFP
            if "nonfarm" in nombre or "non-farm" in nombre or "payroll" in nombre:
                return "NFP", datos

            # PMI
            if "pmi" in nombre:
                return "PMI", datos

            # Fed / FOMC / rate decision
            if "fed" in nombre or "fomc" in nombre or "interest rate" in nombre or "rate decision" in nombre:
                return "DECISION_TASAS_FED", datos

            # Si no coincide con nada de interés, lo ignoramos
            return None

        except Exception as e:
            print(f"⚠️ Error en _mapear_evento_apify: {e}")
            return None

    # =========================
    # LÓGICA DE ALERTA
    # =========================
    def _es_noticia_reciente(self, timestamp, ventana_minutos=45):
        """Verificar si la noticia es de los últimos X minutos (por defecto 45)."""
        return (datetime.utcnow() - timestamp).total_seconds() <= ventana_minutos * 60

    def _crear_alerta(self, evento, datos):
        """Crear estructura de alerta compatible con telegram_bot."""
        info_evento = self.eventos_alto_impacto[evento]

        # Direcciones probables
        direccion_forex = self._determinar_direccion_forex(info_evento, datos)
        direccion_oro = self._determinar_direccion_oro(info_evento, datos)
        direccion_acciones = self._determinar_direccion_acciones(info_evento, datos)

        alerta = {
            'tipo': 'ALERTA_NOTICIA',
            'evento': evento,
            'nombre': info_evento['nombre'],
            'pais': info_evento['pais'],
            'impacto': info_evento['impacto'],
            'timestamp': datos['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            'datos': {
                'valor_actual': datos['valor_actual'],
                'valor_esperado': datos['valor_esperado'],
                'resultado': datos['resultado'],
                'impacto_mercado': datos['impacto_mercado']
            },
            'efectos_mercado': {
                'forex': direccion_forex,
                'oro': direccion_oro,
                'acciones': direccion_acciones
            },
            'simbolos_afectados': info_evento['simbolos_afectados'],
            'recomendaciones': self._generar_recomendaciones(info_evento, datos)
        }

        self.ultimas_alertas.append(alerta)
        return alerta

    def _determinar_direccion_forex(self, info_evento, datos):
        """Determinar dirección para Forex basado en noticia."""
        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_usd'] == 'FUERTE_POSITIVO':
                return {'USD': 'FUERTE_ALCISTA', 'EUR': 'BAJISTA', 'GBP': 'BAJISTA'}
            if info_evento['efecto_usd'] == 'FUERTE_NEGATIVO':
                return {'USD': 'FUERTE_BAJISTA', 'EUR': 'ALCISTA', 'GBP': 'ALCISTA'}
        elif datos['resultado'] == 'MENOR_ESPERADO':
            if info_evento['efecto_usd'] == 'FUERTE_NEGATIVO':
                return {'USD': 'FUERTE_BAJISTA', 'EUR': 'ALCISTA', 'GBP': 'ALCISTA'}
        return {'USD': 'NEUTRO', 'EUR': 'NEUTRO', 'GBP': 'NEUTRO'}

    def _determinar_direccion_oro(self, info_evento, datos):
        """Determinar dirección para Oro basado en noticia."""
        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_oro'] == 'NEGATIVO':
                return 'BAJISTA'
            if info_evento['efecto_oro'] == 'POSITIVO':
                return 'ALCISTA'
        return 'NEUTRO'

    def _determinar_direccion_acciones(self, info_evento, datos):
        """Determinar dirección para índices/acciones basado en noticia."""
        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_acciones'] == 'NEGATIVO':
                return 'BAJISTA'
            if info_evento['efecto_acciones'] == 'POSITIVO':
                return 'ALCISTA'
        return 'NEUTRO'

    def _generar_recomendaciones(self, info_evento, datos):
        """Texto de recomendaciones basado en la noticia."""
        recomendaciones = []

        if datos['resultado'] == 'MAYOR_ESPERADO':
            if info_evento['efecto_usd'] == 'FUERTE_POSITIVO':
                recomendaciones.extend([
                    "🎯 EURUSD - Posible VENTA",
                    "🎯 GBPUSD - Posible VENTA",
                    "💰 USDJPY - Posible COMPRA"
                ])
            if info_evento['efecto_oro'] == 'NEGATIVO':
                recomendaciones.append("🪙 XAUUSD - Posible VENTA")
            if info_evento['efecto_acciones'] == 'NEGATIVO':
                recomendaciones.extend([
                    "📉 SPX500 - Posible VENTA",
                    "📉 NAS100 - Posible VENTA"
                ])

        elif datos['resultado'] == 'MENOR_ESPERADO':
            if info_evento['efecto_usd'] == 'FUERTE_NEGATIVO':
                recomendaciones.extend([
                    "🎯 EURUSD - Posible COMPRA",
                    "🎯 GBPUSD - Posible COMPRA"
                ])

        return recomendaciones
