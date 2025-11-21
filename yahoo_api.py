# AGREGAR ESTE MÉTODO A yahoo_api.py (al final de la clase YahooFinanceAPI)
def obtener_datos_historicos_ohlc(self, simbolo, periodo="1d", intervalo="5m"):
    """Obtener datos OHLC históricos para backtesting"""
    try:
        symbol_mapping = {
            # FOREX
            "EURUSD": "EURUSD=X", "USDCAD": "CAD=X", "EURCHF": "EURCHF=X", "EURAUD": "EURAUD=X",
            "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X", "AUDUSD": "AUDUSD=X", "NZDUSD": "NZDUSD=X",
            "USDCHF": "CHF=X", "GBPJPY": "GBPJPY=X",
            
            # MATERIAS PRIMAS
            "XAUUSD": "GC=F", "XAGUSD": "SI=F", "OILUSD": "CL=F", "XPTUSD": "PL=F",
            "XPDUSD": "PA=F", "NGASUSD": "NG=F", "COPPER": "HG=F",
            
            # ACCIONES/ÍNDICES
            "SPX500": "^GSPC", "NAS100": "^IXIC", "DJI30": "^DJI", 
            "GER40": "^GDAXI", "UK100": "^FTSE", "JPN225": "^N225"
        }
        
        yahoo_symbol = symbol_mapping.get(simbolo)
        if not yahoo_symbol:
            print(f"❌ Símbolo no encontrado para OHLC: {simbolo}")
            return None
            
        url = f"{self.base_url}/{yahoo_symbol}"
        params = {
            "range": periodo,
            "interval": intervalo
        }
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                quotes = result['indicators']['quote'][0]
                
                # Validar que hay datos suficientes
                if not quotes['open'] or len(quotes['open']) < 10:
                    return None
                
                # Crear lista de datos OHLC
                datos = []
                for i in range(len(result['timestamp'])):
                    if (quotes['open'][i] is not None and 
                        quotes['high'][i] is not None and 
                        quotes['low'][i] is not None and 
                        quotes['close'][i] is not None):
                        
                        datos.append({
                            'timestamp': result['timestamp'][i],
                            'open': quotes['open'][i],
                            'high': quotes['high'][i], 
                            'low': quotes['low'][i],
                            'close': quotes['close'][i],
                            'volume': quotes['volume'][i] if i < len(quotes.get('volume', [])) else 0
                        })
                
                print(f"✅ OHLC {simbolo}: {len(datos)} velas obtenidas")
                return datos if len(datos) > 20 else None  # Mínimo 20 velas útiles
                
        print(f"❌ Error en respuesta OHLC para {simbolo}")
        return None
        
    except Exception as e:
        print(f"❌ Error datos OHLC {simbolo}: {e}")
        return None

# AGREGAR TAMBIÉN ESTE MÉTODO PARA COMPATIBILIDAD
def obtener_datos_tecnicos_completos(self, simbolo):
    """Obtener datos técnicos completos incluyendo OHLC"""
    try:
        # Primero obtener precio actual
        precio_actual = self.obtener_precio_real(simbolo)
        
        if not precio_actual:
            return None
        
        # Obtener datos OHLC para análisis
        datos_ohlc = self.obtener_datos_historicos_ohlc(simbolo, "1d", "15m")
        
        if datos_ohlc and len(datos_ohlc) > 20:
            # Extraer precios de cierre para RSI
            closes = [d['close'] for d in datos_ohlc if d['close'] is not None]
            
            # Calcular RSI básico
            if len(closes) >= 14:
                rsi = self._calcular_rsi_simple(closes)
            else:
                rsi = 50
                
            # Determinar tendencia básica
            if len(closes) >= 5:
                ultimos_5 = closes[-5:]
                if ultimos_5[-1] > ultimos_5[0]:
                    tendencia = "ALCISTA"
                elif ultimos_5[-1] < ultimos_5[0]:
                    tendencia = "BAJISTA"
                else:
                    tendencia = "LATERAL"
            else:
                tendencia = "LATERAL"
                
            return {
                'precio_actual': precio_actual,
                'rsi': rsi,
                'tendencia': tendencia,
                'volatilidad': 0.5,  # Valor por defecto
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'fuente': 'Yahoo Finance OHLC',
                'datos_ohlc': datos_ohlc  # Incluir datos completos para backtesting
            }
        else:
            # Fallback al método original
            return self.obtener_datos_tecnicos(simbolo)
            
    except Exception as e:
        print(f"❌ Error datos técnicos completos {simbolo}: {e}")
        return self.obtener_datos_tecnicos(simbolo)

def _calcular_rsi_simple(self, closes, periodo=14):
    """Calcular RSI simple para datos OHLC"""
    if len(closes) < periodo + 1:
        return 50
        
    gains = []
    losses = []
    
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
    
    if len(gains) < periodo:
        return 50
        
    avg_gain = sum(gains[-periodo:]) / periodo
    avg_loss = sum(losses[-periodo:]) / periodo
    
    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)
