# estrategia_dca.py - ACTUALIZADO CON ESTRATEGIA BACKTESTING
import random
from datetime import datetime

class EstrategiaDCA:
    def __init__(self):
        self.operaciones_activas = {}
        self.yahoo = None
        self.analisis_sr = None
        self.indicadores_reales = None
        self.estrategia_final = None

    def _get_estrategia_final(self):
        if self.estrategia_final is None:
            from estrategia_sr_final import EstrategiaSRFinal
            self.estrategia_final = EstrategiaSRFinal()
        return self.estrategia_final

    def _get_indicadores(self):
        if self.indicadores_reales is None:
            from indicadores_reales import IndicadoresReales
            self.indicadores_reales = IndicadoresReales()
        return self.indicadores_reales

    def _get_analisis_sr(self):
        if self.analisis_sr is None:
            from analisis_tecnico import AnalisisTechnicoSR
            self.analisis_sr = AnalisisTechnicoSR()
        return self.analisis_sr

    def generar_señal_avanzada(self, par):
        """Generar señal combinando ambas estrategias"""
        try:
            from config import PARAMETROS_POR_PAR
            params = PARAMETROS_POR_PAR.get(par, PARAMETROS_POR_PAR['EURUSD'])

            # Obtener datos históricos para backtesting strategy
            datos_historicos = self.obtener_datos_historicos_completos(par)

            if not datos_historicos:
                print(f"❌ No hay datos históricos para {par}, usando estrategia básica")
                return self.generar_señal_real(par)

            # 🎯 PRIMERO: Estrategia Backtesting S/R Final
            señal_backtesting = self._get_estrategia_final().detectar_señal_backtesting(datos_historicos)

            if señal_backtesting:
                print(f"🎯 SEÑAL BACKTESTING DETECTADA: {par} {señal_backtesting['direccion']}")

                # Calcular niveles con estrategia backtesting
                niveles = self._get_estrategia_final().calcular_niveles_operacion(señal_backtesting, params)

                return {
                    'par': par,
                    'direccion': señal_backtesting['direccion'],
                    'precio_actual': señal_backtesting['precio_actual'],
                    'tp1': niveles['tp1'],
                    'tp2': niveles['tp2'],
                    'sl': niveles['sl'],
                    'dca_1': niveles['dca_1'],
                    'dca_2': niveles['dca_2'],
                    'rsi': 50,  # Se calculará después
                    'tendencia': 'ALCISTA' if señal_backtesting['direccion'] == 'COMPRA' else 'BAJISTA',
                    'winrate_esperado': params['winrate'],
                    'rentabilidad_esperada': params['rentabilidad'],
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'fuente_datos': 'Yahoo Finance + Backtesting',
                    'leverage': params['leverage'],
                    'confianza': señal_backtesting['confianza'],
                    'estrategia': señal_backtesting['estrategia'],
                    'niveles_sr': {
                        'support': [señal_backtesting['soporte']],
                        'resistance': [señal_backtesting['resistencia']]
                    },
                    'zona_recomendada': señal_backtesting.get('zona_recomendada', 'ZONA CLAVE'),
                    'tipo_estructura': señal_backtesting.get('tipo_estructura', 'DESCONOCIDA')
                }

            # Si no hay señal de backtesting, usar estrategia clásica (fallback)
            return self.generar_señal_real(par)

        except Exception as e:
            print(f"❌ Error en generar_señal_avanzada: {e}")
            return self.generar_señal_real(par)  # Fallback a estrategia original

    def obtener_datos_historicos_completos(self, par, periodo="1d", intervalo="5m"):
        """Obtener datos históricos completos para backtesting"""
        try:
            from yahoo_api import YahooFinanceAPI
            yahoo = YahooFinanceAPI()

            # Obtener datos en formato OHLC
            datos = yahoo.obtener_datos_historicos_ohlc(par, periodo, intervalo)

            if datos and len(datos) > 50:  # Mínimo 50 velas
                return datos
            return None

        except Exception as e:
            print(f"❌ Error obteniendo datos históricos {par}: {e}")
            return None

    # MANTENER TODOS LOS MÉTODOS EXISTENTES...
    def generar_señal_real(self, par):
        """Fallback simple cuando no se pueda usar la estrategia avanzada.
        Por defecto, no genera señal para evitar operaciones de baja calidad.
        """
        return None
