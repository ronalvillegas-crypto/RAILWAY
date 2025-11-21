# config.py - CONFIGURACIÓN EXPANDIDA
import os

# Configuración Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 🎯 PARÁMETROS BACKTESTING S/R FINAL PERFECTA
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
    'trailing_stop_activation': 0.0020
}

# PARÁMETROS POR PAR OPTIMIZADOS
PARAMETROS_POR_PAR = {
    # FOREX PRINCIPALES (EXISTENTES + NUEVOS)
    'EURUSD': {'winrate': 63.4, 'rentabilidad': 210.23, 'leverage': 20, 'dca_niveles': [0.005, 0.010], 'tp_niveles': [0.015, 0.025], 'sl': 0.012, 'tipo': 'forex'},
    'USDCAD': {'winrate': 63.2, 'rentabilidad': 168.16, 'leverage': 20, 'dca_niveles': [0.006, 0.012], 'tp_niveles': [0.018, 0.030], 'sl': 0.015, 'tipo': 'forex'},
    'EURCHF': {'winrate': 48.9, 'rentabilidad': 0.61, 'leverage': 15, 'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.012, 0.020], 'sl': 0.018, 'tipo': 'forex'},
    'EURAUD': {'winrate': 64.3, 'rentabilidad': 322.94, 'leverage': 20, 'dca_niveles': [0.004, 0.008], 'tp_niveles': [0.020, 0.035], 'sl': 0.010, 'tipo': 'forex'},
    
    # FOREX ADICIONALES (NUEVOS)
    'GBPUSD': {'winrate': 58.5, 'rentabilidad': 145.30, 'leverage': 20, 'dca_niveles': [0.005, 0.010], 'tp_niveles': [0.015, 0.025], 'sl': 0.012, 'tipo': 'forex'},
    'USDJPY': {'winrate': 59.2, 'rentabilidad': 138.75, 'leverage': 20, 'dca_niveles': [0.006, 0.012], 'tp_niveles': [0.018, 0.030], 'sl': 0.015, 'tipo': 'forex'},
    'AUDUSD': {'winrate': 56.8, 'rentabilidad': 125.40, 'leverage': 20, 'dca_niveles': [0.007, 0.014], 'tp_niveles': [0.020, 0.035], 'sl': 0.016, 'tipo': 'forex'},
    'NZDUSD': {'winrate': 55.3, 'rentabilidad': 118.90, 'leverage': 20, 'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.022, 0.038], 'sl': 0.018, 'tipo': 'forex'},
    'USDCHF': {'winrate': 57.1, 'rentabilidad': 132.60, 'leverage': 20, 'dca_niveles': [0.005, 0.010], 'tp_niveles': [0.016, 0.028], 'sl': 0.013, 'tipo': 'forex'},
    'GBPJPY': {'winrate': 56.2, 'rentabilidad': 128.40, 'leverage': 15, 'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.022, 0.038], 'sl': 0.018, 'tipo': 'forex'},
    
    # MATERIAS PRIMAS (EXISTENTES + NUEVAS)
    'XAUUSD': {'winrate': 58.0, 'rentabilidad': 145.0, 'leverage': 10, 'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.025, 0.040], 'sl': 0.020, 'tipo': 'commodity'},
    'XAGUSD': {'winrate': 55.0, 'rentabilidad': 120.0, 'leverage': 10, 'dca_niveles': [0.010, 0.020], 'tp_niveles': [0.030, 0.050], 'sl': 0.025, 'tipo': 'commodity'},
    'OILUSD': {'winrate': 56.0, 'rentabilidad': 135.0, 'leverage': 10, 'dca_niveles': [0.012, 0.024], 'tp_niveles': [0.035, 0.060], 'sl': 0.030, 'tipo': 'commodity'},
    'XPTUSD': {'winrate': 52.0, 'rentabilidad': 95.0, 'leverage': 8, 'dca_niveles': [0.015, 0.030], 'tp_niveles': [0.040, 0.070], 'sl': 0.035, 'tipo': 'commodity'},
    'XPDUSD': {'winrate': 51.5, 'rentabilidad': 88.0, 'leverage': 8, 'dca_niveles': [0.016, 0.032], 'tp_niveles': [0.042, 0.075], 'sl': 0.038, 'tipo': 'commodity'},
    'NGASUSD': {'winrate': 53.0, 'rentabilidad': 105.0, 'leverage': 8, 'dca_niveles': [0.020, 0.040], 'tp_niveles': [0.050, 0.085], 'sl': 0.045, 'tipo': 'commodity'},
    'COPPER': {'winrate': 54.2, 'rentabilidad': 98.0, 'leverage': 8, 'dca_niveles': [0.015, 0.030], 'tp_niveles': [0.038, 0.065], 'sl': 0.035, 'tipo': 'commodity'},
    
    # ACCIONES (ÍNDICES PRINCIPALES)
    'SPX500': {'winrate': 59.8, 'rentabilidad': 155.0, 'leverage': 5, 'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.022, 0.038], 'sl': 0.018, 'tipo': 'indice'},
    'NAS100': {'winrate': 61.2, 'rentabilidad': 168.0, 'leverage': 5, 'dca_niveles': [0.010, 0.020], 'tp_niveles': [0.025, 0.042], 'sl': 0.022, 'tipo': 'indice'},
    'DJI30': {'winrate': 57.5, 'rentabilidad': 142.0, 'leverage': 5, 'dca_niveles': [0.007, 0.014], 'tp_niveles': [0.020, 0.035], 'sl': 0.016, 'tipo': 'indice'},
    'GER40': {'winrate': 56.3, 'rentabilidad': 135.0, 'leverage': 5, 'dca_niveles': [0.009, 0.018], 'tp_niveles': [0.024, 0.040], 'sl': 0.020, 'tipo': 'indice'},
    'UK100': {'winrate': 55.8, 'rentabilidad': 128.0, 'leverage': 5, 'dca_niveles': [0.008, 0.016], 'tp_niveles': [0.022, 0.038], 'sl': 0.019, 'tipo': 'indice'},
    'JPN225': {'winrate': 54.7, 'rentabilidad': 118.0, 'leverage': 5, 'dca_niveles': [0.010, 0.020], 'tp_niveles': [0.026, 0.044], 'sl': 0.022, 'tipo': 'indice'},
}

# ✅ TODOS LOS PARES ACTIVOS
TOP_PARES = list(PARAMETROS_POR_PAR.keys())

# 🎯 MANTENER COMPATIBILIDAD
TOP_5_PARES = ['EURUSD', 'USDCAD', 'XAUUSD', 'SPX500', 'GBPUSD']

# 🎯 GESTIÓN DE RIESGO OPTIMIZADA
RISK_MANAGEMENT = {
    'max_drawdown': 0.50,
    'consecutive_loss_limit': 5,
    'capital_inicial': 1000
}
