# config_mejorada.py - CONFIGURACIÓN EXPANDIDA CON MEJORAS
import os

# Configuración Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 🎯 PARÁMETROS BACKTESTING MEJORADOS
PARAMETROS_BACKTESTING = {
    'window_sr': 15,
    'umbral_proximidad': 0.0020,
    'ema_rapida': 20,
    'ema_lenta': 15, 
    'stop_loss': 0.0025,
    'take_profit_multiplier': 3.5,
    'risk_por_operacion': 0.025,
    'max_operaciones': 200,
    'min_velas_entre_ops': 3,
    'trailing_stop_activation': 0.0020,
    
    # NUEVOS PARÁMETROS MEJORADOS
    'max_operaciones_simultaneas': 3,
    'pausa_despues_perdidas': 5,
    'ratio_risk_reward_minimo': 2.0,
    'volatilidad_maxima_aceptable': 2.0
}

# PARÁMETROS POR PAR OPTIMIZADOS CON MEJORAS
PARAMETROS_POR_PAR = {
    # FOREX PRINCIPALES
    'EURUSD': {'winrate': 63.4, 'rentabilidad': 210.23, 'leverage': 20, 
               'dca_niveles': [0.005, 0.010], 'tp_niveles': [0.015, 0.025], 
               'sl': 0.012, 'tipo': 'forex', 'sesion_optima': 'LONDRES'},
    
    'USDCAD': {'winrate': 63.2, 'rentabilidad': 168.16, 'leverage': 20, 
               'dca_niveles': [0.006, 0.012], 'tp_niveles': [0.018, 0.030], 
               'sl': 0.015, 'tipo': 'forex', 'sesion_optima': 'NUEVA_YORK'},
    
    'EURCHF': {'winrate': 48.9, 'rentabilidad': 0.61, 'leverage': 15, 
               'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.012, 0.020], 
               'sl': 0.018, 'tipo': 'forex', 'sesion_optima': 'LONDRES'},
    
    'EURAUD': {'winrate': 64.3, 'rentabilidad': 322.94, 'leverage': 20, 
               'dca_niveles': [0.004, 0.008], 'tp_niveles': [0.020, 0.035], 
               'sl': 0.010, 'tipo': 'forex', 'sesion_optima': 'LONDRES'},
    
    # FOREX ADICIONALES
    'GBPUSD': {'winrate': 58.5, 'rentabilidad': 145.30, 'leverage': 20, 
               'dca_niveles': [0.005, 0.010], 'tp_niveles': [0.015, 0.025], 
               'sl': 0.012, 'tipo': 'forex', 'sesion_optima': 'LONDRES'},
    
    'USDJPY': {'winrate': 59.2, 'rentabilidad': 138.75, 'leverage': 20, 
               'dca_niveles': [0.006, 0.012], 'tp_niveles': [0.018, 0.030], 
               'sl': 0.015, 'tipo': 'forex', 'sesion_optima': 'ASIA'},
    
    # MATERIAS PRIMAS
    'XAUUSD': {'winrate': 58.0, 'rentabilidad': 145.0, 'leverage': 10, 
               'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.025, 0.040], 
               'sl': 0.020, 'tipo': 'commodity', 'sesion_optima': 'LONDRES'},
    
    'XAGUSD': {'winrate': 55.0, 'rentabilidad': 120.0, 'leverage': 10, 
               'dca_niveles': [0.010, 0.020], 'tp_niveles': [0.030, 0.050], 
               'sl': 0.025, 'tipo': 'commodity', 'sesion_optima': 'LONDRES'},
    
    'OILUSD': {'winrate': 56.0, 'rentabilidad': 135.0, 'leverage': 10, 
               'dca_niveles': [0.012, 0.024], 'tp_niveles': [0.035, 0.060], 
               'sl': 0.030, 'tipo': 'commodity', 'sesion_optima': 'NUEVA_YORK'},
    
    # ACCIONES/ÍNDICES
    'SPX500': {'winrate': 59.8, 'rentabilidad': 155.0, 'leverage': 5, 
               'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.022, 0.038], 
               'sl': 0.018, 'tipo': 'indice', 'sesion_optima': 'NUEVA_YORK'},
    
    'NAS100': {'winrate': 61.2, 'rentabilidad': 168.0, 'leverage': 5, 
               'dca_niveles': [0.010, 0.020], 'tp_niveles': [0.025, 0.042], 
               'sl': 0.022, 'tipo': 'indice', 'sesion_optima': 'NUEVA_YORK'},
}

# ✅ TODOS LOS PARES ACTIVOS MEJORADOS
TOP_PARES = list(PARAMETROS_POR_PAR.keys())

# 🎯 GESTIÓN DE RIESGO MEJORADA
RISK_MANAGEMENT = {
    'max_drawdown': 0.50,
    'consecutive_loss_limit': 5,
    'capital_inicial': 1000,
    'max_operaciones_dia': 10,
    'ratio_risk_reward_min': 2.0,
    'volatilidad_max_aceptable': 2.0
}

# 🔧 CONFIGURACIÓN APIs GRATUITAS
FREE_APIS_CONFIG = {
    'yahoo': {'enabled': True, 'requests_per_day': 800},
    'twelvedata': {'enabled': True, 'requests_per_day': 800, 'api_key': 'demo'},
    'alphavantage': {'enabled': True, 'requests_per_day': 25, 'api_key': 'demo'},
    'cache_ttl': {
        'precios': 60,      # 1 minuto
        'indicadores': 300, # 5 minutos
        'noticias': 900     # 15 minutos
    }
}

# 🕒 CONFIGURACIÓN SESIONES MERCADO
MARKET_SESSIONS = {
    'ASIA': {'inicio': 0, 'fin': 8, 'activos': ['USDJPY', 'AUDUSD', 'NZDUSD', 'XAUUSD']},
    'LONDRES': {'inicio': 8, 'fin': 16, 'activos': ['EURUSD', 'GBPUSD', 'EURCHF', 'XAGUSD']},
    'NUEVA_YORK': {'inicio': 13, 'fin': 21, 'activos': ['USDCAD', 'USDCHF', 'SPX500', 'NAS100']}
}
