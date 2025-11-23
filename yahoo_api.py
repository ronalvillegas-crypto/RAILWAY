import requests
from datetime import datetime

class YahooFinanceAPI:
    """
    Cliente sencillo para obtener precios y datos OHLC desde Yahoo Finance
    usando el endpoint público de charts.
    """

    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        # Mapeo interno de símbolos a tickers de Yahoo
        self.symbol_mapping = {
            # FOREX
            "EURUSD": "EURUSD=X", "USDCAD": "CAD=X", "EURCHF": "EURCHF=X", "EURAUD": "EURAUD=X",
            "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "NZDUSD": "NZDUSD=X",
            "USDCHF": "CHF=X", "GBPJPY": "GBPJPY=X",

            # MATERIAS PRIMAS
            "XAUUSD": "GC=F", "XAGUSD": "SI=F", "OILUSD": "CL=F", "XPTUSD": "PL=F",
            "XPDUSD": "PA=F", "NGASUSD": "NG=F", "COPPER": "HG=F",

            # ACCIONES/ÍNDICES
            "SPX500": "^GSPC", "NAS100": "^IXIC", "DJI30": "^DJI",
            "GER40": "^GDAXI", "UK100": "^FTSE", "JPN225": "^N225",
        }

    # =============================
    # MÉTODOS PÚBLICOS PRINCIPALES
    # =============================

    def obtener_precio_real(self, simbolo: str):
        """
        Devuelve el último precio de cierre disponible para el símbolo dado.
        Si algo falla, retorna None.
        """
        try:
            yahoo_symbol = self._map_symbol(simbolo)
            if not yahoo_symbol:
                print(f"❌ Símbolo no mapeado en YahooFinanceAPI.obtener_precio_real: {simbolo}")
                return None

            url = f"{self.base_url}/{yahoo_symbol}"
            params = {
                "range": "1d",
                "interval": "1m",
            }
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            }
            resp = requests.get(url, params=params, headers=headers, timeout=15)

            if resp.status_code != 200:
                print(f"⚠️ Error HTTP {resp.status_code} en obtener_precio_real({simbolo})")
                return None

            data = resp.json()
            result = (
                data.get("chart", {})
                    .get("result", [None])[0]
            )
            if not result:
                print(f"⚠️ Respuesta sin 'result' para {simbolo}")
                return None

            closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            if not closes:
                print(f"⚠️ Sin datos de cierre en obtener_precio_real({simbolo})")
                return None

            # Tomar el último cierre no None
            for price in reversed(closes):
                if price is not None:
                    return float(price)

            print(f"⚠️ Todos los cierres son None para {simbolo}")
            return None
        except Exception as e:
            print(f"❌ Error obteniendo precio real {simbolo}: {e}")
            return None

    def obtener_datos_historicos_ohlc(self, simbolo, periodo: str = "1d", intervalo: str = "5m"):
        """
        Obtener datos OHLC históricos para backtesting desde Yahoo Finance.

        Retorna una lista de dicts:
        [
            { 'timestamp': ts, 'open': o, 'high': h, 'low': l, 'close': c, 'volume': v },
            ...
        ]
        o None si falla.
        """
        try:
            yahoo_symbol = self._map_symbol(simbolo)
            if not yahoo_symbol:
                print(f"❌ Símbolo no encontrado para OHLC: {simbolo}")
                return None

            url = f"{self.base_url}/{yahoo_symbol}"
            params = {
                "range": periodo,
                "interval": intervalo,
            }
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            }
            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code} en OHLC para {simbolo}")
                return None

            data = response.json()
            chart = data.get("chart", {})
            results = chart.get("result", [])
            if not results:
                print(f"⚠️ Sin resultados OHLC para {simbolo}")
                return None

            result = results[0]
            indicators = result.get("indicators", {})
            quote = indicators.get("quote", [{}])[0]

            opens = quote.get("open", [])
            highs = quote.get("high", [])
            lows = quote.get("low", [])
            closes = quote.get("close", [])
            volumes = quote.get("volume", [])

            if not opens or len(opens) < 10:
                return None

            timestamps = result.get("timestamp", [])
            datos = []
            for i, ts in enumerate(timestamps):
                # Asegurar que existan los 4 precios
                try:
                    o = opens[i]
                    h = highs[i]
                    l = lows[i]
                    c = closes[i]
                except IndexError:
                    continue

                if o is None or h is None or l is None or c is None:
                    continue

                v = volumes[i] if i < len(volumes) else 0
                datos.append({
                    "timestamp": ts,
                    "open": o,
                    "high": h,
                    "low": l,
                    "close": c,
                    "volume": v,
                })

            if len(datos) <= 20:
                print(f"⚠️ Muy pocas velas OHLC ({len(datos)}) para {simbolo}")
                return None

            print(f"✅ OHLC {simbolo}: {len(datos)} velas obtenidas")
            return datos
        except Exception as e:
            print(f"❌ Error datos OHLC {simbolo}: {e}")
            return None

    def obtener_datos_tecnicos_completos(self, simbolo):
        """
        Devuelve un dict con:
            - precio_actual
            - rsi
            - tendencia
            - volatilidad (placeholder)
            - timestamp
            - fuente
            - datos_ohlc (lista completa)
        Usado por estrategias avanzadas para tener datos reales.
        """
        try:
            datos_ohlc = self.obtener_datos_historicos_ohlc(simbolo, periodo="5d", intervalo="30m")
            if not datos_ohlc:
                return None

            # Último cierre como precio actual
            cierres = [d["close"] for d in datos_ohlc if d.get("close") is not None]
            if not cierres:
                return None

            precio_actual = float(cierres[-1])

            # Calcular RSI
            if len(cierres) >= 14:
                rsi = self._calcular_rsi_simple(cierres)
            else:
                rsi = 50.0

            # Tendencia básica en los últimos 5 cierres
            if len(cierres) >= 5:
                ult5 = cierres[-5:]
                if ult5[-1] > ult5[0]:
                    tendencia = "ALCISTA"
                elif ult5[-1] < ult5[0]:
                    tendencia = "BAJISTA"
                else:
                    tendencia = "LATERAL"
            else:
                tendencia = "LATERAL"

            return {
                "precio_actual": precio_actual,
                "rsi": rsi,
                "tendencia": tendencia,
                "volatilidad": 0.5,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "fuente": "Yahoo Finance OHLC",
                "datos_ohlc": datos_ohlc,
            }
        except Exception as e:
            print(f"❌ Error obteniendo datos técnicos de {simbolo}: {e}")
            return None

    # =============================
    # MÉTODOS AUXILIARES INTERNOS
    # =============================

    def _map_symbol(self, simbolo: str):
        """
        Convierte el símbolo interno (ej. EURUSD, XAUUSD)
        al ticker real que entiende Yahoo Finance.
        """
        return self.symbol_mapping.get(simbolo, None)

    def _calcular_rsi_simple(self, cierres, periodo: int = 14):
        """
        Cálculo simple de RSI usando ganancias/pérdidas promedio.
        """
        if len(cierres) < periodo + 1:
            return 50.0

        gains = []
        losses = []
        for i in range(1, len(cierres)):
            cambio = cierres[i] - cierres[i - 1]
            if cambio > 0:
                gains.append(cambio)
                losses.append(0.0)
            elif cambio < 0:
                gains.append(0.0)
                losses.append(-cambio)
            else:
                gains.append(0.0)
                losses.append(0.0)

        if len(gains) < periodo:
            return 50.0

        avg_gain = sum(gains[-periodo:]) / periodo
        avg_loss = sum(losses[-periodo:]) / periodo

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
